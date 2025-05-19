from typing import List

class FurnitureModule:
    def __init__(self, name: str, width: float, height: float, connect_points: List[str]):
        self.name = name
        self.width = width
        self.height = height
        self.connect_points = connect_points  # e.g. ["left", "top"]

class ModularFurniture:
    def __init__(self, modules: List[FurnitureModule]):
        self.modules = modules

    def total_size(self):
        total_width = sum(m.width for m in self.modules)
        total_height = max(m.height for m in self.modules)
        return total_width, total_height
