# generation/strategies/tv_stand_strategy.py
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
from generation.collision.buffer_check import CollisionChecker
import random

class TvStandStrategy:
    @staticmethod
    def place(room, existing_items):
        config = ConfigLoader.get_furniture_config(FurnitureType.TV_STAND)
        width, height = config["default_size"]
        sofa_spacing = config.get("sofa_spacing", 1.0)
        margin = config.get("margin", 1.0)

        # Align with sofa
        sofa = next((item for item in existing_items if item.type == FurnitureType.SOFA), None)
        if sofa:
            if sofa.width > sofa.height:  # Horizontal sofa
                x = sofa.x + (sofa.width - width)/2
                y = sofa.y + sofa.height + sofa_spacing
            else:  # Vertical sofa
                x = sofa.x + sofa.width + sofa_spacing
                y = sofa.y + (sofa.height - height)/2
            
            tv_stand = Furniture(x, y, width, height, FurnitureType.TV_STAND)
            if room.is_within_bounds(tv_stand) and not CollisionChecker(existing_items).check_collision(tv_stand):
                return tv_stand

        # Wall fallback
        walls = ["north", "south", "east", "west"]
        wall = random.choice(walls)
        if wall == "north":
            x = (room.width - width)/2
            y = room.height - height - margin
        elif wall == "south":
            x = (room.width - width)/2
            y = margin
        elif wall == "east":
            x = room.width - width - margin
            y = (room.height - height)/2
        else:
            x = margin
            y = (room.height - height)/2
        
        return Furniture(x, y, width, height, FurnitureType.TV_STAND)