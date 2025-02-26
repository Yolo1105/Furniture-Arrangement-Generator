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
            FurnitureType.SHOE_CABINET
        ]
        self.zone_manager = self.ZoneManager(room) if hasattr(room, 'zones') else None

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

    def generate_layout(self, furniture_list: List[FurnitureType]) -> List[Furniture]:
        ordered_types = sorted(
            furniture_list,
            key=lambda x: self.priority_order.index(x) if x in self.priority_order else 99
        )
        
        self._generate_core_furniture(ordered_types)
        self._generate_related_items()
        self._fill_remaining_items(ordered_types)
        return self.layout

    def _select_zone(self, zone_type: str) -> Optional[dict]:
        """根据区域类型选择可用区域"""
        if not hasattr(self.room, 'zones'):
            return None
        zones = [z for z in self.room.zones if z['type'] == zone_type]
        return random.choice(zones) if zones else None

    def _fill_remaining_items(self, furniture_types):
        """填充剩余家具，优先使用区域管理"""
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
            
            # 无区域则通用生成
            item = FurnitureFactory.create(f_type, self.room)
            self._safe_add(item)

    def _place_in_zone(self, f_type: FurnitureType, zone: dict) -> Optional[Furniture]:
        """在指定区域内生成家具"""
        config = ConfigLoader.get_furniture_config(f_type)
        if not config:
            return None
        
        width, height = config["default_size"]
        x = random.uniform(max(zone['x1'], 0), min(zone['x2'] - width, self.room.width - width))
        y = random.uniform(max(zone['y1'], 0), min(zone['y2'] - height, self.room.height - height))
        return Furniture(x, y, width, height, f_type)

    def _safe_add(self, item: Optional[Furniture]) -> bool:
        """安全添加家具（边界+碰撞检测）"""
        if not item or not self.room.is_within_bounds(item):
            return False
        if self.collision_checker.check_collision(item):
            return False
        self.layout.append(item)
        self.collision_checker.add_item(item)
        return True