from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, Optional, Tuple, Literal

from g_util.datacontainer.container import Container, PathLike
from g_util.mesh.mesh import Mesh

MappingType = Literal["subset", "barycentric"]


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _qualname(tp: type) -> str:
    return f"{tp.__module__}.{tp.__qualname__}"


def _import_type(qualname: str) -> type:
    mod, _, name = qualname.rpartition(".")
    if not mod:
        raise ValueError(f"Invalid type qualname: {qualname!r}")
    return getattr(import_module(mod), name)


def _ensure_mapping_type(t: Optional[str]) -> Optional[MappingType]:
    if t is None:
        return None
    if t not in ("subset", "barycentric"):
        raise ValueError(f"Unsupported mapping: {t!r} (expected 'subset'|'barycentric')")
    return t  # type: ignore[return-value]


def _join_key(parts: List[str]) -> str:
    # stable + collision-resistant
    return "__".join(parts)

def _node_name_from_relpath(relpath: str) -> str:
    p = Path(relpath)
    stem = p.stem
    parent = p.parent.as_posix()
#     return f"{parent}/{stem}" if parent and parent != "." else stem
    return f"{parent}" if parent and parent != "." else stem



# -----------------------------------------------------------------------------
# Persisted spec (JSON)
# -----------------------------------------------------------------------------

@dataclass(slots=True)
class _MeshSpec:
    name: str  # leaf name (stem)
    key: str
    relpath: str
    loader: str
    user_type: Optional[str] = None
    mapping_to: Optional[str] = None
    mapping_type: Optional[MappingType] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "name": self.name,
            "key": self.key,
            "relpath": self.relpath,
            "loader": self.loader,
        }
        if self.user_type is not None:
            d["user_type"] = self.user_type
        if self.mapping_type is not None:
            d["mapping"] = {"to": self.mapping_to, "type": self.mapping_type}
        return d

    @staticmethod
    def from_dict(d: Mapping[str, Any]) -> "_MeshSpec":
        mapping = d.get("mapping")
        return _MeshSpec(
            name=str(d["name"]),
            key=str(d["key"]),
            relpath=str(d["relpath"]),
            loader=str(d["loader"]),
            user_type=None if d.get("user_type") is None else str(d.get("user_type")),
            mapping_to=(
                None
                if mapping is None or mapping.get("to") is None
                else str(mapping.get("to"))
            ),
            mapping_type=_ensure_mapping_type(
                None
                if mapping is None or mapping.get("type") is None
                else str(mapping.get("type"))
            ),
        )


# -----------------------------------------------------------------------------
# Runtime nodes
# -----------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class DataGraphNode:
    graph: "DataGraph"
    name: str
    key: str
    relpath: str
    loader: type
    user_type: Optional[str]
    mapping_to: Optional[str]
    mapping_type: Optional[MappingType]

    @property
    def path(self) -> Path:
        return self.graph.ct.path / self.relpath

    def mesh(self) -> Mesh:
        return self.loader.read(self.path)

    def mappings(self) -> Tuple[Tuple[str, MappingType], ...]:
        if self.mapping_to is None or self.mapping_type is None:
            return ()
        return ((self.mapping_to, self.mapping_type),)


# -----------------------------------------------------------------------------
# Build DSL objects
# -----------------------------------------------------------------------------

@dataclass(slots=True)
class DataGraphAdd:
    filename: str
    mesh: Mesh
    mapping: Optional[Tuple[str, MappingType]] = None  # parent_key
    user_type: Optional[str] = None


@dataclass(slots=True)
class GroupHandle:
    session: "_BuildSession"
    path_parts: List[str]

    def child(self, name: str) -> "GroupHandle":
        return GroupHandle(self.session, self.path_parts + [str(name)])

    def add(self, *a, **kw) -> str:
        return self.session._add_mesh(self.path_parts, DataGraphAdd(*a, **kw))


# -----------------------------------------------------------------------------
# DataGraph (runtime)
# -----------------------------------------------------------------------------

