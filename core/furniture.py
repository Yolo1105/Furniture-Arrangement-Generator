from shapely.geometry import Polygon
from shapely.affinity import rotate
from enum import Enum
import uuid
from typing import Optional, List
from core.module_defs import FurnitureModule

class FurnitureType(Enum):
    BED = "bed"
    SOFA = "sofa"
    TABLE = "table"
    CHAIR = "chair"
    WARDROBE = "wardrobe"
    TV_STAND = "tv_stand"
    COFFEE_TABLE = "coffee_table"
    BOOKSHELF = "bookshelf"
    DESK = "desk"
    SHOE_CABINET = "shoe_cabinet"
    NIGHTSTAND = "nightstand"
    DINING_SET = "dining_set"

class Furniture:
    def __init__(self, x: float, y: float, width: float, height: float,
                 f_type: FurnitureType, rotation: float = 0, modules: Optional[List[FurnitureModule]] = None):
        self.id = str(uuid.uuid4())
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = f_type
        self.rotation = rotation
        self.modules = modules or []  # 模块化支持
        self._base_polygon = self._create_polygon()
        self.clearance = self._get_default_clearance()
        self.must_near = []

    def _create_polygon(self) -> Polygon:
        return Polygon([
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height)
        ])

    def _get_default_clearance(self) -> float:
        clearance_rules = {
            FurnitureType.BED: 1.5,
            FurnitureType.SOFA: 1.0,
            FurnitureType.WARDROBE: 0.8,
            FurnitureType.TV_STAND: 1.2,
            FurnitureType.DESK: 0.7,
            FurnitureType.CHAIR: 0.5
        }
        return clearance_rules.get(self.type, 0.5)

    def get_buffered_polygon(self) -> Polygon:
        return self.polygon.buffer(self.clearance)

    @property
    def polygon(self) -> Polygon:
        center = (self.x + self.width/2, self.y + self.height/2)
        return rotate(self._base_polygon, self.rotation, origin=center)

    def move_by(self, dx: float, dy: float):
        self.x += dx
        self.y += dy
        self._base_polygon = self._create_polygon()

    def set_position(self, new_x: float, new_y: float):
        self.x = new_x
        self.y = new_y
        self._base_polygon = self._create_polygon()

    def rotate(self, angle: float):
        self.rotation = angle % 360

# 以下是各家具类型的子类，各自重写了 _get_default_clearance 和设置了 must_near 属性

# Ensure must_near is always a list
class Bed(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = [FurnitureType.WARDROBE]

class Sofa(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = [FurnitureType.COFFEE_TABLE]

class Table(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = [FurnitureType.CHAIR]

class Chair(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = [FurnitureType.DESK]

class Wardrobe(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = [FurnitureType.BED]

class TvStand(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = [FurnitureType.SOFA]

class CoffeeTable(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = [FurnitureType.SOFA]

class Bookshelf(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = []

class Desk(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = [FurnitureType.CHAIR]

class ShoeCabinet(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = []
