# generation/strategies/wardrobe_strategy.py
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
from generation.collision.buffer_check import CollisionChecker
import random

class WardrobeStrategy:
    @staticmethod
    def place(room, existing_items):
        config = ConfigLoader.get_furniture_config(FurnitureType.WARDROBE)
        width, height = config["default_size"]
        margin = config.get("margin", 1.0)

        # Opposite wall from bed
        bed = next((item for item in existing_items if item.type == FurnitureType.BED), None)
        if bed:
            bed_center = bed.x + bed.width/2
            if bed_center < room.width/2:
                x = room.width - width - margin
            else:
                x = margin
            y = bed.y + (bed.height - height)/2
            
            wardrobe = Furniture(x, y, width, height, FurnitureType.WARDROBE)
            if room.is_within_bounds(wardrobe):
                return wardrobe

        # Random wall placement
        walls = ["north", "south", "east", "west"]
        wall = random.choice(walls)
        if wall == "north":
            x = random.uniform(margin, room.width - width - margin)
            y = room.height - height - margin
        elif wall == "south":
            x = random.uniform(margin, room.width - width - margin)
            y = margin
        elif wall == "east":
            x = room.width - width - margin
            y = random.uniform(margin, room.height - height - margin)
        else:
            x = margin
            y = random.uniform(margin, room.height - height - margin)
        
        return Furniture(x, y, width, height, FurnitureType.WARDROBE)