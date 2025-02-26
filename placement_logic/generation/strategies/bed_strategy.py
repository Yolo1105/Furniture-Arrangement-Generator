# generation/strategies/bed_strategy.py
from core import Furniture, FurnitureType
from core.config_loader import ConfigLoader
import random
from generation.strategy_registry import register_strategy

@register_strategy(FurnitureType.BED)
class BedStrategy:
    @staticmethod
    def place(room, existing_items):
        config = ConfigLoader.get_furniture_config(FurnitureType.BED)
        width, height = config["default_size"]

        # 获取门的位置，避免床正对门
        doors = room.config.get("doors", [])
        min_door_distance = config.get("min_door_distance", 2.0)

        def is_too_close_to_door(x, y):
            """检查床是否太靠近门"""
            for door in doors:
                door_x, door_y, door_w, door_h = door
                door_center_x = door_x + door_w / 2
                door_center_y = door_y + door_h / 2
                if abs(x + width / 2 - door_center_x) < min_door_distance or abs(y + height / 2 - door_center_y) < min_door_distance:
                    return True
            return False

        # **优先在 bedroom 区域放置**
        if hasattr(room, "zones"):
            bedroom_zones = [z for z in room.zones if z['type'] == 'bedroom']
            if bedroom_zones:
                for _ in range(5):
                    zone = random.choice(bedroom_zones)
                    x = random.uniform(max(zone['x1'], 0), min(zone['x2'] - width, room.width - width))
                    y = random.uniform(max(zone['y1'], 0), min(zone['y2'] - height, room.height - height))
                    bed = Furniture(x, y, width, height, FurnitureType.BED)
                    if room.is_within_bounds(bed) and not is_too_close_to_door(x, y):
                        return bed

        # **退而求其次，靠墙放置**
        for _ in range(5):  # 5 次尝试
            x = (room.width - width) / 2
            y = 1.0  # 默认贴南墙
            if not is_too_close_to_door(x, y):
                return Furniture(x, y, width, height, FurnitureType.BED)

        # 兜底策略（如果始终无法远离门）
        return Furniture((room.width - width) / 2, 1.0, width, height, FurnitureType.BED)
