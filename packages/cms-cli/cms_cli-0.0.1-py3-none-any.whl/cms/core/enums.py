from enum import Enum


class MagDirParameterName(Enum):
    WIND = "wind"
    CURRENT = "current"
    WAVE = "wave"


class ResamplingMethod(Enum):
    NEAREST = "nearest"
    MEAN = "mean"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    COUNT = "count"

    @staticmethod
    def from_string(method: str) -> "ResamplingMethod":
        """Map a string to the corresponding ResamplingMethod enum."""
        try:
            return ResamplingMethod[method.upper()]
        except KeyError:
            valid_methods = ", ".join([m.name.lower() for m in ResamplingMethod])
            raise ValueError(f"Invalid resampling method '{method}'. Choose one of: {valid_methods}")
