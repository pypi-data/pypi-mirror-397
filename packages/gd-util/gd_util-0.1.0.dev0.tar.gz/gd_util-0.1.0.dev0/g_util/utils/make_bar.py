from __future__ import annotations

import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import meshio
import pyvista as pv
from g_util.datacontainer.container import PathLike
from g_util.datagraph.mesh_datagraph import DataGraph, DataGraphAdd
from g_util.mesh.mesh import TetraMesh, TriangleMesh
import vtk
from vtk.util.numpy_support import numpy_to_vtk

from g_util.utils import fPath, dump_json
from g_util.datacontainer import Container


def _vtk_cube_polydata(bounds) -> pv.PolyData:
    x0, x1, y0, y1, z0, z1 = map(float, bounds)
    src = vtk.vtkCubeSource()
    src.SetBounds(x0, x1, y0, y1, z0, z1)
    src.Update()
    return pv.wrap(src.GetOutput()).triangulate()


def _vtk_seed_tets_from_bounds(bounds, pitch: float) -> pv.UnstructuredGrid:
    x0, x1, y0, y1, z0, z1 = map(float, bounds)

    xs = np.arange(x0, x1 + 0.5 * pitch, pitch)
    ys = np.arange(y0, y1 + 0.5 * pitch, pitch)
    zs = np.arange(z0, z1 + 0.5 * pitch, pitch)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    pts = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()]).astype(np.float64)

    vtk_pts = vtk.vtkPoints()
    vtk_pts.SetData(numpy_to_vtk(pts, deep=True))

    poly = vtk.vtkPolyData()
    poly.SetPoints(vtk_pts)

    del3d = vtk.vtkDelaunay3D()
    del3d.SetInputData(poly)
    del3d.Update()

    tet_only = vtk.vtkDataSetTriangleFilter()
    tet_only.SetInputConnection(del3d.GetOutputPort())
    tet_only.Update()

    return pv.wrap(tet_only.GetOutput())


def _run_mmg3d(
    input_mesh: Path,
    output_mesh: Path,
    *,
    hmin: float,
    hmax: float,
    hgrad: float = 1.0,
    nr: bool = True,
):
    cmd = [
        sys.executable,
        "-m",
        "mmg3d",
        str(input_mesh),
        str(output_mesh),
        "-hmin",
        str(hmin),
        "-hmax",
        str(hmax),
        "-hgrad",
        str(hgrad),
    ]
    if nr:
        cmd.append("-nr")
    subprocess.run(
        cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )


def _run_mmgs(
    input_mesh: Path,
    output_mesh: Path,
    *,
    hmin: float,
    hmax: float,
    hgrad: float = 1.0,
    nr: bool = True,
):
    cmd = [
        sys.executable,
        "-m",
        "mmgs",
        str(input_mesh),
        str(output_mesh),
        "-hmin",
        str(hmin),
        "-hmax",
        str(hmax),
        "-hgrad",
        str(hgrad),
    ]
    if nr:
        cmd.append("-nr")
    subprocess.run(
        cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )


def _remesh_surface_mmgs(
    poly: pv.PolyData, *, edgel: float, hgrad: float = 1.0, nr: bool = True
) -> pv.PolyData:
    poly = poly.triangulate().clean()
    m_in = pv.to_meshio(poly)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        in_mesh = td / "surf_in.mesh"
        out_mesh = td / "surf_out.mesh"

        meshio.write(in_mesh, m_in, file_format="medit")
        _run_mmgs(in_mesh, out_mesh, hmin=edgel, hmax=edgel, hgrad=hgrad, nr=nr)

        out = pv.from_meshio(meshio.read(out_mesh))
        # mmgs triangles may come back as UnstructuredGrid; normalize to PolyData
        if isinstance(out, pv.UnstructuredGrid):
            out = out.extract_surface()
        return out.triangulate().clean()


def generate_bar(
    edgel: float,
    out_dir: PathLike,
    *,
    bounds=(0, 1e-2, 0, 1e-2, 0, 5e-2),
    hgrad=1.0,
    nr=False,
):
    out_dir = Path(out_dir)

    _ = _vtk_cube_polydata(bounds)  # keep if you still want it around (not used below)

    seed_grid = _vtk_seed_tets_from_bounds(bounds, pitch=edgel)
    seed_meshio = pv.to_meshio(seed_grid.cast_to_unstructured_grid())

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        in_mesh = td / "seed.mesh"
        out_mesh = td / "bar.mesh"

        meshio.write(in_mesh, seed_meshio, file_format="medit")
        _run_mmg3d(in_mesh, out_mesh, hmin=edgel, hmax=edgel, hgrad=hgrad, nr=nr)

        tetra = pv.from_meshio(meshio.read(out_mesh))

    # outer surface of the tetra mesh
    surf = tetra.extract_surface().triangulate().clean()
    surf["z"] = surf.points[:, 1]

    zmin = float(surf.points[:, 1].min())
    zmax = float(surf.points[:, 1].max())

    eps = 1e-12
    top = surf.threshold((zmax - eps, zmax + eps), scalars="z")
    bottom = surf.threshold((zmin - eps, zmin + eps), scalars="z")

    # remesh the full outer surface in 3D (surface remesher = mmgs)
    surf_remesh = _remesh_surface_mmgs(surf, edgel=edgel, hgrad=hgrad, nr=nr)

    with DataGraph.build(out_dir, clean=True) as g:
        cube = g.child("cube")
        dofs = cube.add("tetra.vtk", TetraMesh(tetra))
        cube.add("surf.vtk", TriangleMesh(surf_remesh), mapping=(dofs, "subset"))

        surf_node = cube.child("cube_bottom")
        surf_node.add("bottom.vtk", TriangleMesh(bottom), mapping=(dofs, "barycentric"))
        
        surf_node = cube.child("cube_top")
        dof2 = surf_node.add("top.vtk", TriangleMesh(bottom), mapping=(dofs, "barycentric"))
        
        surf_node = surf_node.child("pts")
        surf_node.add("top.vtk", TriangleMesh(bottom), mapping=(dof2, "barycentric"))
        
        g.dump_mermaid()
        
    data = DataGraph.load(out_dir)
    print(data)




if __name__ == "__main__":
    out_ = fPath(__file__, "out")

    for i, h in enumerate(reversed(np.linspace(1e-3, 5e-3, 5))):
        o = out_ / f"case_{i}"
        o.mkdir(parents=True, exist_ok=True)

        m = generate_bar(float(h), out_dir=o, nr=False)
        break
        # infos = {
        #     "case": int(i),
        #     "points": int(m["tetra"].n_points),
        #     "tetras": int(m["tetra"].n_cells),
        #     "edge_lenght": float(h),
        # }
        # with Container(o) as ct:
        #     dump_json(ct / "infos.json", infos)
