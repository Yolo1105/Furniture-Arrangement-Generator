from typing import List
from core.furniture import Furniture
import math

class ConstraintManager:
    def __init__(self):
        self._constraints = {}
    
    def add_fixed_position(
        self, 
        furniture_id: str, 
        x: float, 
        y: float,
        tolerance: float = 0.1
    ) -> None:
        """添加固定位置约束：允许坐标在 [x±tolerance, y±tolerance] 范围内"""
        self._constraints[furniture_id] = {
            "type": "position",
            "x": (x - tolerance, x + tolerance),
            "y": (y - tolerance, y + tolerance)
        }
    
    def add_relative_position(
        self,
        anchor_id: str,
        target_id: str,
        min_distance: float,
        max_distance: float
    ) -> None:
        """添加相对位置约束：两个家具中心点距离必须在 [min, max] 范围内"""
        constraint_id = f"{anchor_id}-{target_id}"
        self._constraints[constraint_id] = {
            "type": "relative",
            "anchor": anchor_id,
            "target": target_id,
            "min": min_distance,
            "max": max_distance
        }
    
    def validate(self, layout: List[Furniture]) -> bool:
        """验证所有约束是否满足"""
        # 构建家具ID到对象的映射表
        id_to_item = {item.id: item for item in layout}
        
        for constraint_id, constraint in self._constraints.items():
            if constraint["type"] == "position":
                # 固定位置约束验证
                item = id_to_item.get(constraint_id)
                if not item:
                    continue  # 忽略已删除家具的约束
                x_min, x_max = constraint["x"]
                y_min, y_max = constraint["y"]
                if not (x_min <= item.x <= x_max and y_min <= item.y <= y_max):
                    return False
                
            elif constraint["type"] == "relative":
                # 相对位置约束验证
                anchor = id_to_item.get(constraint["anchor"])
                target = id_to_item.get(constraint["target"])
                if not anchor or not target:
                    continue  # 忽略无效家具的约束
                
                # 计算中心点欧氏距离
                dx = anchor.x - target.x
                dy = anchor.y - target.y
                distance = math.hypot(dx, dy)
                
                if not (constraint["min"] <= distance <= constraint["max"]):
                    return False
        
        return True