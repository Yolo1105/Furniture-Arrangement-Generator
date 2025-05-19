import math
from typing import Tuple

def rotate_point(x: float, y: float, cx: float, cy: float, angle_deg: float) -> Tuple[float, float]:
    """Rotate a point (x, y) around center (cx, cy) by angle in degrees."""
    angle_rad = math.radians(angle_deg)
    dx, dy = x - cx, y - cy
    qx = cx + math.cos(angle_rad) * dx - math.sin(angle_rad) * dy
    qy = cy + math.sin(angle_rad) * dx + math.cos(angle_rad) * dy
    return qx, qy

def get_rotated_bbox(x: float, y: float, w: float, h: float, angle: float) -> Tuple[float, float]:
    """Get bounding box after rotation. Assumes axis-aligned angle (0, 90, 180, 270)."""
    if int(angle) % 180 == 90:
        return h, w
    return w, h

def iou(boxA, boxB) -> float:
    """Compute the Intersection-over-Union of two axis-aligned boxes."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    inter_area = max(0, xB - xA) * max(0, yB - yA)
    if inter_area == 0:
        return 0.0
    boxA_area = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxB_area = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    return inter_area / float(boxA_area + boxB_area - inter_area)
