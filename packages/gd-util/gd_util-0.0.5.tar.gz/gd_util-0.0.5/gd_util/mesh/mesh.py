from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, Self, Union

import meshio
import numpy as np
import pyvista as pv

from gd_util.datacontainer.container import PathLike



def _as_path(p: PathLike) -> Path:
    return p if isinstance(p, Path) else Path(p)


def _is_poly(mesh: pv.DataSet) -> bool:
    return isinstance(mesh, pv.PolyData)


def _run_cli(cmd: list[str]) -> None:
    import subprocess

    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Command failed:\n  {' '.join(cmd)}\n\nOutput:\n{r.stdout}")


def _meshio_cell_type_set(m: meshio.Mesh) -> set[str]:
    return {cb.type for cb in m.cells}


def _only_cells(m: meshio.Mesh, allowed: set[str]) -> meshio.Mesh:
    cells = [cb for cb in m.cells if cb.type in allowed]
    if not cells:
        raise ValueError(
            f"Mesh has no allowed cells {sorted(allowed)} (has {sorted(_meshio_cell_type_set(m))})."
        )

    cell_data: dict[str, list] = {}
    if m.cell_data:
        keep_idx = [i for i, cb in enumerate(m.cells) if cb.type in allowed]
        for k, v in m.cell_data.items():
            cell_data[k] = [v[i] for i in keep_idx]

    return meshio.Mesh(
        points=m.points,
        cells=cells,
        point_data=m.point_data or {},
        cell_data=cell_data,
    )


def _mmg_module_name(kind: str) -> str:
    kind = kind.lower().strip()
    if kind in {"mmgs", "surface"}:
        return "mmgs"
    if kind in {"mmg3d", "volume", "tet", "tetra"}:
        return "mmg3d"
    raise ValueError(f"Unknown mmg kind: {kind!r}")


def _mmg_cli_args(
    *,
    hmin: float | None,
    hmax: float | None,
    hgrad: float | None,
    nr: bool | None,
    extra: Sequence[str] = (),
) -> list[str]:
    args: list[str] = []
    if hmin is not None:
        args += ["-hmin", str(hmin)]
    if hmax is not None:
        args += ["-hmax", str(hmax)]
    if hgrad is not None:
        args += ["-hgrad", str(hgrad)]
    if nr is True:
        args += ["-nr"]
    # NOTE: no "inverse flag" for nr; keep behavior predictable across builds.
    args += list(extra)
    return args


def _mmg_remesh(
    *,
    pvmesh: pv.DataSet,
    mmg: str,
    hmin: float | None,
    hmax: float | None,
    hgrad: float | None = 1.0,
    nr: bool | None = True,
    extra_args: Sequence[str] = (),
) -> pv.DataSet:
    """
    Remesh via MMG Python CLI modules:
      python -m mmgs  in.mesh out.mesh  [mmg flags...]
      python -m mmg3d in.mesh out.mesh  [mmg flags...]

    Uses meshio for IO to .mesh (MEDIT).
    """
    import sys
    import tempfile

    mmg_mod = _mmg_module_name(mmg)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        in_path = td / "in.mesh"
        out_path = td / "out.mesh"

        mi = pv.to_meshio(pvmesh)
        meshio.write(in_path, mi, file_format="medit")

        cmd = [sys.executable, "-m", mmg_mod, str(in_path), str(out_path)]
        cmd += _mmg_cli_args(hmin=hmin, hmax=hmax, hgrad=hgrad, nr=nr, extra=extra_args)
        _run_cli(cmd)

        mo = meshio.read(out_path)
        return pv.from_meshio(mo)


@dataclass(frozen=True, slots=True)
class Mesh:
    """
    Canonical in-memory representation: pyvista.DataSet

    Supported remeshing:
      - Surface remeshing: MMGS (triangles)
      - Volume remeshing: MMG3D (tetrahedra)
    """

    data: pv.DataSet

    # ----------------------------
    # Constructors / IO
    # ----------------------------

    @classmethod
    def read(cls, path: PathLike) -> Self:
        p = _as_path(path)
        return cls(pv.read(str(p)))

    def write(self, path: PathLike, *, binary: bool = True) -> Path:
        p = _as_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.data.save(str(p), binary=binary)
        return p

    @classmethod
    def from_meshio(cls, m: meshio.Mesh) -> Self:
        return cls(pv.from_meshio(m))

    def to_meshio(self) -> meshio.Mesh:
        return pv.to_meshio(self.data)

    # ----------------------------
    # Properties
    # ----------------------------

    @property
    def n_points(self) -> int:
        return int(self.data.n_points)

    @property
    def n_cells(self) -> int:
        return int(self.data.n_cells)

    # ----------------------------
    # Casting helpers
    # ----------------------------

    def as_point(self) -> PointMesh:
        return PointMesh.from_any(self)

    def as_line(self) -> LineMesh:
        return LineMesh.from_any(self)

    def as_triangle(self) -> TriangleMesh:
        return TriangleMesh.from_any(self)

    def as_tetra(self) -> TetraMesh:
        return TetraMesh.from_any(self)


