# generation/strategies/desk_strategy.py
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
from generation.collision.buffer_check import CollisionChecker
import random
from generation.strategy_registry import register_strategy

@register_strategy(FurnitureType.DESK)
class DeskStrategy:
    @staticmethod
    def place(room, existing_items):
        config = ConfigLoader.get_furniture_config(FurnitureType.DESK)
        width, height = config["default_size"]
        margin = config.get("margin", 1.0)

        # Check study zone
        if hasattr(room, "zones"):
            study_zones = [z for z in room.zones if z['type'] == 'study']
            if study_zones:
                zone = random.choice(study_zones)
                x = random.uniform(zone['x1'], zone['x2'] - width)
                y = random.uniform(zone['y1'], zone['y2'] - height)
                desk = Furniture(x, y, width, height, FurnitureType.DESK)
                if not CollisionChecker(existing_items).check_collision(desk):
                    return desk

        # Try window alignment
        windows = room.config.get("windows", [])
        if windows:
            win = random.choice(windows)
            x = win[0] + (win[2] - width)/2
            y = win[1] - height - 0.5  # Below window
            
            if y < 0:
                y = win[1] + win[3] + 0.5  # Above window
            
            desk = Furniture(x, y, width, height, FurnitureType.DESK)
            if room.is_within_bounds(desk):
                return desk

        # Wall placement
        wall = random.choice(["east", "west"])
        if wall == "east":
            x = room.width - width - margin
        else:
            x = margin
        y = random.uniform(margin, room.height - height - margin)
        
        return Furniture(x, y, width, height, FurnitureType.DESK)