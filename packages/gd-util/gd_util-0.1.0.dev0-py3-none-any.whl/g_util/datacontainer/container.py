from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Union, Any
import os
import json

PathLike = Union[str, Path, os.PathLike[str]]


class ContainerInfosError(RuntimeError):
    pass


@dataclass
class Container(os.PathLike[str]):
    root: PathLike
    clean: bool = False
    infos_name: str = "tree.json"
    auto_register: bool = True

    _root: Path = field(init=False, repr=False)
    _infos_path: Path = field(init=False, repr=False)
    _files: Dict[str, str] = field(init=False, default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._root = Path(self.root).expanduser().resolve()
        if self.clean:
            # replace with your clean_dir
            if self._root.exists():
                for p in sorted(self._root.glob("**/*"), reverse=True):
                    if p.is_file() or p.is_symlink():
                        p.unlink(missing_ok=True)
                    elif p.is_dir():
                        p.rmdir()
                self._root.rmdir()
        self._root.mkdir(parents=True, exist_ok=True)
        self._infos_path = self._root / self.infos_name
        self._files = self._load_infos()

    # --- Path-like core -------------------------------------------------
    @property
    def path(self) -> Path:
        return self._root

    def __fspath__(self) -> str:
        return os.fspath(self._root)

    def __str__(self) -> str:
        return str(self._root)

    def __repr__(self) -> str:
        return f"Container({self._root!s})"

    def __truediv__(self, other: PathLike) -> Path:
        other_p = Path(other)
        if other_p.is_absolute():
            # absolute paths: return as-is, do not register
            target = other_p
        else:
            if other_p.suffix == "":
                raise RuntimeError(
                    "Use mkdir() for directories; '/' is for files only."
                )
            target = self._root / other_p

        target.parent.mkdir(parents=True, exist_ok=True)

        if self.auto_register and not other_p.is_absolute():
            self.register(other_p.stem, target.relative_to(self._root).as_posix())

        return target

    def joinpath(self, *parts: PathLike) -> Path:
        # behaves like Path.joinpath, but keeps your '/' policy if you want:
        return self._root.joinpath(*map(Path, parts))

    # Delegate any unknown attribute to the underlying Path
    # IMPORTANT: keys take precedence; else Path methods/properties work.
    def __getattr__(self, name: str) -> Any:
        if name in self._files:
            return self.get(name)
        return getattr(self._root, name)

    # --- Registry -------------------------------------------------------
    def _load_infos(self) -> Dict[str, str]:
        if not self._infos_path.is_file():
            return {}
        try:
            data = json.loads(self._infos_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise ContainerInfosError(f"Cannot read {self._infos_path}") from e

        files = data.get("files")
        if not isinstance(files, dict):
            raise ContainerInfosError("Invalid schema: expected {'files': {key: path}}")

        out: Dict[str, str] = {}
        for k, v in files.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise ContainerInfosError(
                    "Invalid entry types: keys/values must be strings"
                )
            out[k] = v
        return out

    def save(self) -> None:
        payload = {"files": dict(sorted(self._files.items()))}
        self._infos_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def __enter__(self) -> "Container":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.save()

    def register(self, key: str, relpath: PathLike) -> Path:
        rel = Path(relpath).as_posix()
        if key in self._files and self._files[key] != rel:
            raise KeyError(f"{key!r} already registered as {self._files[key]!r}")
        self._files[key] = rel
        return self._root / rel

    def free(self, key: str) -> None:
        self._files.pop(key, None)

    def get(self, key: str) -> Path:
        try:
            return self._root / self._files[key]
        except KeyError as e:
            raise AttributeError(key) from e

    def mkdir(
        self, relpath: PathLike, *, parents: bool = True, exist_ok: bool = True
    ) -> Path:
        p = self._root / Path(relpath)
        p.mkdir(parents=parents, exist_ok=exist_ok)
        return p

    def tree(self, show_keys: bool = True) -> str:
        """
        Generates a visual tree representation of the registered files.

        Args:
            show_keys: If True, displays 'logical_key -> filename'.
                    If False, displays only the filename.

        Returns:
            str: The formatted tree as a string.
        """
        from treelib.tree import Tree

        tree = Tree()
        tree.create_node(tag=f"Container: {self._root.name}", identifier="root")

        # deterministic layout
        sorted_items = sorted(self._files.items(), key=lambda kv: kv[1])

        for key, relpath in sorted_items:
            parts = Path(relpath).parts
            current_id = "root"

            for i, part in enumerate(parts):
                node_id = "/".join(parts[: i + 1])  # unique id by full prefix

                if not tree.contains(node_id):
                    is_last = i == len(parts) - 1
                    label = f"{key} -> {part}" if (is_last and show_keys) else part
                    tree.create_node(tag=label, identifier=node_id, parent=current_id)

                current_id = node_id

        return str(tree.show(stdout=False))
