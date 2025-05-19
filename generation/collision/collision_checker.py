from shapely.geometry import Polygon
from core.furniture import Furniture
from core.room import Room
from generation.collision.relation_rules import must_be_near, must_face
from rules.relation_rules import must_be_near as rule_requires_near
from rules.relation_rules import should_face as rule_requires_face

def check_overlap(f1: Furniture, f2: Furniture) -> bool:
    """Return True if f1 and f2 overlap after rotation."""
    return f1.polygon.intersects(f2.polygon)

def check_within_room(f: Furniture, room: Room) -> bool:
    """Check whether a furniture polygon is completely inside the room."""
    return room.room_polygon.contains(f.polygon)

def check_clearance(f: Furniture, others: list, buffer: float = None) -> bool:
    """
    Check whether furniture f has enough clearance from other furniture.
    Uses either per-furniture clearance or overridden buffer value.
    """
    clearance = buffer if buffer is not None else f.clearance
    buffered_poly = f.polygon.buffer(clearance)
    for other in others:
        if other.id != f.id and buffered_poly.intersects(other.polygon):
            return False
    return True

def check_all_rules(f: Furniture, others: list, room: Room) -> bool:
    """
    Check all physical and semantic constraints:
    - inside room
    - no collision
    - respects clearance
    - must be near certain types (from rule)
    - must face certain types (from rule)
    """
    # 1. 在房间内
    if not check_within_room(f, room):
        return False

    # 2. 不重叠
    if not check_clearance(f, others, buffer=None):
        return False

    # 3. 靠近关系（仅当规则中要求）
    for other in others:
        if rule_requires_near(f.type, other.type):
            if not must_be_near(f, others, other.type):
                return False

    # 4. 朝向关系（仅当规则中要求）
    for other in others:
        facing_rule = rule_requires_face(f.type, other.type)
        if facing_rule and not must_face(f, others, other.type):
            return False

    return True