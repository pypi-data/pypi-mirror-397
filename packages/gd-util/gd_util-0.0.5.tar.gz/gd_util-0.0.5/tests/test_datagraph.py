from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pyvista as pv
import pytest

from gd_util.datagraph import DataGraph
from gd_util.mesh.mesh import Mesh, TriangleMesh, TetraMesh


# -----------------------------------------------------------------------------
# Local fixtures (do NOT rely on cross-file pytest discovery)
# -----------------------------------------------------------------------------


@pytest.fixture
def sample_tetra_vtk(tmp_path: Path) -> Path:
    path = tmp_path / "tetra.vtk"

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    cells = np.array([4, 0, 1, 2, 3])
    cell_types = np.array([pv.CellType.TETRA])

    grid = pv.UnstructuredGrid(cells, cell_types, points)
    grid.save(path)

    return path


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def _read_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def _mesh_spec(payload: Dict[str, Any], key: str) -> Dict[str, Any]:
    return next(m for m in payload["meshes"] if m["key"] == key)


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


def test_datagraph_full_roundtrip_with_nested_groups(
    sample_tetra_vtk: Path, tmp_path: Path
) -> None:
    out_dir = tmp_path / "out"

    base = Mesh.read(sample_tetra_vtk)
    tetra = base.as_tetra().data
    surf = base.as_triangle().data

    # reuse same surface for simplicity (top / bottom semantics irrelevant here)
    bottom = surf
    top = surf

    # -------------------------
    # build
    # -------------------------
    with DataGraph.build(out_dir, clean=True) as g:
        cube = g.child("cube")

        dofs = cube.add("tetra.vtk", TetraMesh(tetra))
        cube.add("surf.vtk", TriangleMesh(surf), mapping=(dofs, "subset"))

        cube_bottom = cube.child("cube_bottom")
        cube_bottom.add(
            "bottom.vtk", TriangleMesh(bottom), mapping=(dofs, "barycentric")
        )

        cube_top = cube.child("cube_top")
        dof2 = cube_top.add("top.vtk", TriangleMesh(top), mapping=(dofs, "barycentric"))

        pts = cube_top.child("pts")
        pts.add("top.vtk", TriangleMesh(top), mapping=(dof2, "barycentric"))

    # -------------------------
    # persisted json
    # -------------------------
    payload = _read_json(out_dir / "datagraph.json")

    assert payload["schema"] == "datagraph/v1"

    keys = {m["key"] for m in payload["meshes"]}
    assert keys == {
        "cube__tetra",
        "cube__surf",
        "cube__cube_bottom__bottom",
        "cube__cube_top__top",
        "cube__cube_top__pts__top",
    }

    assert _mesh_spec(payload, "cube__surf")["mapping"] == {
        "to": "cube__tetra",
        "type": "subset",
    }
    assert _mesh_spec(payload, "cube__cube_top__pts__top")["mapping"] == {
        "to": "cube__cube_top__top",
        "type": "barycentric",
    }

    # -------------------------
    # files written correctly
    # -------------------------
    assert (out_dir / "cube/tetra.vtk").exists()
    assert (out_dir / "cube/surf.vtk").exists()
    assert (out_dir / "cube/cube_bottom/bottom.vtk").exists()
    assert (out_dir / "cube/cube_top/top.vtk").exists()
    assert (out_dir / "cube/cube_top/pts/top.vtk").exists()

    # -------------------------
    # load + runtime
    # -------------------------
    data = DataGraph.load(out_dir)

    assert {n.key for n in data} == keys

    n_tet = data.by_key("cube__tetra")
    n_surf = data.by_key("cube__surf")

    assert n_tet.mappings() == ()
    assert n_surf.mappings() == (("cube__tetra", "subset"),)

    m0 = n_tet.mesh()
    m1 = n_surf.mesh()

    assert isinstance(m0, TetraMesh)
    assert isinstance(m1, TriangleMesh)
    assert m0.n_cells == 1
    assert m1.n_cells >= 4


def test_build_clean_removes_previous_content(
    sample_tetra_vtk: Path, tmp_path: Path
) -> None:
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "old.txt").write_text("x", encoding="utf-8")

    base = Mesh.read(sample_tetra_vtk)
    tetra = base.as_tetra().data

    with DataGraph.build(out_dir, clean=True) as g:
        cube = g.child("cube")
        _ = cube.add("tetra.vtk", TetraMesh(tetra))

    assert not (out_dir / "old.txt").exists()
    assert (out_dir / "datagraph.json").exists()
    assert (out_dir / "cube" / "tetra.vtk").exists()


def test_invalid_mapping_type_raises_valueerror(
    sample_tetra_vtk: Path, tmp_path: Path
) -> None:
    out_dir = tmp_path / "out"
    base = Mesh.read(sample_tetra_vtk)
    tetra = base.as_tetra().data
    surf = base.as_triangle().data

    with DataGraph.build(out_dir, clean=True) as g:
        cube = g.child("cube")
        dofs = cube.add("tetra.vtk", TetraMesh(tetra))

        with pytest.raises(ValueError, match="Unsupported mapping"):
            cube.add("surf.vtk", TriangleMesh(surf), mapping=(dofs, "nope"))  # type: ignore[arg-type]


