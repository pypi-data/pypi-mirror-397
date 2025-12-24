import dataclasses
import os
from collections.abc import Iterator
from typing import Literal

import healpy as hp
import numpy as np

from ._pkdgrav import Simulation, steps


class NpyLoader:
    def __init__(self, sim: Simulation, path: str | os.PathLike[str]) -> None:
        self.path = path
        self.outname = sim.outname

    def __call__(self, step: int) -> np.ndarray:
        tag = "lightcone" if step > 1 else "incomplete"
        path = os.path.join(self.path, f"{self.outname}.{step:05d}.{tag}.npy")
        return np.load(path)


class ParquetLoader:
    read_parquet = None

    @classmethod
    def load(cls, path: str | os.PathLike[str]) -> np.ndarray:
        if cls.read_parquet is None:
            try:
                from pandas import read_parquet
            except ModuleNotFoundError as exc:
                raise ValueError("parquet format requires pandas") from exc
            else:
                cls.read_parquet = read_parquet
        return cls.read_parquet(path).to_numpy().reshape(-1)

    def __init__(self, sim: Simulation, path: str | os.PathLike[str]) -> None:
        self.path = path
        self.outname = sim.outname
        self.nside = sim.nside

    def __call__(self, step: int) -> np.ndarray:
        path = os.path.join(self.path, f"particles_{step}_{self.nside}.parquet")
        return self.load(path)


def read_gowerst(
    sim: Simulation,
    path: str | os.PathLike[str] | None = None,
    format: Literal["npy", "parquet"] = "npy",
    *,
    zmax: float | None = None,
    nside: int | None = None,
    raw: bool = False,
) -> Iterator[np.ndarray]:
    """Read simulation in GowerSt format."""

    path = os.path.expanduser(path) if path is not None else sim.dir

    if format == "npy":
        loader = NpyLoader(sim, path)
    elif format == "parquet":
        loader = ParquetLoader(sim, path)
    else:
        raise ValueError(f"unknown format: {format}")

    # iterate shells
    for step in steps(sim):
        if zmax is not None and zmax < step.near_redshift:
            break

        data = loader(step.step)

        # number of particles in shell
        particles = data.sum()

        metadata = dataclasses.asdict(step)
        metadata["particles"] = particles

        if nside is not None and nside != hp.get_nside(data):
            # keep the number of particles constant
            data = hp.ud_grade(data, nside, power=-2)
            assert data.sum() == particles, "resampling lost particles!"

        if not raw:
            nbar = step.mean_particles / data.size
            data = data / nbar - 1.0

        # attach metadata
        data = data.view(np.dtype(data.dtype, metadata=metadata))

        yield data
