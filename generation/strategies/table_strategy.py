# generation/strategies/table_strategy.py
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
from generation.collision.buffer_check import CollisionChecker
from shapely.strtree import STRtree
import random

class TableStrategy:
    @staticmethod
    def place(room, existing_items):
        config = ConfigLoader.get_furniture_config(FurnitureType.TABLE)
        size = config["default_size"][0]
        margin = config.get("margin", 2.0)

        # Use spatial index for collision detection
        existing_polys = [item.polygon for item in existing_items]
        tree = STRtree(existing_polys)
        
        for _ in range(10):
            x = random.uniform(margin, room.width - size - margin)
            y = random.uniform(margin, room.height - size - margin)
            temp_table = Furniture(x, y, size, size, FurnitureType.TABLE)
            
            # Fast collision check
            if not any(tree.query(temp_table.polygon)):
                return temp_table
        
        # Fallback to center
        return Furniture(room.width/2 - size/2, room.height/2 - size/2, size, size, FurnitureType.TABLE)