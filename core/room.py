from shapely.geometry import Polygon
from core.furniture import Furniture
from typing import List, Tuple

class Room:
    def __init__(self, width: float, height: float, config=None):
        self.width = width
        self.height = height
        self.config = config or {}
        self.furniture: List[Furniture] = []
        self.room_polygon = Polygon([(0, 0), (width, 0), (width, height), (0, height)])

        self.doors = []
        for d in self.config.get("doors", []):
            x, y, w, h = d
            poly = Polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])
            self.doors.append(((x, y, w, h), poly))

        self.windows = []
        for w in self.config.get("windows", []):
            x, y, ww, wh = w
            poly = Polygon([(x, y), (x + ww, y), (x + ww, y + wh), (x, y + wh)])
            self.windows.append(((x, y, ww, wh), poly))

    def is_within_bounds(self, furniture: Furniture) -> bool:
        return self.room_polygon.contains(furniture.polygon)

    def expand_to_fit(self, min_width: float, min_height: float):
        while min_width > self.width or min_height > self.height:
            self.width += 1
            self.height += 1
            print(f"⚠️ Room expanded to {self.width}x{self.height}")

    def get_wall_segments(self) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        return [
            ((0, 0), (self.width, 0)),
            ((self.width, 0), (self.width, self.height)),
            ((self.width, self.height), (0, self.height)),
            ((0, self.height), (0, 0))
        ]
