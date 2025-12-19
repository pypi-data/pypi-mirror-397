import logging
from pathlib import Path
from functools import partial
from pprint import pprint
from typing import Callable
import numpy as np
import matplotlib.pyplot as plt

import param
from pymoo.algorithms.soo.nonconvex.cmaes import CMAES
from pymoo.core.problem import Problem
from pymoo.optimize import minimize

from g_util.parameterspace import (
    OptimParams,
    SimulationParams,
    ParameterSpaceAsk,
)
from g_util.utils import clean_dir


def prgm_worker(dname):
    params = SimulationParams.load_from(dname)
    t = np.linspace(0, 1, 100)
    res = params.p1 * np.sin(params.p2 * 2 * np.pi * t)
    return res


def cmaes_loss(dname: str, target: np.ndarray = None):
    res = prgm_worker(dname)
    return np.sqrt(np.mean((res - target) ** 2))


def fake_worker(dname: str):
    params = SimulationParams.load_from(dname)
    res = prgm_worker(dname)
    np.savetxt(params.out_dir / "result.txt", res)
    return res


class MyProblem(Problem):
    def __init__(
        self,
        out_path: str,
        simulation_params: SimulationParams,
        optim_params: OptimParams,
        loss: Callable,
        target: np.ndarray,
    ):
        self.out_path = Path(out_path)
        self.simulation_params = simulation_params
        self.optim_params = optim_params
        self.loss = partial(loss, target=target)
        self.gen = 0

        vals = [
            p
            for p in optim_params.param.objects().values()
            if isinstance(p, param.Number)
        ]

        xl = np.array([p.bounds[0] for p in vals])
        xu = np.array([p.bounds[1] for p in vals])

        super().__init__(n_var=len(optim_params.to_dict()), n_obj=1, xl=xl, xu=xu)

    def _evaluate(self, x, out):
        self.gen += 1

        explo = ParameterSpaceAsk(self.out_path / f"gen_{self.gen}")
        explo.dump_params(x, self.simulation_params, self.optim_params)
        vals = explo.run(self.loss, parallel=False)

        out["F"] = vals

        clean_dir(explo.out_dir)


def make_fake_target(
    out, simulation_params: SimulationParams, optim_params: OptimParams
):
    simulation_params.out_dir = out
    for name, p in optim_params.param.objects().items():
        if isinstance(p, param.Number):
            lo, hi = p.bounds
            value = np.random.uniform(lo, hi)
            setattr(optim_params, name, value)
            simulation_params.param.add_parameter(name, param.Number(value))
    simulation_params.save()
    fake_worker(out)

    res = np.loadtxt(out / "result.txt")
    res += np.random.normal(scale=0.03, size=res.shape)  # noise
    np.savetxt(out / "result.txt", res)


def run_cmaes():
    out_path = Path(__file__).parent / "out"

    class Params(OptimParams):
        p1 = param.Number(1, bounds=(0, 1), doc="Parameter 1")
        p2 = param.Number(1, bounds=(0.9, 1.1), doc="Parameter 2")

    simulation_params = SimulationParams()
    optim_params = Params()

    make_fake_target(out_path / "target", simulation_params, optim_params)
    target = np.loadtxt(out_path / "target/result.txt")

    problem = MyProblem(out_path, simulation_params, optim_params, cmaes_loss, target)
    algorithm = CMAES()

    res = minimize(
        problem,
        algorithm,
        seed=1,
        verbose=True,
        termination=("n_gen", 30),
        save_history=True,
    )
    np.save(out_path / "best_cma.npy", res.X)

    print("Best solution found:")
    print("  x =", res.X)
    print("  f(x) =", res.F)

    # Extract convergence history: best f at each generation
    best_F = []
    for algo in res.history:
        pop_F = algo.pop.get("F")
        best_F.append(np.min(pop_F))

    best_F = np.array(best_F)
    log.info(f"Last 5 best F values: {best_F[-5:]}")

    # Plot convergence
    fig, ax = plt.subplots()
    ax.plot(best_F, marker="o")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best f(x)")
    ax.set_yscale("log")
    ax.grid()
    fig.tight_layout()
    fig.savefig(out_path / "plot_f.png")
    # plt.show()
    plt.close(fig)


def plot_cmaes(show=True):
    out_path = Path(__file__).parent / "out"

    class Params(OptimParams):
        p1 = param.Number(1, bounds=(0, 1), doc="Parameter 1")
        p2 = param.Number(1, bounds=(0.9, 1.1), doc="Parameter 2")

    simulation_params = SimulationParams()
    optim_params = Params()

    # Show predictions
    target_params = SimulationParams.load_from(out_path / "target")
    best_X = np.load(out_path / "best_cma.npy", allow_pickle=True)
    target = np.loadtxt(out_path / "target/result.txt")

    optim_params.assign(best_X)
    pprint(target_params.to_dict())
    print("CMA-ES prediction", optim_params.to_dict())

    # Plot model result with best params
    simulation_params.save_with(out_path / "verif", optim_params)
    best_result = fake_worker(simulation_params.out_dir)

    fig, ax = plt.subplots()
    ax.plot(target)
    ax.plot(best_result, marker="o")
    fig.tight_layout()
    fig.savefig(simulation_params.out_dir / "plot.png")
    if show:
        plt.show()
    plt.close(fig)


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    run_cmaes()
    plot_cmaes()