@dataclass(slots=True)
class DataGraph:
    ct: Container
    schema: str
    groups: Dict[str, Any]
    meshes: List[Dict[str, Any]]
    _index: Dict[str, DataGraphNode] = field(default_factory=dict, init=False, repr=False)

    @staticmethod
    def build(out_dir: PathLike, *, clean: bool = False, fname: str = "datagraph.json") -> "_BuildSession":
        return _BuildSession(ct=Container(Path(out_dir), clean=clean), fname=fname)

    @staticmethod
    def load(out_dir: PathLike, *, fname: str = "datagraph.json") -> "DataGraph":
        ct = Container(Path(out_dir))
        p = ct.path / fname
        payload = json.loads(p.read_text(encoding="utf-8"))

        if not isinstance(payload, dict) or payload.get("schema") != "datagraph/v1":
            raise ValueError(f"Invalid datagraph file: {p}")

        g = DataGraph(
            ct=ct,
            schema=str(payload["schema"]),
            groups=dict(payload.get("groups", {})),
            meshes=list(payload.get("meshes", [])),
        )
        g._build_index()
        return g

    def _build_index(self) -> None:
        self._index.clear()
        for raw in self.meshes:
            spec = _MeshSpec.from_dict(raw)
            loader = _import_type(spec.loader)
            self._index[spec.key] = DataGraphNode(
                graph=self,
                name=spec.name,
                key=spec.key,
                relpath=spec.relpath,
                loader=loader,
                user_type=spec.user_type,
                mapping_to=spec.mapping_to,
                mapping_type=spec.mapping_type,
            )

    def __iter__(self) -> Iterator[DataGraphNode]:
        if not self._index:
            self._build_index()
        yield from self._index.values()

    def by_key(self, key: str) -> DataGraphNode:
        if not self._index:
            self._build_index()
        return self._index[key]


    def dump_mermaid(self, fname: str = "data_graph.md") -> Path:
        if not self._index:
            self._build_index()

        def node_id(key: str) -> str:
            return key.replace("-", "_").replace(".", "_")

        def display_node_name(relpath: str) -> str:
            p = Path(relpath)
            parts = list(p.parts)
            if len(parts) <= 1:
                return p.stem
            if len(parts) == 2:
                return parts[0]  # "cube", not "cube/tetra"
            return "/".join(parts[:-1])  # "cube/cube_bottom"

        def short_loader_name(loader: type) -> str:
            return getattr(loader, "__name__", str(loader))

        def mesh_stats(node: DataGraphNode) -> Tuple[Optional[int], Optional[int], Optional[str]]:
            """
            Best-effort extraction across different mesh implementations.
            Returns (n_points, n_cells, cell_type).
            """
            try:
                m = node.mesh()
            except Exception:
                return None, None, None

            # points
            n_points = None
            for attr in ("n_points", "npoints", "num_points", "n_vertices", "n_verts"):
                v = getattr(m, attr, None)
                if isinstance(v, int):
                    n_points = v
                    break
            if n_points is None:
                pts = getattr(m, "points", None)
                if pts is not None:
                    try:
                        n_points = len(pts)
                    except Exception:
                        pass

            # cells
            n_cells = None
            for attr in ("n_cells", "ncells", "num_cells", "n_elements", "n_faces", "n_tets", "n_tris"):
                v = getattr(m, attr, None)
                if isinstance(v, int):
                    n_cells = v
                    break
            if n_cells is None:
                cells = getattr(m, "cells", None)
                if cells is not None:
                    try:
                        n_cells = len(cells)
                    except Exception:
                        pass

            # cell type
            cell_type = None
            for attr in ("cell_type", "celltype", "cells_type", "element_type"):
                v = getattr(m, attr, None)
                if isinstance(v, str) and v:
                    cell_type = v
                    break
            if cell_type is None:
                # common patterns: m.cells may be a dict-like by type, or an object with .type
                cells = getattr(m, "cells", None)
                if isinstance(cells, dict) and cells:
                    try:
                        cell_type = next(iter(cells.keys()))
                        cell_type = str(cell_type)
                    except Exception:
                        pass
                else:
                    ct = getattr(cells, "type", None)
                    if isinstance(ct, str) and ct:
                        cell_type = ct

            return n_points, n_cells, cell_type

        lines: List[str] = ["graph BT"]

        # cache stats to avoid re-reading meshes if referenced multiple times
        stats_cache: Dict[str, Tuple[Optional[int], Optional[int], Optional[str]]] = {}

        # nodes
        for node in self._index.values():
            nid = node_id(node.key)
            basename = Path(node.relpath).name
            node_name = display_node_name(node.relpath)

            if node.key not in stats_cache:
                stats_cache[node.key] = mesh_stats(node)
            n_points, n_cells, cell_type = stats_cache[node.key]

            parts = [
                f"{node_name}<br/>{basename} &lt;{short_loader_name(node.loader)}&gt;",
                f"{n_points if n_points is not None else '?'} points ; {n_cells if n_cells is not None else '?'} cells",
            ]
            if cell_type:
                parts.append(f"cell: {cell_type}")

            label = "<br/>".join(parts)
            lines.append(f'    {nid}["{label}"]')

        # edges: child -> parent (bottom-up)
        for node in self._index.values():
            if node.mapping_to is None or node.mapping_type is None:
                continue
            child = node_id(node.key)
            parent = node_id(node.mapping_to)
            lines.append(f"    {child} -->|{node.mapping_type}| {parent}")

        md = "\n".join(["```mermaid", "\n".join(lines), "```", ""])
        path = self.ct.path / fname
        path.write_text(md, encoding="utf-8")
        return path

