from shapely.geometry import Polygon
from core.furniture import Furniture

class Room:
    def __init__(self, width: float, height: float, config=None):
        """
        初始化房间对象
        坐标系：原点(0,0)位于房间左下角，
        X轴向右延伸，Y轴向上延伸
        """
        self.width = width
        self.height = height
        self.config = config or {}

        # 构建房间多边形，用于精确的边界检测
        self.room_polygon = Polygon([(0, 0), (width, 0), (width, height), (0, height)])

        # 处理门与窗，将其存为 (数据, 多边形) 对
        self.doors = []
        for d in self.config.get("doors", []):
            x, y, w, h = d
            door_poly = Polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])
            self.doors.append(((x, y, w, h), door_poly))
        
        self.windows = []
        for w in self.config.get("windows", []):
            x, y, w_width, w_height = w
            window_poly = Polygon([(x, y), (x + w_width, y), (x + w_width, y + w_height), (x, y + w_height)])
            self.windows.append(((x, y, w_width, w_height), window_poly))

    def is_within_bounds(self, furniture: Furniture) -> bool:
        """
        检查家具是否完全位于房间内部，
        通过判断房间多边形是否完全包含家具的多边形
        """
        return self.room_polygon.contains(furniture.polygon)

    def get_wall_segments(self):
        """
        返回房间四面墙的线段表示，
        用于家具靠墙放置逻辑
        """
        return [
            ((0, 0), (self.width, 0)),                # 下墙
            ((self.width, 0), (self.width, self.height)),  # 右墙
            ((0, self.height), (self.width, self.height)), # 上墙
            ((0, 0), (0, self.height))                # 左墙
        ]
