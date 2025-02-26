# rules/clearance.py
from core.furniture import FurnitureType
from shapely.geometry import Polygon
from dataclasses import dataclass

@dataclass
class ClearanceIssue:
    blocking_id: str
    message: str
    offset_x: float = 0.0
    offset_y: float = 0.0

# 定义各家具之间的最小间距（单位：米）
CLEARANCE_RULES = {
    FurnitureType.BED: {
        "wall": 0.6,
        "door": 1.5,
        FurnitureType.WARDROBE: 1.0
    },
    FurnitureType.SOFA: {
        "walkway": 1.0,
        FurnitureType.COFFEE_TABLE: 0.5  # 40-60cm取中值0.5m
    },
    FurnitureType.TABLE: {
        "walkway": 0.8,
        FurnitureType.CHAIR: 0.75
    },
    FurnitureType.WARDROBE: {
        "door": 0.6
    },
    FurnitureType.TV_STAND: {
        FurnitureType.SOFA: 0.0  # 通过位置规则控制观影距离
    },
    FurnitureType.DESK: {
        FurnitureType.CHAIR: 0.7
    },
    FurnitureType.BOOKSHELF: {
        "reading_area": 0.5
    },
    FurnitureType.SHOE_CABINET: {
        "entrance": 0.5
    },
    FurnitureType.COFFEE_TABLE: {
        FurnitureType.SOFA: 0.4
    },
    FurnitureType.CHAIR: {
        FurnitureType.TABLE: 0.75,
        "back": 0.5
    }
}

def check_all_clearances(layout, room):
    """综合间距检查，包括门/窗缓冲区和家具之间间距"""
    violations = []
    
    # 门/窗缓冲区
    door_zones = []
    for door in getattr(room, 'doors', []):
        if isinstance(door, (list, tuple)) and len(door) >= 4:
            x, y, w, h = door
            door_zone = Polygon([
                (x-1.2, y-1.2), (x+w+1.2, y-1.2),
                (x+w+1.2, y+h+1.2), (x-1.2, y+h+1.2)
            ])
            door_zones.append(door_zone)

    for item in layout:
        # 床头避免正对门窗
        if item.type == FurnitureType.BED:
            if any(zone.contains(item.polygon) for zone in door_zones):
                violations.append(ClearanceIssue(
                    blocking_id=item.id,
                    message=f"床{item.id}距离门窗太近",
                    offset_x=0.5,  # 建议向右移动
                    offset_y=0.0
                ))
        
        # 家具间间距检查
        for other in layout:
            if item != other:
                min_dist = CLEARANCE_RULES.get(item.type, {}).get(other.type, 0.3)
                if item.polygon.distance(other.polygon) < min_dist:
                    # 计算移动建议
                    dx = item.x - other.x
                    dy = item.y - other.y
                    dist = (dx**2 + dy**2)**0.5 or 1
                    move_dist = min_dist - item.polygon.distance(other.polygon)
                    
                    violations.append(ClearanceIssue(
                        blocking_id=item.id,
                        message=f"{item.type}{item.id}与{other.type}{other.id}间距不足",
                        offset_x=(dx/dist) * move_dist,
                        offset_y=(dy/dist) * move_dist
                    ))
    
    return violations

def ensure_door_clearance(layout, room):
    """确保门前通道畅通"""
    modified_layout = list(layout)
    
    # 创建门前区域
    door_areas = []
    for door in getattr(room, 'doors', []):
        if isinstance(door, (list, tuple)) and len(door) >= 4:
            x, y, w, h = door
            # 创建门前1.2米区域
            door_area = Polygon([
                (x-0.3, y-1.2), (x+w+0.3, y-1.2),
                (x+w+0.3, y+h+1.2), (x-0.3, y+h+1.2)
            ])
            door_areas.append(door_area)
    
    # 检查并调整
    for index, item in enumerate(layout):
        for area in door_areas:
            if item.polygon.intersects(area):
                # 计算移动方向和距离
                centroid_item = item.polygon.centroid
                centroid_door = area.centroid
                
                dx = centroid_item.x - centroid_door.x
                dy = centroid_item.y - centroid_door.y
                
                # 归一化方向向量
                dist = (dx**2 + dy**2)**0.5 or 1
                dx, dy = dx/dist, dy/dist
                
                # 移动家具，直到不再与门区域相交
                move_dist = 0.3
                original_x, original_y = item.x, item.y
                
                while item.polygon.intersects(area) and move_dist < 2.0:
                    item.x = original_x + dx * move_dist
                    item.y = original_y + dy * move_dist
                    move_dist += 0.3
                
                # 如果还是相交，考虑删除该家具
                if item.polygon.intersects(area):
                    item.x, item.y = original_x, original_y
                    modified_layout.remove(item)
                    break
    
    return modified_layout

def check_human_ergonomics(layout):
    """检查家具间人体工学距离"""
    issues = []
    
    for i, item1 in enumerate(layout):
        for j, item2 in enumerate(layout):
            if i >= j:  # 避免重复检查
                continue
                
            # 获取这对家具之间的最小间距规则
            min_dist = max(
                CLEARANCE_RULES.get(item1.type, {}).get(item2.type, 0),
                CLEARANCE_RULES.get(item2.type, {}).get(item1.type, 0),
                0.6  # 默认最小通道宽度
            )
            
            # 检查实际距离
            actual_dist = item1.polygon.distance(item2.polygon)
            if actual_dist < min_dist:
                issues.append((item1, item2, min_dist - actual_dist))
    
    return issues
