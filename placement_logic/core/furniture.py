from shapely.geometry import Polygon
from shapely.affinity import rotate
from enum import Enum

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

class Furniture:
    def __init__(self, x: float, y: float, width: float, height: float, f_type: str, rotation: float = 0):
        """
        :param rotation: 旋转角度（0-360度，默认0度）
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = FurnitureType(f_type.lower())
        self.rotation = rotation
        # 保存初始（未旋转）的多边形
        self._base_polygon = self._create_polygon()
        self.clearance = self._get_default_clearance()
        self.must_near = None

    def _create_polygon(self) -> Polygon:
        """创建初始多边形（未旋转状态）"""
        return Polygon([
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height)
        ])

    def _get_default_clearance(self) -> float:
        """获取家具的默认安全间距，根据家具类型返回相应的值"""
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
        """获取带安全间距的多边形"""
        return self.polygon.buffer(self.clearance)

    @property
    def polygon(self) -> Polygon:
        """
        动态返回旋转后的多边形，
        旋转中心为家具的中心 (x + width/2, y + height/2)
        """
        center = (self.x + self.width/2, self.y + self.height/2)
        return rotate(self._base_polygon, self.rotation, origin=center)

    def move_by(self, dx: float, dy: float):
        """
        基于位移量移动家具，并更新基础多边形。
        不改变旋转角度。
        """
        self.x += dx
        self.y += dy
        self._base_polygon = self._create_polygon()

    def set_position(self, new_x: float, new_y: float):
        """
        将家具直接移动到新坐标，并更新基础多边形。
        """
        self.x = new_x
        self.y = new_y
        self._base_polygon = self._create_polygon()

    def rotate(self, angle: float):
        """
        更新家具的旋转角度，不修改原始位置数据。
        旋转后的多边形由 polygon 属性动态计算。
        """
        self.rotation = angle % 360

# 以下是各家具类型的子类，各自重写了 _get_default_clearance 和设置了 must_near 属性

class Bed(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = FurnitureType.WARDROBE

    def _get_default_clearance(self) -> float:
        return 1.5

class Sofa(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = FurnitureType.COFFEE_TABLE

    def _get_default_clearance(self) -> float:
        return 1.0

class Table(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = FurnitureType.CHAIR

    def _get_default_clearance(self) -> float:
        return 0.7

class Chair(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = FurnitureType.DESK

    def _get_default_clearance(self) -> float:
        return 0.5

class Wardrobe(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = FurnitureType.BED

    def _get_default_clearance(self) -> float:
        return 0.8

class TvStand(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = FurnitureType.SOFA

    def _get_default_clearance(self) -> float:
        return 1.2

class CoffeeTable(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = FurnitureType.SOFA

    def _get_default_clearance(self) -> float:
        return 0.6

class Bookshelf(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = None  # 无强制关联

    def _get_default_clearance(self) -> float:
        return 0.4

class Desk(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = FurnitureType.CHAIR

    def _get_default_clearance(self) -> float:
        return 0.7

class ShoeCabinet(Furniture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_near = None  # 通常靠近入口

    def _get_default_clearance(self) -> float:
        return 0.3
