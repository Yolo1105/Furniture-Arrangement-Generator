# generation/strategies/nightstand_strategy.py
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
from generation.collision.buffer_check import CollisionChecker
import random
from generation.strategy_registry import register_strategy

@register_strategy(FurnitureType.NIGHTSTAND)
class NightstandStrategy:
    @staticmethod
    def place(room, existing_items):
        config = ConfigLoader.get_furniture_config(FurnitureType.NIGHTSTAND)
        width, height = config["default_size"]
        base_offset = config.get("offset", 2.0)
        margin = config.get("margin", 1.0)

        # Find bed
        bed = next((item for item in existing_items if item.type == FurnitureType.BED), None)
        if bed:
            offset = base_offset + random.uniform(-0.3, 0.3)
            side = random.choice(["left", "right"])
            
            if side == "left":
                x = bed.x - width - offset
            else:
                x = bed.x + bed.width + offset
            
            y = bed.y + (bed.height - height) / 2
            nightstand = Furniture(x, y, width, height, FurnitureType.NIGHTSTAND)
            
            if room.is_within_bounds(nightstand) and not CollisionChecker(existing_items).check_collision(nightstand):
                return nightstand

        # Fallback random placement
        x = random.uniform(margin, room.width - width - margin)
        y = random.uniform(margin, room.height - height - margin)
        return Furniture(x, y, width, height, FurnitureType.NIGHTSTAND)