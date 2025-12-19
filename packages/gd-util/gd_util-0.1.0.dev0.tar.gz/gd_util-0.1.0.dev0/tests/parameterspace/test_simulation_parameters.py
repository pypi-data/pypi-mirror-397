import json
from pathlib import Path

import param
import pytest

from g_util.parameterspace.optimisation_parameters import OptimParams
from g_util.parameterspace.simulation_parameters import SimulationParams

"""Simulation parameters persistence helpers (save/load/copy/save_with)."""


def test_to_dict_serializes_out_dir_as_string_or_none():
    p = SimulationParams()
    d = p.to_dict()
    assert "out_dir" in d
    assert d["out_dir"] is None

    td = Path("/tmp/dummy_path")  # Simulation d'un chemin
    p.out_dir = td
    d = p.to_dict()
    assert d["out_dir"] == str(td)


def test_save_writes_params_json_and_optional_infos_json(tmp_path: Path):
    out = tmp_path / "run"
    out.mkdir(parents=True, exist_ok=True)

    p = SimulationParams()
    p.out_dir = out

    p.save(data={"a": 1})

    assert (out / "params.json").exists()
    assert (out / "infos.json").exists()

    params_payload = json.loads((out / "params.json").read_text())
    infos_payload = json.loads((out / "infos.json").read_text())

    assert "out_dir" in params_payload
    assert params_payload["out_dir"] == str(out)
    assert infos_payload == {"a": 1}


def test_load_from_restores_known_fields_and_adds_unknown_as_numbers(tmp_path: Path):
    out = tmp_path / "run"
    out.mkdir(parents=True, exist_ok=True)

    payload = {"out_dir": str(out), "p1": 0.25, "p2": 1.05}
    (out / "params.json").write_text(json.dumps(payload))

    p = SimulationParams.load_from(out)

    assert p.out_dir == out
    assert hasattr(p, "p1")
    assert hasattr(p, "p2")
    assert p.p1 == pytest.approx(0.25, abs=1e-12)
    assert p.p2 == pytest.approx(1.05, abs=1e-12)

    assert isinstance(p.param["p1"], param.Number)
    assert isinstance(p.param["p2"], param.Number)


def test_copy_creates_independent_object(tmp_path: Path):
    p = SimulationParams()
    p.out_dir = tmp_path
    p.param.add_parameter("p1", param.Number(0.1))

    q = p.copy()
    assert p is not q
    assert q.out_dir == p.out_dir
    assert q.p1 == pytest.approx(p.p1, abs=1e-12)

    q.p1 = 0.9
    assert p.p1 == pytest.approx(0.1, abs=1e-12)
    assert q.p1 == pytest.approx(0.9, abs=1e-12)


def test_save_with_sets_out_dir_adds_optim_params_and_saves(tmp_path: Path):
    class P(OptimParams):
        p1 = param.Number(0.3, bounds=(0.0, 1.0))
        p2 = param.Number(1.02, bounds=(0.9, 1.1))

    optim = P()
    out = tmp_path / "run"
    sp = SimulationParams()
    sp.save_with(out, optim)

    assert sp.out_dir == out
    assert (out / "params.json").exists()

    saved = json.loads((out / "params.json").read_text())
    assert "p1" in saved
    assert "p2" in saved
    assert saved["p1"] == pytest.approx(0.3, abs=1e-12)
    assert saved["p2"] == pytest.approx(1.02, abs=1e-12)

    loaded = SimulationParams.load_from(out)
    assert loaded.p1 == pytest.approx(0.3, abs=1e-12)
    assert loaded.p2 == pytest.approx(1.02, abs=1e-12)
