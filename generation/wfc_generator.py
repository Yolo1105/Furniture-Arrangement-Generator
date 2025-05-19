from typing import List, Tuple
import numpy as np
from constants import ROOM_WIDTH, ROOM_HEIGHT, GRID_SIZE, DOOR_ZONE, FurnitureSpec

def generate_candidate_positions(spec: FurnitureSpec) -> List[Tuple[float, float]]:
    """
    为单个家具生成所有合法候选放置位置（左下角坐标）。
    """
    candidates = []
    for x in np.arange(0, ROOM_WIDTH - spec.width + 0.01, GRID_SIZE):
        for y in np.arange(0, ROOM_HEIGHT - spec.height + 0.01, GRID_SIZE):
            # 规则：必须贴墙
            near_wall = (
                abs(x) < 0.1 or
                abs(x + spec.width - ROOM_WIDTH) < 0.1 or
                abs(y) < 0.1 or
                abs(y + spec.height - ROOM_HEIGHT) < 0.1
            )
            if spec.must_touch_wall and not near_wall:
                continue

            # 规则：避免门区
            door_x, door_y, door_w, door_h = DOOR_ZONE
            in_door_zone = (
                x < door_x + door_w and
                x + spec.width > door_x and
                y < door_y + door_h and
                y + spec.height > door_y
            )
            if spec.avoid_door_zone and in_door_zone:
                continue

            candidates.append((round(x, 2), round(y, 2)))
    return candidates


def generate_all_candidates(furniture_list: List[FurnitureSpec]) -> dict:
    """
    为所有家具生成候选放置点。
    返回 dict: {name -> [(x, y), ...]}
    """
    return {spec.name: generate_candidate_positions(spec) for spec in furniture_list}
