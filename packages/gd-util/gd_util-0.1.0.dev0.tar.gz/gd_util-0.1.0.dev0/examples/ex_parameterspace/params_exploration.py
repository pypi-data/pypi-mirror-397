import logging
from pathlib import Path
import numpy as np

import param

from g_util.parameterspace import OptimParams, ParameterSpaceExploration, SimulationParams


def main():
    out_path = Path(__file__).parent / "out"

    class Params(OptimParams):
        p1 = param.Number(1, bounds=(0, 1), doc="Parameter 1")
        p2 = param.Number(1, bounds=(0.9, 1.1), doc="Parameter 2")

    simulation_params = SimulationParams()
    optim_params = Params()

    explo = ParameterSpaceExploration(out_path)
    explo.dump_params(simulation_params, optim_params)
    explo.run(worker)
    explo.gather_results()
    explo.plot_results()


def worker(dname: str):
    params = SimulationParams.load_from(dname)
    t = np.linspace(0, 1, 100)  # fake data
    res = params.p1 * np.sin(params.p2 * 2 * np.pi * t)
    np.savetxt(params.out_dir / "result.txt", res)


log = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    main()