@dataclass(frozen=True, slots=True)
class PointMesh(Mesh):
    @classmethod
    def from_any(cls, mesh: Mesh) -> Self:
        mi = mesh.to_meshio()
        # If vertex cells exist, keep only them. Otherwise, synthesize one vertex per point.
        if any(cb.type == "vertex" for cb in mi.cells):
            mo = _only_cells(mi, {"vertex"})
        else:
            n = len(mi.points)
            verts = np.arange(n, dtype=int).reshape(-1, 1)
            mo = meshio.Mesh(
                points=mi.points,
                cells=[("vertex", verts)],
                point_data=mi.point_data or {},
                cell_data={},
            )
        return cls(pv.from_meshio(mo))


@dataclass(frozen=True, slots=True)
class LineMesh(Mesh):
    @classmethod
    def from_any(cls, mesh: Mesh) -> Self:
        mi = mesh.to_meshio()
        mo = _only_cells(mi, {"line"})
        return cls(pv.from_meshio(mo))


@dataclass(frozen=True, slots=True)
class TriangleMesh(Mesh):
    @classmethod
    def from_any(cls, mesh: Mesh) -> Self:
        ds = mesh.data
        poly_in = ds if _is_poly(ds) else ds.extract_surface()
        poly_in = poly_in.triangulate().clean()

        mi = pv.to_meshio(poly_in)
        mo = _only_cells(mi, {"triangle"})

        out = pv.from_meshio(mo)
        poly_out = out if _is_poly(out) else out.extract_surface()
        poly_out = poly_out.triangulate().clean()
        return cls(poly_out)

    def remesh_mmgs(
        self,
        *,
        edgel: float,
        hgrad: float = 1.0,
        nr: bool = True,
        extra_args: Sequence[str] = (),
    ) -> Self:
        # Strongly normalize surface input
        poly = self.data if _is_poly(self.data) else self.data.extract_surface()
        poly = poly.triangulate().clean()

        out = _mmg_remesh(
            pvmesh=poly,
            mmg="mmgs",
            hmin=edgel,
            hmax=edgel,
            hgrad=hgrad,
            nr=nr,
            extra_args=extra_args,
        )

        poly_out = out if _is_poly(out) else out.extract_surface()
        poly_out = poly_out.triangulate().clean()
        return type(self)(poly_out)


@dataclass(frozen=True, slots=True)
class TetraMesh(Mesh):
    @classmethod
    def from_any(cls, mesh: Mesh) -> Self:
        ug = mesh.data.cast_to_unstructured_grid()
        mi = pv.to_meshio(ug)
        mo = _only_cells(mi, {"tetra"})
        return cls(pv.from_meshio(mo))

    def remesh_mmg3d(
        self,
        *,
        hmin: float,
        hmax: float,
        hgrad: float = 1.0,
        nr: bool = True,
        extra_args: Sequence[str] = (),
    ) -> Self:
        # Normalize volume input
        ug = self.data.cast_to_unstructured_grid()

        # Ensure tetra-only input for mmg3d (fail fast if not)
        mi = pv.to_meshio(ug)
        mi = _only_cells(mi, {"tetra"})
        ug_tet = pv.from_meshio(mi).cast_to_unstructured_grid()

        out = _mmg_remesh(
            pvmesh=ug_tet,
            mmg="mmg3d",
            hmin=hmin,
            hmax=hmax,
            hgrad=hgrad,
            nr=nr,
            extra_args=extra_args,
        )

        # Normalize output to tetra-only, too
        mo = pv.to_meshio(out.cast_to_unstructured_grid())
        mo = _only_cells(mo, {"tetra"})
        return type(self)(pv.from_meshio(mo))
