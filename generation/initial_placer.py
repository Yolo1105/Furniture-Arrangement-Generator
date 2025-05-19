from typing import Optional, List
from core.furniture import Furniture, FurnitureType
from core.room import Room
from core.config_loader import ConfigLoader
from generation.collision.buffer_check import CollisionChecker
from generation.factory import FurnitureFactory
import random

class SmartPlacer:
    def __init__(self, room: Room):
        self.room = room
        self.layout: List[Furniture] = []
        self.collision_checker = CollisionChecker(self.layout)
        self.priority_order = [
            FurnitureType.BED, 
            FurnitureType.SOFA,
            FurnitureType.DINING_SET,
            FurnitureType.WARDROBE,
            FurnitureType.DESK,
            FurnitureType.TABLE,
            FurnitureType.TV_STAND,
            FurnitureType.COFFEE_TABLE,
            FurnitureType.BOOKSHELF,
            FurnitureType.SHOE_CABINET,
            FurnitureType.NIGHTSTAND  # Add missing types
        ]
        self.zone_manager = self.ZoneManager(room) if hasattr(room, 'zones') else None

    def place_furniture(self, furniture_type: FurnitureType):
        """Places a piece of furniture ensuring it does not overlap."""
        config = ConfigLoader.get_furniture_config(furniture_type)
        if not config:
            print(f"⚠️ No config found for {furniture_type}, skipping placement.")
            return

        width, height = config.get("default_size", (1.0, 1.0))
        clearance = config.get("clearance", 1.0)  # Ensure minimum spacing
        furniture = FurnitureFactory.create(furniture_type, self.room)

        max_attempts = 100
        shift_step = 0.5  # Small adjustment per attempt

        for _ in range(max_attempts):
            x = random.uniform(clearance, self.room.width - width - clearance)
            y = random.uniform(clearance, self.room.height - height - clearance)

            furniture.x, furniture.y = x, y
            if not self.collision_checker.check_collision(furniture):
                self.layout.append(furniture)
                self.collision_checker.add_item(furniture)
                print(f"✅ Placed {furniture.type} at ({x}, {y})")
                return
            
            # Shift slightly and retry
            for dx in [-shift_step, 0, shift_step]:
                for dy in [-shift_step, 0, shift_step]:
                    adjusted_x = x + dx
                    adjusted_y = y + dy

                    if 0 <= adjusted_x <= self.room.width - width and 0 <= adjusted_y <= self.room.height - height:
                        furniture.x, furniture.y = adjusted_x, adjusted_y
                        if not self.collision_checker.check_collision(furniture):
                            self.layout.append(furniture)
                            self.collision_checker.add_item(furniture)
                            print(f"✅ Adjusted placement: {furniture.type} at ({adjusted_x}, {adjusted_y})")
                            return

        print(f"⚠️ Could not place {furniture_type} after {max_attempts} attempts.")


    def generate_layout(self, furniture_list: List[FurnitureType]) -> List[Furniture]:
        ordered_types = sorted(
            furniture_list,
            key=lambda x: self.priority_order.index(x) if x in self.priority_order else 99
        )

        self._generate_core_furniture(ordered_types)  
        self._generate_related_items()

        # Ensure all remaining items get placed, even if they were not in priority order
        for f_type in furniture_list:
            if f_type not in [f.type for f in self.layout]:  # If not placed, force it
                print(f"⚠️ {f_type} was not placed earlier, forcing placement.")
                self.place_furniture(f_type)

        print(f"🏠 Final furniture count: {len(self.layout)}")
        return self.layout

    def _generate_core_furniture(self, furniture_types: List[FurnitureType]):
        """Ensures key furniture pieces are placed first (e.g., bed, sofa)."""
        for f_type in furniture_types:
            if f_type in self.priority_order[:3]:  # Prioritize first 3 items
                self.place_furniture(f_type)

    def _generate_related_items(self):
        """Ensure required furniture is placed before dependent furniture."""
        for f in self.layout:
            related_items = f.must_near if f.must_near else []

            if isinstance(related_items, FurnitureType):
                related_items = [related_items]

            for rel_type in related_items:
                if rel_type not in [f.type for f in self.layout]:
                    print(f"⚠️ {f.type} requires {rel_type}, but it's missing. Placing anyway.")
                    self.place_furniture(rel_type)  # Place missing dependent furniture

    def _fill_remaining_items(self, furniture_types):
        """Fill remaining items in the layout."""
        for f_type in furniture_types:
            if f_type in self.priority_order:
                continue
            
            if self.zone_manager:
                zone_type = self.zone_manager.get_placement_zone(f_type)
                if zone_type:
                    zone = self._select_zone(zone_type)
                    if zone:
                        item = self._place_in_zone(f_type, zone)
                        self._safe_add(item)
                        continue
            
            # Default placement if no zone
            item = FurnitureFactory.create(f_type, self.room)
            self._safe_add(item)

    class ZoneManager:
        def __init__(self, room: Room):
            self.room = room
            self._init_zone_mapping()
        
        def _init_zone_mapping(self):
            self.type_to_zone = {
                FurnitureType.BED: 'bedroom',
                FurnitureType.WARDROBE: 'bedroom',
                FurnitureType.SOFA: 'living_room',
                FurnitureType.TV_STAND: 'living_room',
                FurnitureType.COFFEE_TABLE: 'living_room',
                FurnitureType.TABLE: 'dining',
                FurnitureType.DINING_SET: 'dining',
                FurnitureType.DESK: 'study',
                FurnitureType.BOOKSHELF: 'study',
                FurnitureType.SHOE_CABINET: 'entrance'
            }
        
        def get_placement_zone(self, f_type: FurnitureType) -> Optional[str]:
            return self.type_to_zone.get(f_type)

    def _select_zone(self, zone_type: str) -> Optional[dict]:
        """Select an available zone based on type."""
        if not hasattr(self.room, 'zones'):
            return None
        zones = [z for z in self.room.zones if z['type'] == zone_type]
        return random.choice(zones) if zones else None

    def _place_in_zone(self, f_type: FurnitureType, zone: dict) -> Optional[Furniture]:
        """Place furniture within a specified zone, or fallback if zone is missing."""
        config = ConfigLoader.get_furniture_config(f_type)
        if not config:
            return None

        width, height = config["default_size"]
        
        # If no valid zone, allow placement anywhere in the room
        if not zone:
            x = random.uniform(0, self.room.width - width)
            y = random.uniform(0, self.room.height - height)
        else:
            x = random.uniform(max(zone['x1'], 0), min(zone['x2'] - width, self.room.width - width))
            y = random.uniform(max(zone['y1'], 0), min(zone['y2'] - height, self.room.height - height))

        return Furniture(x, y, width, height, f_type)

    def _safe_add(self, item: Optional[Furniture]) -> bool:
        """Safely adds furniture, checking boundaries and collisions."""
        if not item or not self.room.is_within_bounds(item):
            return False
        if self.collision_checker.check_collision(item):
            return False
        self.layout.append(item)
        self.collision_checker.add_item(item)
        return True