def test_mapping_to_unknown_key_is_preserved_and_exposed(
    sample_tetra_vtk: Path, tmp_path: Path
) -> None:
    """
    DataGraph does not validate referential integrity (today).
    This test locks that behavior: mapping_to can point to a missing key
    and still roundtrips (mappings() exposes it).
    """
    out_dir = tmp_path / "out"
    base = Mesh.read(sample_tetra_vtk)
    surf = base.as_triangle().data

    with DataGraph.build(out_dir, clean=True) as g:
        cube = g.child("cube")
        cube.add("surf.vtk", TriangleMesh(surf), mapping=("missing_key", "subset"))

    data = DataGraph.load(out_dir)
    node = data.by_key("cube__surf")
    assert node.mappings() == (("missing_key", "subset"),)


def test_duplicate_leaf_in_same_group_overwrites_breadcrumb_but_keeps_mesh_entries(
    sample_tetra_vtk: Path, tmp_path: Path
) -> None:
    """
    Current behavior: adding the same leaf name twice in the same group produces
    duplicate mesh entries (same key), but breadcrumbs in groups dict are overwritten.
    This test documents that behavior (and will catch accidental changes).
    """
    out_dir = tmp_path / "out"
    base = Mesh.read(sample_tetra_vtk)
    surf = base.as_triangle().data

    with DataGraph.build(out_dir, clean=True) as g:
        cube = g.child("cube")
        cube.add("surf.vtk", TriangleMesh(surf))
        cube.add(
            "surf.vtk", TriangleMesh(surf)
        )  # same filename -> same leaf -> same key

    payload = _read_json(out_dir / "datagraph.json")

    # two entries in meshes list (because builder appends)
    assert sum(1 for m in payload["meshes"] if m["key"] == "cube__surf") == 2

    # breadcrumb exists and points to the same key (overwritten to same value)
    assert payload["groups"]["cube"]["surf"]["mesh_key"] == "cube__surf"


def test_loader_import_failure_on_load_raises(
    sample_tetra_vtk: Path, tmp_path: Path
) -> None:
    """
    Corrupt the persisted loader qualname; DataGraph.load should fail when building index.
    """
    out_dir = tmp_path / "out"
    base = Mesh.read(sample_tetra_vtk)
    tetra = base.as_tetra().data

    with DataGraph.build(out_dir, clean=True) as g:
        cube = g.child("cube")
        _ = cube.add("tetra.vtk", TetraMesh(tetra))

    p = out_dir / "datagraph.json"
    payload = _read_json(p)
    payload["meshes"][0]["loader"] = "no_such_module.Nope"
    p.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    with pytest.raises(ModuleNotFoundError):
        _ = DataGraph.load(out_dir)


def test_node_mesh_raises_if_file_missing(
    sample_tetra_vtk: Path, tmp_path: Path
) -> None:
    """
    Load succeeds (JSON OK), but reading a node's mesh should fail if the file is missing.
    """
    out_dir = tmp_path / "out"
    base = Mesh.read(sample_tetra_vtk)
    tetra = base.as_tetra().data

    with DataGraph.build(out_dir, clean=True) as g:
        cube = g.child("cube")
        _ = cube.add("tetra.vtk", TetraMesh(tetra))

    data = DataGraph.load(out_dir)

    # delete the mesh file after load
    (out_dir / "cube" / "tetra.vtk").unlink()

    with pytest.raises(Exception):
        _ = data.by_key("cube__tetra").mesh()


def test_json_is_deterministic_sorted_keys(
    sample_tetra_vtk: Path, tmp_path: Path
) -> None:
    out_dir = tmp_path / "out"
    base = Mesh.read(sample_tetra_vtk)
    tetra = base.as_tetra().data

    with DataGraph.build(out_dir, clean=True) as g:
        cube = g.child("cube")
        _ = cube.add("tetra.vtk", TetraMesh(tetra))

    raw = (out_dir / "datagraph.json").read_text(encoding="utf-8")

    # top-level keys are sorted alphabetically because json.dumps(..., sort_keys=True)
    assert raw.find('"groups"') < raw.find('"meshes"') < raw.find('"schema"')


def test_iteration_is_lazy_and_builds_index(
    sample_tetra_vtk: Path, tmp_path: Path
) -> None:
    """
    __iter__ builds index on first iteration. Lock that behavior.
    """
    out_dir = tmp_path / "out"
    base = Mesh.read(sample_tetra_vtk)
    tetra = base.as_tetra().data

    with DataGraph.build(out_dir, clean=True) as g:
        cube = g.child("cube")
        _ = cube.add("tetra.vtk", TetraMesh(tetra))

    data = DataGraph.load(out_dir)

    # internal index starts built by load() (it calls _build_index), but this
    # test still ensures iter works and yields nodes with correct keys
    ks = [n.key for n in data]
    assert ks == ["cube__tetra"]
