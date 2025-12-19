import pytest
from pathlib import Path
import pyvista as pv
import numpy as np

from g_util.mesh.mesh import Mesh, TriangleMesh, TetraMesh, PointMesh, LineMesh


@pytest.fixture
def sample_tetra_vtk(tmp_path) -> Path:
    """Creates a simple tetrahedron VTK file for testing."""
    path = tmp_path / "test_tetra.vtk"
    # Create a simple tetrahedron: 4 points, 1 cell
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float)
    cells = np.array([4, 0, 1, 2, 3])
    cell_types = np.array([pv.CellType.TETRA])
    grid = pv.UnstructuredGrid(cells, cell_types, points)
    grid.save(str(path))
    return path


class TestMeshSystem:

    def test_io_operations(self, sample_tetra_vtk, tmp_path):
        """Tests reading and writing of mesh files."""
        # Read
        mesh = Mesh.read(sample_tetra_vtk)
        assert isinstance(mesh.data, pv.DataSet)
        assert mesh.data.n_cells > 0

        # Write
        out_path = tmp_path / "output.vtk"
        saved_path = mesh.write(out_path)
        assert out_path.exists()
        assert saved_path == out_path

    def test_casting_hierarchy(self, sample_tetra_vtk):
        """Tests the conversion between different mesh types (Point, Triangle, Tetra)."""
        base_mesh = Mesh.read(sample_tetra_vtk)

        # Test conversion to Triangle (Surface extraction)
        surf = base_mesh.as_triangle()
        assert isinstance(surf, TriangleMesh)
        assert surf.data.n_cells >= 4  # A tetra has 4 triangular faces

        # Test conversion to Tetra
        vol = base_mesh.as_tetra()
        assert isinstance(vol, TetraMesh)

        # Test conversion to Points
        pts = base_mesh.as_point()
        assert isinstance(pts, PointMesh)
        assert pts.data.n_points == 4

    def test_surface_remeshing_mmgs(self, sample_tetra_vtk):
        """
        Tests the MMGS remeshing logic.
        Note: Requires mmgs to be installed in the environment.
        """
        m = Mesh.read(sample_tetra_vtk)
        surf = m.as_triangle()

        # Perform remeshing with a specific edge length
        target_edgel = 0.1
        remeshed_surf = surf.remesh_mmgs(edgel=target_edgel, hgrad=1.2)

        assert isinstance(remeshed_surf, TriangleMesh)
        assert remeshed_surf.data.n_cells > 0
        # Ensure it's still a surface/polydata
        assert isinstance(remeshed_surf.data, pv.PolyData)

    def test_volume_remeshing_mmg3d(self, sample_tetra_vtk):
        """
        Tests the MMG3D remeshing logic.
        Note: Requires mmg3d to be installed in the environment.
        """
        m = TetraMesh.read(sample_tetra_vtk)

        # Perform volume remeshing
        # Using larger bounds to ensure the CLI is triggered correctly
        vol = m.remesh_mmg3d(hmin=0.05, hmax=0.2, nr=False)

        assert isinstance(vol, TetraMesh)
        assert vol.data.n_cells > 0
        # Ensure the output is an UnstructuredGrid (standard for volumes)
        assert isinstance(vol.data, pv.UnstructuredGrid)

    def test_invalid_mesh_type_filter(self):
        """Tests that _only_cells raises error when no valid cells exist."""
        from g_util.mesh.mesh import _only_cells
        import meshio

        # Create a mesh with only lines
        empty_mi = meshio.Mesh(
            points=[[0, 0, 0], [1, 1, 1]], cells=[("line", [[0, 1]])]
        )

        # Try to extract triangles from a line-only mesh
        with pytest.raises(ValueError, match="Mesh has no allowed cells"):
            _only_cells(empty_mi, {"triangle"})

    def test_mmg_module_resolver(self):
        """Tests the internal module name mapping."""
        from g_util.mesh.mesh import _mmg_module_name

        assert _mmg_module_name("surface") == "mmgs"
        assert _mmg_module_name("tetra") == "mmg3d"
        assert _mmg_module_name("mmgs") == "mmgs"

        with pytest.raises(ValueError):
            _mmg_module_name("invalid_type")

    def test_as_point_synthesizes_vertex_cells(self, sample_tetra_vtk):
        """Casting a tetra mesh to points should synthesize vertex cells (1 per point)."""
        base_mesh = Mesh.read(sample_tetra_vtk)
        pts = base_mesh.as_point()

        mi = pv.to_meshio(pts.data)
        assert any(cb.type == "vertex" for cb in mi.cells)

        vblocks = [cb for cb in mi.cells if cb.type == "vertex"]
        assert len(vblocks) == 1
        assert vblocks[0].data.shape == (pts.data.n_points, 1)

    def test_triangle_cast_returns_clean_triangulated_polydata(self, sample_tetra_vtk):
        """Triangle casting should produce a clean triangulated PolyData surface."""
        base_mesh = Mesh.read(sample_tetra_vtk)
        surf = base_mesh.as_triangle()

        assert isinstance(surf.data, pv.PolyData)
        assert surf.data.is_all_triangles
        assert surf.data.n_points > 0
        assert surf.data.n_cells >= 4

    def test_as_tetra_rejects_non_tetra_cells(self):
        """Casting to tetra should fail fast when no tetra cells exist."""
        poly = pv.Plane(i_resolution=1, j_resolution=1).triangulate()
        m = Mesh(poly)

        with pytest.raises(ValueError, match="Mesh has no allowed cells"):
            _ = m.as_tetra()

    def test_as_triangle_preserves_point_data(self, sample_tetra_vtk):
        """Point data should survive a cast to TriangleMesh."""
        m0 = Mesh.read(sample_tetra_vtk)
        m0.data.point_data["pid"] = np.arange(m0.data.n_points, dtype=int)

        surf = m0.as_triangle()
        assert isinstance(surf.data, pv.PolyData)
        assert "pid" in surf.data.point_data
        assert surf.data.point_data["pid"].shape[0] == surf.data.n_points

    def test_trianglemesh_from_polydata_is_idempotent(self):
        """Casting an already-triangulated PolyData surface should remain a PolyData and triangles-only."""
        poly = pv.Sphere(theta_resolution=12, phi_resolution=12).triangulate().clean()
        surf = Mesh(poly).as_triangle()

        assert isinstance(surf.data, pv.PolyData)
        assert surf.data.is_all_triangles
        assert surf.data.n_points == poly.n_points
        assert surf.data.n_cells == poly.n_cells

    def test_tetra_cast_preserves_cell_count_for_tetra_input(self, sample_tetra_vtk):
        """Casting a tetra mesh to TetraMesh should keep tetra-only connectivity (same cell count here)."""
        base = Mesh.read(sample_tetra_vtk)
        vol = base.as_tetra()

        assert isinstance(vol, TetraMesh)
        assert vol.data.n_cells == 1

        mi = pv.to_meshio(vol.data)
        assert {cb.type for cb in mi.cells} == {"tetra"}
