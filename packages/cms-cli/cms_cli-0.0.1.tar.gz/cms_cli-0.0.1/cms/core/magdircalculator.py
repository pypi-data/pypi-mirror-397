from abc import ABC, abstractmethod
from typing import Union

import numpy as np
from xarray import DataArray


class MagDirCalculator(ABC):
    def __init__(self, x: Union[DataArray, np.ndarray, float], y: Union[DataArray, np.ndarray, float]):
        self._x = x
        self._y = y

    @abstractmethod
    def get_dir(self) -> Union[DataArray, np.ndarray, float]:
        pass

    @abstractmethod
    def get_mag(self) -> Union[DataArray, np.ndarray, float]:
        pass


class VectorComponentCalculator(MagDirCalculator):
    """Base class for calculating magnitude and direction from orthogonal velocity components."""

    def get_dir(self) -> Union[DataArray, np.ndarray, float]:
        return np.mod(360 + (np.arctan2(self._y, self._x) * 180 / np.pi), 360)

    def get_mag(self) -> Union[DataArray, np.ndarray, float]:
        return np.sqrt(self._x * self._x + self._y * self._y)


class CurrentCalculator(VectorComponentCalculator):
    pass


class WindCalculator(VectorComponentCalculator):
    pass


class WaveCalculator(MagDirCalculator):
    def get_dir(self) -> Union[DataArray, np.ndarray, float]:
        return np.mod(self._y + 180 + 360, 360)

    def get_mag(self) -> Union[DataArray, np.ndarray, float]:
        return self._x
