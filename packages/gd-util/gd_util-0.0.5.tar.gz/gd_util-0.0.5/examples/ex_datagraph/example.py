# example.py
"""
Example usage of DataGraph for progressively more complex simulated objects.

This file illustrates:
- a minimal tetrahedral cube
- a topology + surface with a mapping
- how the same structure scales to complex assemblies (e.g. heart-like objects)

Nothing here is domain-specific: only conventions.
"""

from pathlib import Path

import meshio

from gd_util.datacontainer.container import Container
from gd_util.datagraph.mesh_datagraph import (
    AssetRef,
    DataGraphBuilder,
)
from gd_util.utils.make_bar import generate_bar


# -----------------------------------------------------------------------------
# Helpers (purely illustrative)
# -----------------------------------------------------------------------------


def load_mesh(path: Path) -> meshio.Mesh:
    return meshio.read(path)


# -----------------------------------------------------------------------------
# Example 1: minimal tetrahedral cube
# -----------------------------------------------------------------------------


def example_cube_tetra(tmp_dir: Path) -> None:
    """
    Single tetrahedral object, no mappings.
    """
    ct = Container(tmp_dir / "cube", clean=True)

    m = generate_bar(5e-3, out_dir=ct, nr=False)
    m["tetra"].write(ct / "meshes/cube_tet.vtk")

    g = (
        DataGraphBuilder.new(ct)
        .node("cube", kind="tetra", name="CubeTetra")
        .asset_key("cube", "mesh", "cube_tet", role="mesh")
        .child_of("cube", "root")
        .build()
    )

    g.save()
    cube_mesh = g.mesh("cube")
    print("Cube tetra:", cube_mesh)


# -----------------------------------------------------------------------------
# Example 2: volume + surface with mapping
# -----------------------------------------------------------------------------


def example_volume_surface_mapping(tmp_dir: Path) -> None:
    """
    A volumetric mesh mapped to a surface mesh.
    """
    ct = Container(tmp_dir / "bar", clean=True)

    # Files assumed to exist / be generated elsewhere
    ct / "meshes/bar_tet.vtu"  # registers key: bar_tet
    ct / "meshes/bar_surface.vtu"  # registers key: bar_surface
    ct / "mappings/tet_to_surface.json"  # registers key: tet_to_surface

    g = (
        DataGraphBuilder.new(ct)
        .node("bar_vol", kind="tetra", name="BarVolume")
        .asset_key("bar_vol", "mesh", "bar_tet", role="mesh")
        .child_of("bar_vol", "root")
        .node("bar_surf", kind="triangle", name="BarSurface")
        .asset_key("bar_surf", "mesh", "bar_surface", role="mesh")
        .child_of("bar_surf", "bar_vol")
        .mapping(
            "bar_vol",
            "bar_surf",
            method="surface_extraction",
            data=AssetRef.key("tet_to_surface", role="mapping"),
        )
        .build()
    )

    g.save()

    vol = g.mesh("bar_vol")
    surf = g.mesh("bar_surf")
    print("Volume cells:", len(vol.cells))
    print("Surface cells:", len(surf.cells))


# -----------------------------------------------------------------------------
# Example 3: heart-like composite object (conceptual)
# -----------------------------------------------------------------------------


def example_heart_like(tmp_dir: Path) -> None:
    """
    Illustrative heart-like object composed of multiple subsystems.

    This mirrors how a real heart model would scale:
    - independent topologies
    - shared DOFs
    - multiple mappings
    """
    ct = Container(tmp_dir / "heart", clean=True)

    # Pretend these already exist
    ct / "meshes/myocardium_tet.vtu"
    ct / "meshes/epi_tri.vtu"
    ct / "meshes/endo_tri.vtu"
    ct / "mappings/myo_to_epi.json"
    ct / "mappings/myo_to_endo.json"

    g = DataGraphBuilder.new(ct)

    g = (
        g.node("myocardium", kind="tetra", name="Myocardium")
        .asset_key("myocardium", "mesh", "myocardium_tet", role="mesh")
        .child_of("myocardium", "root")
        .node("epicardium", kind="triangle", name="Epicardium")
        .asset_key("epicardium", "mesh", "epi_tri", role="mesh")
        .child_of("epicardium", "myocardium")
        .node("endocardium", kind="triangle", name="Endocardium")
        .asset_key("endocardium", "mesh", "endo_tri", role="mesh")
        .child_of("endocardium", "myocardium")
        .mapping(
            "myocardium",
            "epicardium",
            method="surface_extraction",
            data=AssetRef.key("myo_to_epi", role="mapping"),
        )
        .mapping(
            "myocardium",
            "endocardium",
            method="surface_extraction",
            data=AssetRef.key("myo_to_endo", role="mapping"),
        )
        .build()
    )

    g.save()

    # Runtime usage
    myo = g.mesh("myocardium")
    epi = g.mesh("epicardium")
    endo = g.mesh("endocardium")

    print("Heart model:")
    print("  myocardium:", myo)
    print("  epicardium:", epi)
    print("  endocardium:", endo)


# -----------------------------------------------------------------------------
# Entry point (for manual testing)
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        example_cube_tetra(tmp)
        # example_volume_surface_mapping(tmp)
        # example_heart_like(tmp)
