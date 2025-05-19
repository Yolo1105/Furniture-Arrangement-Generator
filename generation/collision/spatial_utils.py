from typing import Tuple
import numpy as np

def get_aabb(polygon) -> Tuple[float, float, float, float]:
    """Return axis-aligned bounding box of a shapely polygon."""
    return polygon.bounds  # (minx, miny, maxx, maxy)

def compute_center(polygon) -> Tuple[float, float]:
    """Compute the geometric center of a polygon."""
    return polygon.centroid.x, polygon.centroid.y

def grid_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
    """Compute L1 (grid) distance between two grid cells."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def overlap_area(p1, p2) -> float:
    """Return intersection area between two shapely polygons."""
    return p1.intersection(p2).area
