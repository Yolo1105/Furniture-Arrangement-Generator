from core.furniture import Furniture
from typing import List
from rules.relation_rules import get_relation_rule
from shapely.geometry import Point
import math

def euclidean(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def must_be_near_reward(f: Furniture, others: List[Furniture]) -> float:
    rule = get_relation_rule(f.type)
    targets = rule.get("must_near", [])
    fx, fy = f.x + f.width / 2, f.y + f.height / 2
    min_dist = float('inf')

    for o in others:
        if o.id != f.id and o.type in targets:
            ox, oy = o.x + o.width / 2, o.y + o.height / 2
            dist = euclidean((fx, fy), (ox, oy))
            if dist < min_dist:
                min_dist = dist

    if min_dist < 1.5:
        return max(0.0, 1.0 - min_dist / 1.5)
    return 0.0

def must_face_reward(f: Furniture, others: List[Furniture]) -> float:
    rule = get_relation_rule(f.type)
    facing = rule.get("facing", None)
    if not facing: return 0.0
    target_type = facing.get("type")

    for o in others:
        if o.type == target_type:
            dx = (o.x + o.width / 2) - (f.x + f.width / 2)
            dy = (o.y + o.height / 2) - (f.y + f.height / 2)
            angle = math.atan2(dy, dx) * 180 / math.pi
            diff = abs(angle - f.rotation)
            if diff < facing.get("threshold", 30):
                return 1.0
    return 0.0
