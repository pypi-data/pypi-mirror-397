import dataclasses
import os
from collections.abc import Iterator

import numpy as np

from ._cosmology import ClassCosmology, SimpleCosmology
from ._parfile import read_par


@dataclasses.dataclass
class Simulation:
    path: str | os.PathLike[str]
    dir: str | os.PathLike[str] | None = None

    parameters: dict[str, object] = dataclasses.field(init=False, repr=False)
    cosmology: dict[str, object] = dataclasses.field(init=False, repr=False)

    outname: str | None = dataclasses.field(init=False, repr=False)
    nside: int | None = dataclasses.field(init=False, repr=False)

    redshifts: np.ndarray = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        self.path = os.path.realpath(os.path.expanduser(self.path))

        if self.dir is None:
            self.dir = os.path.dirname(self.path)

        self.parameters = read_par(self.path)

        if self.parameters.get("bClass", False):
            class_path = self.parameters["achClassFilename"]
            if not os.path.isabs(class_path):
                class_path = os.path.join(self.dir, class_path)
            self.cosmology = ClassCosmology(class_path)
        else:
            self.cosmology = SimpleCosmology(self.parameters)

        self.outname = self.parameters.get("achOutName")
        self.nside = self.parameters.get("nSideHealpix")

        # load redshifts from logfile
        z = np.loadtxt(os.path.join(self.dir, f"{self.outname}.log"), usecols=1)
        if z.shape != (self.parameters["nSteps"] + 1,):
            raise ValueError("inconsistent steps in .par and .log file")

        # replace nearly-zero final redshift by zero
        if np.fabs(z[-1]) < 1e-14:
            z[-1] = 0.0

        # reorder redshifts from latest to earliest
        self.redshifts = z[::-1]


@dataclasses.dataclass
class Step:
    """
    Metadata for simulation steps.
    """

    step: int
    near_redshift: float
    far_redshift: float
    comoving_volume: float
    mean_density: float
    mean_particles: float


def load(path: str | os.PathLike[str]) -> Simulation:
    return Simulation(path)


def steps(sim: Simulation) -> Iterator[Step]:
    """
    Returns an iterator of metadata for each simulation step.
    """

    # pre-compute some simulation properties
    boxsize = sim.parameters["dBoxSize"] / sim.cosmology.h
    density = (sim.parameters["nGrid"] / boxsize) ** 3

    steps = range(sim.parameters["nSteps"], 0, -1)
    redshifts = sim.redshifts
    for step, z_near, z_far in zip(steps, redshifts, redshifts[1:]):
        comoving_volume = sim.cosmology.comoving_volume(z_near, z_far)

        yield Step(
            step=step,
            near_redshift=z_near,
            far_redshift=z_far,
            comoving_volume=comoving_volume,
            mean_density=density,
            mean_particles=density * comoving_volume,
        )
