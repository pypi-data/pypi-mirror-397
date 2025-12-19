import json
from pathlib import Path

import numpy as np
import param
import pandas as pd
import pytest

from gd_util.parameterspace.optimisation_parameters import OptimParams
from gd_util.parameterspace.parameter_space import (
    BaseParameterSpaceOperation,
    ParameterSpaceAsk,
    ParameterSpaceExploration,
)
from gd_util.parameterspace.simulation_parameters import SimulationParams

"""Parameter space utilities: exploration (dump/run/gather/plot) and ask-mode dumping."""


def _worker(case_dir: Path) -> None:
    params = SimulationParams.load_from(case_dir)
    t = np.linspace(0.0, 1.0, 10)
    res = params.p1 * np.sin(params.p2 * 2.0 * np.pi * t)
    np.savetxt(Path(params.out_dir) / "result.txt", res)


# --- Tests pour BaseParameterSpaceOperation ---


def test_base_dirs_uses_default_dir_key(tmp_path: Path):
    out = tmp_path / "out"
    out.mkdir(parents=True, exist_ok=True)

    (out / f"{BaseParameterSpaceOperation.DIR_KEY}_0").mkdir()
    (out / f"{BaseParameterSpaceOperation.DIR_KEY}_1").mkdir()
    (out / "other_0").mkdir()

    ps = BaseParameterSpaceOperation(out)
    assert [d.name for d in ps.dirs] == ["case_0", "case_1"]


# --- Tests pour ParameterSpaceExploration ---


def test_dump_params_creates_case_dirs_with_json(tmp_path: Path):
    class P(OptimParams):
        p1 = param.Number(0.5, bounds=(0.0, 1.0))
        p2 = param.Number(1.0, bounds=(0.9, 1.1))

    out = tmp_path / "out"
    explo = ParameterSpaceExploration(out)

    simu = SimulationParams()
    optim = P()

    explo.dump_params(simu, optim, n=2)

    dirs = explo.dirs
    assert len(dirs) == 2 * len(optim.all_keys)
    for d in dirs:
        assert d.name.startswith("case_")
        assert (d / "params.json").exists()
        assert (d / "infos.json").exists()


def test_run_sequential_executes_worker_for_all_cases(tmp_path: Path):
    class P(OptimParams):
        p1 = param.Number(0.5, bounds=(0.0, 1.0))
        p2 = param.Number(1.0, bounds=(0.9, 1.1))

    out = tmp_path / "out"
    explo = ParameterSpaceExploration(out)

    simu = SimulationParams()
    optim = P()

    explo.dump_params(simu, optim, n=2)
    explo.run(_worker, parallel=False)

    for d in explo.dirs:
        assert (d / "result.txt").exists()
        arr = np.loadtxt(d / "result.txt")
        assert arr.shape == (10,)
        assert np.isfinite(arr).all()


def test_gather_results_builds_dataframe_and_writes_csv(tmp_path: Path):
    class P(OptimParams):
        p1 = param.Number(0.5, bounds=(0.0, 1.0))
        p2 = param.Number(1.0, bounds=(0.9, 1.1))

    out = tmp_path / "out"
    explo = ParameterSpaceExploration(out)

    simu = SimulationParams()
    optim = P()

    explo.dump_params(simu, optim, n=2)
    explo.run(_worker, parallel=False)

    df = explo.gather_results()

    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 10
    assert df.columns.nlevels == 3
    assert (out / "results.csv").exists()


def test_value_map_reads_infos(tmp_path: Path):
    class P(OptimParams):
        p1 = param.Number(0.5, bounds=(0.0, 1.0))
        p2 = param.Number(1.0, bounds=(0.9, 1.1))

    out = tmp_path / "out"
    explo = ParameterSpaceExploration(out)

    simu = SimulationParams()
    optim = P()

    explo.dump_params(simu, optim, n=2)

    vm = explo.value_map
    assert set(k[0] for k in vm.keys()) == {"p1", "p2"}
    assert all(isinstance(k[1], int) for k in vm.keys())
    assert all(isinstance(v, float) for v in vm.values())


def test_plot_results_creates_png(tmp_path: Path):
    class P(OptimParams):
        p1 = param.Number(0.5, bounds=(0.0, 1.0))
        p2 = param.Number(1.0, bounds=(0.9, 1.1))

    out = tmp_path / "out"
    explo = ParameterSpaceExploration(out)

    simu = SimulationParams()
    optim = P()

    explo.dump_params(simu, optim, n=2)
    explo.run(_worker, parallel=False)
    explo.gather_results()
    explo.plot_results(show=False)

    assert (out / "plots.png").exists()


# --- Tests pour ParameterSpaceAsk ---


def test_dirs_uses_pop_key(tmp_path: Path):
    out = tmp_path / "out"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pop_0").mkdir()
    (out / "pop_1").mkdir()
    (out / "case_0").mkdir()

    ask = ParameterSpaceAsk(out)
    assert [d.name for d in ask.dirs] == ["pop_0", "pop_1"]


def test_dump_params_creates_pop_dirs_with_params_json(tmp_path: Path):
    class P(OptimParams):
        p1 = param.Number(0.3, bounds=(0.0, 1.0))
        p2 = param.Number(0.93, bounds=(0.9, 1.1))

    out = tmp_path / "out"
    ask = ParameterSpaceAsk(out)

    simu = SimulationParams()
    optim = P()

    values = np.array([[0.2, 0.95], [0.8, 1.05]], dtype=float)
    ask.dump_params(values, simu, optim)

    dirs = ask.dirs
    assert len(dirs) == 2
    for d in dirs:
        assert d.name.startswith("pop_")
        assert (d / "params.json").exists()
