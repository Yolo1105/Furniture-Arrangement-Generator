from typing import Optional, List
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
from core.room import Room

_strategy_registry = {}

def register_strategy(f_type: FurnitureType):
    """Decorator to associate strategy classes with furniture types."""
    def decorator(cls):
        _strategy_registry[f_type] = cls.place
        return cls
    return decorator

class FurnitureFactory:
    @staticmethod
    def create(f_type: FurnitureType, room: Room, ref_item: Optional[Furniture] = None) -> Optional[Furniture]:
        """Dynamically generates furniture, ensuring placement, and falls back to default layout if needed."""
        config = ConfigLoader.get_furniture_config(f_type)
        if not config:
            raise ValueError(f"Missing configuration for {f_type}")
        
        # Ensure necessary fields exist
        try:
            width, height = config["default_size"]
        except KeyError:
            raise KeyError(f"Config for {f_type} must contain 'default_size'")

        # Ensure sizes are in valid grid units (1.0 or 0.5)
        def snap_to_grid(size):
            return 1.0 if size >= 0.75 else 0.5

        width = snap_to_grid(width)
        height = snap_to_grid(height)

        # Ensure room is large enough to fit this furniture
        if width > room.width or height > room.height:
            print(f"⚠️ {f_type} is too big ({width}x{height}), expanding room...")
            room.expand_to_fit(width, height)  # Dynamically adjust room size

        # Retrieve registered strategy function
        strategy = _strategy_registry.get(f_type)
        if strategy:
            furniture = strategy(room, config, ref_item)
            if furniture:
                return furniture

        # If strategy fails, fall back to default grid placement
        return FurnitureFactory.default_placement(f_type, room, width, height)

    @staticmethod
    def default_placement(f_type: FurnitureType, room: Room, width: float, height: float) -> Furniture:
        """Provides a default placement strategy if dynamic placement fails."""
        print(f"⚠️ Failed to place {f_type}, using default fallback placement.")

        # Place items in a grid pattern from (0,0) onwards
        grid_size = 1  # Step size for placement grid
        x, y = 0, 0
        while any(f.x == x and f.y == y for f in room.layout):
            x += grid_size
            if x + width > room.width:
                x = 0
                y += grid_size
                if y + height > room.height:
                    print(f"⚠️ Not enough space for {f_type}, expanding room.")
                    room.expand_to_fit(x + width, y + height)

        furniture = Furniture(x=x, y=y, width=width, height=height, f_type=f_type)
        room.layout.append(furniture)
        return furniture

# ==========================
# Register All Furniture Strategies
# ==========================

@register_strategy(FurnitureType.BED)
class BedPlacement:
    @staticmethod
    def place(room: Room, config: dict, ref_item: Optional[Furniture] = None) -> Furniture:
        width, height = config["default_size"]
        x = room.width / 2 - width / 2
        y = room.height / 4
        return Furniture(x, y, width, height, FurnitureType.BED)

@register_strategy(FurnitureType.SOFA)
class SofaPlacement:
    @staticmethod
    def place(room: Room, config: dict, ref_item: Optional[Furniture] = None) -> Furniture:
        width, height = config["default_size"]
        x = room.width / 2 - width / 2
        y = room.height - height - 0.5
        return Furniture(x, y, width, height, FurnitureType.SOFA)

@register_strategy(FurnitureType.TABLE)
class TablePlacement:
    @staticmethod
    def place(room: Room, config: dict, ref_item: Optional[Furniture] = None) -> Furniture:
        width, height = config["default_size"]
        x = room.width / 2 - width / 2
        y = room.height / 2 - height / 2
        return Furniture(x, y, width, height, FurnitureType.TABLE)

@register_strategy(FurnitureType.CHAIR)
class ChairPlacement:
    @staticmethod
    def place(room: Room, config: dict, ref_item: Optional[Furniture] = None) -> Furniture:
        width, height = config["default_size"]
        x = room.width / 2 - width / 2
        y = room.height / 2 - height / 2 + 1.0
        return Furniture(x, y, width, height, FurnitureType.CHAIR)

@register_strategy(FurnitureType.WARDROBE)
class WardrobePlacement:
    @staticmethod
    def place(room: Room, config: dict, ref_item: Optional[Furniture] = None) -> Furniture:
        width, height = config["default_size"]
        x = room.width - width - 0.5
        y = 0.5
        return Furniture(x, y, width, height, FurnitureType.WARDROBE)

@register_strategy(FurnitureType.TV_STAND)
class TVStandPlacement:
    @staticmethod
    def place(room: Room, config: dict, ref_item: Optional[Furniture] = None) -> Furniture:
        width, height = config["default_size"]
        x = room.width / 2 - width / 2
        y = 0.5
        return Furniture(x, y, width, height, FurnitureType.TV_STAND)

@register_strategy(FurnitureType.COFFEE_TABLE)
class CoffeeTablePlacement:
    @staticmethod
    def place(room: Room, config: dict, ref_item: Optional[Furniture] = None) -> Furniture:
        width, height = config["default_size"]
        x = room.width / 2 - width / 2
        y = room.height / 2 - height / 2
        return Furniture(x, y, width, height, FurnitureType.COFFEE_TABLE)

@register_strategy(FurnitureType.BOOKSHELF)
class BookshelfPlacement:
    @staticmethod
    def place(room: Room, config: dict, ref_item: Optional[Furniture] = None) -> Furniture:
        width, height = config["default_size"]
        x = 0.5
        y = room.height - height - 0.5
        return Furniture(x, y, width, height, FurnitureType.BOOKSHELF)

@register_strategy(FurnitureType.DESK)
class DeskPlacement:
    @staticmethod
    def place(room: Room, config: dict, ref_item: Optional[Furniture] = None) -> Furniture:
        width, height = config["default_size"]
        x = 0.5
        y = room.height - height - 0.5
        return Furniture(x, y, width, height, FurnitureType.DESK)

@register_strategy(FurnitureType.SHOE_CABINET)
class ShoeCabinetPlacement:
    @staticmethod
    def place(room: Room, config: dict, ref_item: Optional[Furniture] = None) -> Furniture:
        width, height = config["default_size"]
        x = 0.5
        y = 0.5
        return Furniture(x, y, width, height, FurnitureType.SHOE_CABINET)

@register_strategy(FurnitureType.NIGHTSTAND)
class NightstandPlacement:
    @staticmethod
    def place(room: Room, config: dict, ref_item: Optional[Furniture] = None) -> Furniture:
        width, height = config["default_size"]
        x = ref_item.x + ref_item.width + 0.2 if ref_item else 1.0
        y = ref_item.y if ref_item else 1.0
        return Furniture(x, y, width, height, FurnitureType.NIGHTSTAND)

@register_strategy(FurnitureType.DINING_SET)
class DiningSetPlacement:
    @staticmethod
    def place(room: Room, config: dict, ref_item: Optional[Furniture] = None) -> Furniture:
        width, height = config["default_size"]
        x = room.width / 2 - width / 2
        y = room.height / 2 - height / 2
        return Furniture(x, y, width, height, FurnitureType.DINING_SET)
