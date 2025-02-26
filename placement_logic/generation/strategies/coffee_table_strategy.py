# generation/strategies/coffee_table_strategy.py
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
from generation.collision.buffer_check import CollisionChecker
import random
from generation.strategy_registry import register_strategy

@register_strategy(FurnitureType.COFFEE_TABLE)
class CoffeeTableStrategy:
    @staticmethod
    def place(room, existing_items):
        config = ConfigLoader.get_furniture_config(FurnitureType.COFFEE_TABLE)
        width, height = config["default_size"]
        sofa_spacing = config.get("sofa_spacing", 0.5)
        margin = config.get("margin", 1.0)

        # Find sofa
        sofa = next((item for item in existing_items if item.type == FurnitureType.SOFA), None)
        if sofa:
            if sofa.width > sofa.height:  # Horizontal sofa
                x = sofa.x + (sofa.width - width) / 2
                y = sofa.y + sofa.height + sofa_spacing
            else:  # Vertical sofa
                x = sofa.x + sofa.width + sofa_spacing
                y = sofa.y + (sofa.height - height) / 2
            
            coffee_table = Furniture(x, y, width, height, FurnitureType.COFFEE_TABLE)
            if not CollisionChecker(existing_items).check_collision(coffee_table):
                return coffee_table

        # Fallback to central area
        x = random.uniform(margin, room.width - width - margin)
        y = random.uniform(margin, room.height - height - margin)
        coffee_table = Furniture(x, y, width, height, FurnitureType.COFFEE_TABLE)
        return coffee_table if room.is_within_bounds(coffee_table) else None