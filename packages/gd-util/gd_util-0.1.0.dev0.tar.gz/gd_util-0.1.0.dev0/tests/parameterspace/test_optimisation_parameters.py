import param
import pytest
from g_util.parameterspace.optimisation_parameters import OptimParams

"""Container for optimization parameters with utilities for serialization and iteration"""

def test_to_dict_excludes_name():
    class P(OptimParams):
        p1 = param.Number(1.0, bounds=(0.0, 1.0))
        p2 = param.Number(2.0, bounds=(0.0, 3.0))

    p = P()
    d = p.to_dict()

    assert "name" not in d
    assert d["p1"] == 1.0
    assert d["p2"] == 2.0

def test_all_keys_matches_to_dict_keys():
    class P(OptimParams):
        p1 = param.Number(1.0, bounds=(0.0, 1.0))
        p2 = param.Number(2.0, bounds=(0.0, 3.0))

    p = P()
    assert p.all_keys == list(p.to_dict().keys())

def test_items_yields_pairs_from_to_dict():
    class P(OptimParams):
        p1 = param.Number(1.0, bounds=(0.0, 1.0))
        p2 = param.Number(2.0, bounds=(0.0, 3.0))

    p = P()
    assert dict(p.items) == p.to_dict()

def test_assign_sets_values_in_key_order():
    class P(OptimParams):
        p1 = param.Number(0.0, bounds=(0.0, 1.0))
        p2 = param.Number(0.0, bounds=(0.0, 3.0))

    p = P()
    assert p.all_keys == ["p1", "p2"]

    p.assign([0.3, 2.7])
    assert p.p1 == pytest.approx(0.3, abs=1e-12)
    assert p.p2 == pytest.approx(2.7, abs=1e-12)

def test_linear_iter_yields_index_and_parameterized():
    class P(OptimParams):
        p1 = param.Number(0.5, bounds=(0.0, 1.0))
        p2 = param.Number(1.0, bounds=(0.9, 1.1))

    p = P()
    out = list(p.linear_iter("p1", "p2", n=3))

    assert len(out) == 3
    assert [i for i, _ in out] == [0, 1, 2]

    xs = [x for _, x in out]
    for x in xs:
        assert hasattr(x, "p1")
        assert hasattr(x, "p2")

    p1_vals = [x.p1 for x in xs]
    p2_vals = [x.p2 for x in xs]
    assert len(set(p1_vals)) > 1
    assert len(set(p2_vals)) > 1

def test_linear_oneatatime_iter_yields_infos_and_changes_one_param():
    class P(OptimParams):
        p1 = param.Number(0.5, bounds=(0.0, 1.0))
        p2 = param.Number(1.0, bounds=(0.9, 1.1))

    p = P()
    out = list(p.linear_oneatatime_iter("p1", "p2", n=3))

    assert out

    for idx, x, xi in out:
        assert isinstance(idx, int)
        assert hasattr(x, "p1")
        assert hasattr(x, "p2")
        assert isinstance(xi, dict)

        assert set(xi.keys()) == {"i", "varying", "value"}
        assert isinstance(xi["i"], int)
        assert xi["varying"] in {"p1", "p2"}

        changed_key = xi["varying"]
        assert getattr(x, changed_key) == pytest.approx(xi["value"], abs=1e-12)

        other_key = "p2" if changed_key == "p1" else "p1"
        assert getattr(x, other_key) == pytest.approx(getattr(p, other_key), abs=1e-12)

def test_lhs_iter_yields_index_and_parameterized_within_bounds():
    class P(OptimParams):
        p1 = param.Number(0.5, bounds=(0.0, 1.0))
        p2 = param.Number(1.0, bounds=(0.9, 1.1))

    p = P()
    out = list(p.lhs_iter("p1", "p2", n=8))

    assert len(out) == 8

    idxs = [i for i, _ in out]
    assert idxs == list(range(8))

    xs = [x for _, x in out]
    for x in xs:
        assert p.param["p1"].bounds[0] <= x.p1 <= p.param["p1"].bounds[1]
        assert p.param["p2"].bounds[0] <= x.p2 <= p.param["p2"].bounds[1]

    p1_vals = [x.p1 for x in xs]
    p2_vals = [x.p2 for x in xs]
    assert len(set(p1_vals)) > 1
    assert len(set(p2_vals)) > 1

def test_random_sampling_iter_yields_index_and_parameterized_within_bounds():
    class P(OptimParams):
        p1 = param.Number(0.5, bounds=(0.0, 1.0))
        p2 = param.Number(1.0, bounds=(0.9, 1.1))

    p = P()
    out = list(p.random_sampling_iter("p1", "p2", n=10))

    assert len(out) == 10
    assert [i for i, _ in out] == list(range(10))

    xs = [x for _, x in out]
    for i, x in xs:
        assert p.param["p1"].bounds[0] <= x.p1 <= p.param["p1"].bounds[1]
        assert p.param["p2"].bounds[0] <= x.p2 <= p.param["p2"].bounds[1]

    p1_vals = [x.p1 for i, x in xs]
    p2_vals = [x.p2 for i, x in xs]
    assert len(set(p1_vals)) > 1
    assert len(set(p2_vals)) > 1
