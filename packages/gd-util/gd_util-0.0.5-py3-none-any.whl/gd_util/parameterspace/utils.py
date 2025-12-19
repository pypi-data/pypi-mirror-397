from pathlib import Path

import param


class Foldername(param.Foldername):
    __slots__ = ["create_if_not_exist", "must_exist"]

    def __init__(
        self, default=None, create_if_not_exist=True, must_exist=False, **params
    ):
        self.create_if_not_exist = create_if_not_exist
        self.must_exist = must_exist
        super().__init__(default, **params)

    def _resolve(self, path) -> Path:
        if path is None:
            return
        p = Path(path)
        if self.create_if_not_exist:
            p.mkdir(parents=True, exist_ok=True)
        p = p.resolve()
        if self.must_exist and not p.exists():
            raise ValueError(f"Directory does not exist: {p}")
        return p
