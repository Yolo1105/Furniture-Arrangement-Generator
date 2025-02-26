# generation/strategies/chair_strategy.py
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
import random
from generation.strategy_registry import register_strategy

@register_strategy(FurnitureType.CHAIR)
class ChairStrategy:
    @staticmethod
    def place(room, existing_items):
        config = ConfigLoader.get_furniture_config(FurnitureType.CHAIR)
        if "default_size" not in config:
            raise KeyError("Chair config missing 'default_size'")
        chair_size = config["default_size"]

        table = next((item for item in existing_items if item.type == FurnitureType.TABLE), None)
        if not table:
            return None  

        positions = [
            (table.x - chair_size[0] - 0.5, table.y + table.height/2),
            (table.x + table.width + 0.5, table.y + table.height/2),
            (table.x + table.width/2, table.y - chair_size[1] - 0.5),
            (table.x + table.width/2, table.y + table.height + 0.5)
        ]

        chairs = []
        for x, y in random.sample(positions, len(positions)):
            chair = Furniture(x, y, *chair_size, FurnitureType.CHAIR)
            if ChairStrategy.check_access_path(chair, table, existing_items):
                chairs.append(chair)

        return chairs if chairs else None

    @staticmethod
    def check_access_path(chair, table, existing_items):
        """确保椅子周围有足够的通道空间"""
        return all(
            chair.polygon.distance(other.polygon) >= 0.8
            for other in existing_items if other != table
        )
