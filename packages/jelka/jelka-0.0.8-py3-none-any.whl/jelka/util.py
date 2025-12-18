from typing import Tuple, Union

from .types import Position


def length(position: Union[Position, Tuple[float, float, float]]) -> float:
    """Calculates an absolute value of a point."""
    return Position(*position).magnitude()


def distance(p1: Union[Position, Tuple[float, float, float]], p2: Union[Position, Tuple[float, float, float]]) -> float:
    """Calculates a distance between two points."""
    return (Position(*p1) - Position(*p2)).magnitude()
