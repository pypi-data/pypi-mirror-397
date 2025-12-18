"""Shared type aliases used throughout the bounded number utilities."""

from typing import Union
from enum import Enum, auto
RealNumber = Union[int, float]

class BoundType(Enum):
    """Available strategies for constraining integer values."""

    CLAMP = auto()
    CYCLIC = auto()
    BOUNCE = auto()
    MODULO = auto()  # pure 0..n-1 modular arithmetic
    IGNORE = auto()  # no bounding applied