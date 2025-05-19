# generation/strategies/dining_set_strategy.py
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
from generation.collision.buffer_check import CollisionChecker
import random
import math

class DiningSetStrategy:
    @staticmethod
    def place(room, existing_items):
        config = ConfigLoader.get_furniture_config(FurnitureType.DINING_SET)
        table_width, table_height = config["default_size"]
        chair_count = config.get("chair_count", 4)
        chair_size = config.get("chair_size", (6, 6))
        chair_distance = config.get("chair_distance", 10)

        # Place table
        table = Furniture(
            (room.width - table_width)/2,
            (room.height - table_height)/2,
            table_width,
            table_height,
            FurnitureType.TABLE
        )
        if CollisionChecker(existing_items).check_collision(table):
            return None

        # Generate chairs
        chairs = []
        for i in range(chair_count):
            angle = math.radians(i * (360 / chair_count))
            dx = chair_distance * math.cos(angle)
            dy = chair_distance * math.sin(angle)
            
            chair = Furniture(
                table.x + table_width/2 + dx - chair_size[0]/2,
                table.y + table_height/2 + dy - chair_size[1]/2,
                chair_size[0],
                chair_size[1],
                FurnitureType.CHAIR,
                rotation=math.degrees(angle)
            )
            if not CollisionChecker(existing_items + [table] + chairs).check_collision(chair):
                chairs.append(chair)

        return [table] + chairs