# -----------------------------------------------------------------------------
# Build session (context manager)
# -----------------------------------------------------------------------------

@dataclass(slots=True)
class _BuildSession:
    ct: Container
    fname: str
    schema: str = "datagraph/v1"

    groups: Dict[str, Any] = field(default_factory=dict)
    meshes: List[_MeshSpec] = field(default_factory=list)

    def __enter__(self) -> "_BuildSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            return

        payload = {
            "schema": self.schema,
            "groups": self.groups,
            "meshes": [m.to_dict() for m in self.meshes],
        }
        p = self.ct.path / self.fname
        p.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.ct.save()

    # DSL entrypoint
    def child(self, name: str) -> GroupHandle:
        name = str(name)
        self._ensure_group([name])
        return GroupHandle(self, [name])

    def dump_mermaid(self, fname: str = "data_graph.md") -> Path:
        # build a temporary runtime graph view from current specs
        g = DataGraph(
            ct=self.ct,
            schema=self.schema,
            groups=self.groups,
            meshes=[m.to_dict() for m in self.meshes],
        )
        g._build_index()
        return g.dump_mermaid(fname=fname)

    # internal
    def _ensure_group(self, parts: List[str]) -> Dict[str, Any]:
        cur = self.groups
        for p in parts:
            cur = cur.setdefault(p, {})
        return cur

    def _add_mesh(self, group_parts: List[str], add: DataGraphAdd) -> str:
        group = self._ensure_group(group_parts)

        filename = str(add.filename)
        leaf_name = Path(filename).stem

        # store under node_name/.../node_name/fname
        rel_dir = Path(*group_parts).as_posix()
        relpath = f"{rel_dir}/{filename}" if rel_dir else filename

        dst = self.ct.path / relpath
        dst.parent.mkdir(parents=True, exist_ok=True)
        add.mesh.write(dst)

        key = _join_key(group_parts + [leaf_name])
        self.ct.register(key, relpath)

        mapping_to: Optional[str] = None
        mapping_type: Optional[MappingType] = None
        if add.mapping is not None:
            parent_key, mtype = add.mapping
            mapping_type = _ensure_mapping_type(mtype)
            mapping_to = parent_key

        self.meshes.append(_MeshSpec(
            name=leaf_name,
            key=key,
            relpath=relpath,
            loader=_qualname(add.mesh.__class__),
            user_type=add.user_type,
            mapping_to=mapping_to,
            mapping_type=mapping_type,
        ))

        # optional breadcrumb
        group[leaf_name] = {"mesh_key": key, "file": filename}
        return key
