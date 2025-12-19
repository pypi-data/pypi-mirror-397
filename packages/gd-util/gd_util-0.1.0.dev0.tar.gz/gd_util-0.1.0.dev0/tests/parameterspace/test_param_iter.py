import json
from pathlib import Path

import numpy as np
import param
import pytest

from g_util.parameterspace.param_iter import LinearIter, LinearOneAtATimeIter

"""Iterators over parameter spaces with linear sampling strategies."""


class _Defaults(param.Parameterized):
    p1 = param.Number(0.5, bounds=(0.0, 1.0))
    p2 = param.Number(1.0, bounds=(0.9, 1.1))

    def to_dict(self) -> dict:
        x = json.loads(self.param.serialize_parameters())
        x.pop("name", None)
        return x


def test_len_paramiter_is_number_of_params():
    d = _Defaults()
    it = LinearIter(d.param["p1"], d.param["p2"], defaults=d, n=3)
    assert len(it) == 3


def test_linear_iter_len_is_n():
    d = _Defaults()
    it = LinearIter(d.param["p1"], d.param["p2"], defaults=d, n=4)
    assert len(it) == 4


def test_linear_iter_generates_n_samples_and_updates_all():
    d = _Defaults()
    it = LinearIter(d.param["p1"], d.param["p2"], defaults=d, n=3)

    xs = list(it.gen)
    assert len(xs) == 3

    p1_vals = [x.p1 for x in xs]
    p2_vals = [x.p2 for x in xs]
    assert len(set(p1_vals)) > 1
    assert len(set(p2_vals)) > 1

    for x in xs:
        assert d.param["p1"].bounds[0] <= x.p1 <= d.param["p1"].bounds[1]
        assert d.param["p2"].bounds[0] <= x.p2 <= d.param["p2"].bounds[1]

    assert d.p1 == pytest.approx(0.5, abs=1e-12)
    assert d.p2 == pytest.approx(1.0, abs=1e-12)


def test_linear_oneatatime_iter_len_is_n_times_num_params():
    d = _Defaults()
    it = LinearOneAtATimeIter(d.param["p1"], d.param["p2"], defaults=d, n=3)
    assert len(it) == 3 * 2


def test_gen_infos_matches_generated_values():
    d = _Defaults()
    it = LinearOneAtATimeIter(d.param["p1"], d.param["p2"], defaults=d, n=3)

    infos = list(it.gen_infos)
    xs = list(it.gen)

    assert len(infos) == len(xs)
    assert len(infos) == len(it)

    for x, xi in zip(xs, infos):
        assert set(xi.keys()) == {"i", "varying", "value"}
        assert isinstance(xi["i"], int)
        assert xi["varying"] in {"p1", "p2"}

        changed_key = xi["varying"]
        assert np.isfinite(xi["value"])
        assert getattr(x, changed_key) == pytest.approx(xi["value"], abs=1e-12)

        other_key = "p2" if changed_key == "p1" else "p1"
        assert getattr(x, other_key) == pytest.approx(getattr(d, other_key), abs=1e-12)


def test_save_writes_json_with_expected_keys(tmp_path: Path):
    d = _Defaults()
    it = LinearIter(d.param["p1"], d.param["p2"], defaults=d, n=3)

    out = tmp_path / "iter.json"
    it.save(out)

    assert out.exists()
    payload = json.loads(out.read_text())

    assert set(payload.keys()) == {"n", "N", "bounds", "varying", "defaults"}
    assert payload["n"] == 3
    assert payload["N"] == 3
    assert isinstance(payload["defaults"], dict)
    assert "p1" in payload["defaults"]
    assert "p2" in payload["defaults"]
