# generation/strategies/shoe_cabinet_strategy.py
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
import random

class ShoeCabinetStrategy:
    @staticmethod
    def place(room, existing_items):
        config = ConfigLoader.get_furniture_config(FurnitureType.SHOE_CABINET)
        width, height = config["default_size"]
        door_spacing = config.get("door_spacing", 1.0)
        margin = config.get("margin", 0.5)
        doors = room.config.get("doors", [])

        # Prioritize door closest to origin (0,0)
        if doors:
            main_door = min(doors, key=lambda d: d[0]**2 + d[1]**2)
            door_center_x = main_door[0] + main_door[2]/2
            
            if door_center_x < room.width/2:
                x = main_door[0] + main_door[2] + door_spacing
            else:
                x = main_door[0] - width - door_spacing
            
            y = main_door[1] + (main_door[3] - height)/2
            
            # Clamp to room boundaries
            x = max(margin, min(x, room.width - width - margin))
            y = max(margin, min(y, room.height - height - margin))
            
            cabinet = Furniture(x, y, width, height, FurnitureType.SHOE_CABINET)
            if room.is_within_bounds(cabinet):
                return cabinet

        # Fallback to entrance area
        return Furniture(margin, margin, width, height, FurnitureType.SHOE_CABINET)