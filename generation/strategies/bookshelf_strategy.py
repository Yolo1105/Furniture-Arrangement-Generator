# generation/strategies/bookshelf_strategy.py
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
import random
from generation.strategy_registry import register_strategy

@register_strategy(FurnitureType.BOOKSHELF)
class BookshelfStrategy:
    @staticmethod
    def place(room, existing_items):
        """
        书架策略：
        1. 必须贴墙放置
        2. 需要避开窗户和门
        3. 不能与已有家具重叠
        """
        config = ConfigLoader.get_furniture_config(FurnitureType.BOOKSHELF)
        width, height = config["default_size"]
        windows = room.config.get("windows", [])
        doors = room.config.get("doors", [])

        # 找到可用的墙面
        walls = ["north", "south", "east", "west"]
        available_walls = []
        for wall in walls:
            if not any(
                (w[1] == 0 and wall == "south") or 
                (w[1] + w[3] == room.height and wall == "north") or
                (w[0] + w[2] == room.width and wall == "east") or
                (w[0] == 0 and wall == "west") for w in windows
            ):
                available_walls.append(wall)

        def is_too_close_to_door(x, y):
            """检查书架是否太靠近门"""
            for door in doors:
                door_x, door_y, door_w, door_h = door
                door_center_x = door_x + door_w / 2
                door_center_y = door_y + door_h / 2
                if abs(x + width / 2 - door_center_x) < 2.0 or abs(y + height / 2 - door_center_y) < 2.0:
                    return True
            return False

        # **选择一面可用墙，并尝试 5 次，远离门**
        for _ in range(5):
            if not available_walls:
                return None  # 没有合适的位置，放弃放置
            
            wall_choice = random.choice(available_walls)
            margin = 1.0
            if wall_choice == "north":
                x = random.uniform(margin, room.width - width - margin)
                y = room.height - height - margin
            elif wall_choice == "south":
                x = random.uniform(margin, room.width - width - margin)
                y = margin
            elif wall_choice == "east":
                x = room.width - width - margin
                y = random.uniform(margin, room.height - height - margin)
            else:  # west
                x = margin
                y = random.uniform(margin, room.height - height - margin)

            if not is_too_close_to_door(x, y):
                return Furniture(x, y, width, height, FurnitureType.BOOKSHELF)

        return None  # 没有找到合适的地方

