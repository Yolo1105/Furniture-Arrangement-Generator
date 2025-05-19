# rules/relation_rules.py
import math
from typing import List, Dict, Any, Optional, Tuple
from core.furniture import Furniture, FurnitureType
from core.room import Room

# 定义各家具间的关联规则
RELATIONSHIPS = {
    FurnitureType.BED: [
        {"related": FurnitureType.WARDROBE, "min_distance": 0.8, "max_distance": 2.0},
        {"related": FurnitureType.NIGHTSTAND, "side": "both"}
    ],
    FurnitureType.SOFA: [
        {"related": FurnitureType.COFFEE_TABLE, "min_distance": 0.4, "max_distance": 0.6},
        {"related": FurnitureType.TV_STAND, "facing": True}
    ],
    FurnitureType.TABLE: [
        {"related": FurnitureType.CHAIR, "min_distance": 0.75, "max_distance": 0.75}
    ],
    FurnitureType.WARDROBE: [
        {"related": getattr(FurnitureType, 'MIRROR', None), "alignment": True}
    ],
    FurnitureType.TV_STAND: [
        {"related": FurnitureType.SOFA, "distance_multiplier": 3}
    ],
    FurnitureType.DESK: [
        {"related": FurnitureType.CHAIR, "min_distance": 0.7, "max_distance": 0.7}
    ],
    FurnitureType.BOOKSHELF: [
        {"related": "READING_AREA", "proximity": True}  # "READING_AREA"为房间功能区，不一定为家具
    ],
    FurnitureType.SHOE_CABINET: [
        {"related": "ENTRANCE", "proximity": True}
    ],
    FurnitureType.COFFEE_TABLE: [
        {"related": FurnitureType.SOFA, "min_distance": 0.4, "max_distance": 0.6}
    ],
    FurnitureType.CHAIR: [
        {"related": FurnitureType.TABLE, "min_distance": 0.75, "max_distance": 0.75}
    ]
}

# 定义家具组合关系
FURNITURE_GROUPS = {
    "dining_set": {
        "core": FurnitureType.TABLE,
        "related": [FurnitureType.CHAIR],
        "radius": 2.0,
        "min_items": 4,
        "priority": 0
    },
    "office_set": {
        "core": FurnitureType.DESK,
        "related": [FurnitureType.CHAIR],
        "radius": 1.5,
        "min_items": 1,
        "priority": 1
    },
    "living_set": {
        "core": FurnitureType.SOFA,
        "related": [FurnitureType.COFFEE_TABLE, FurnitureType.TV_STAND],
        "radius": 3.0,
        "min_items": 1,
        "priority": 2
    },
    "bedroom_set": {
        "core": FurnitureType.BED,
        "related": [FurnitureType.NIGHTSTAND, FurnitureType.WARDROBE],
        "radius": 2.5,
        "min_items": 1,
        "priority": 3
    }
}

def enforce_relationships(layout: List[Furniture]) -> List[Furniture]:
    """执行所有关联规则"""
    for item in layout:
        relations = RELATIONSHIPS.get(item.type, [])
        for rel in relations:
            related_items = []
            if isinstance(rel["related"], str):
                # 针对非家具类型（如"READING_AREA"或"ENTRANCE"）的关联，略过具体实现
                continue
            else:
                related_items = [i for i in layout if i.type == rel["related"]]
            if not related_items:
                continue
                
            if rel.get("facing"):
                _adjust_facing(item, related_items)
            if "distance_multiplier" in rel:
                _enforce_distance_multiplier(item, related_items, rel["distance_multiplier"])
            if "min_distance" in rel and "max_distance" in rel:
                _enforce_distance_range(item, related_items, rel["min_distance"], rel["max_distance"])
            if rel.get("alignment"):
                _enforce_alignment(item, related_items)
    return layout

def _adjust_facing(main_item: Furniture, related_items: List[Furniture]) -> None:
    """调整关联物品朝向"""
    for related in related_items:
        dx = related.x - main_item.x
        dy = related.y - main_item.y
        angle = math.degrees(math.atan2(dy, dx))
        related.rotation = (angle + 180) % 360

def _enforce_distance_multiplier(main_item: Furniture, related_items: List[Furniture], multiplier: float) -> None:
    """确保主物品与关联物品之间的距离为某倍数（例如电视观影距离）"""
    for related in related_items:
        current_dist = main_item.polygon.distance(related.polygon)
        # 假设main_item有tv_size属性
        desired_dist = getattr(main_item, 'tv_size', 0.5) * multiplier
        if abs(current_dist - desired_dist) > 0.1:
            dx = related.x - main_item.x
            dy = related.y - main_item.y
            factor = (current_dist - desired_dist) / current_dist if current_dist != 0 else 0
            related.x += dx * factor
            related.y += dy * factor

def _enforce_distance_range(main_item: Furniture, related_items: List[Furniture], min_dist: float, max_dist: float) -> None:
    """确保关联物品之间的距离落在[min_dist, max_dist]范围内"""
    for related in related_items:
        current_dist = main_item.polygon.distance(related.polygon)
        if current_dist < min_dist:
            # 向外移动
            dx = related.x - main_item.x
            dy = related.y - main_item.y
            move_dist = min_dist - current_dist
            norm = (dx**2 + dy**2) ** 0.5 or 1
            related.x += (dx / norm) * move_dist
            related.y += (dy / norm) * move_dist
        elif current_dist > max_dist:
            # 向内移动
            dx = related.x - main_item.x
            dy = related.y - main_item.y
            move_dist = current_dist - max_dist
            norm = (dx**2 + dy**2) ** 0.5 or 1
            related.x -= (dx / norm) * move_dist
            related.y -= (dy / norm) * move_dist

def _enforce_alignment(main_item: Furniture, related_items: List[Furniture]) -> None:
    """确保关联物品对齐"""
    for related in related_items:
        # 简单示例：将关联物品的y坐标与主物品对齐
        related.y = main_item.y

def apply_group_rules(layout: List[Furniture], room: Room) -> List[Furniture]:
    """应用组合家具规则"""
    # 按优先级排序处理组合
    sorted_groups = sorted(
        FURNITURE_GROUPS.items(),
        key=lambda x: x[1].get("priority", 0),
        reverse=True
    )
    
    for group_name, config in sorted_groups:
        cores = [item for item in layout if item.type == config["core"]]
        for core in cores:
            # 强制关联规则（硬性）
            related_items = _enforce_relation(core, layout, config)
            
            # 优化布局（软性）
            if group_name == "dining_set":
                _arrange_dining_set(core, related_items, layout)
            elif group_name == "office_set":
                _arrange_office_set(core, related_items, layout)
            elif group_name == "living_set":
                _arrange_living_set(core, related_items, layout)
            elif group_name == "bedroom_set":
                _arrange_bedroom_set(core, related_items, layout)
    
    return layout

def _enforce_relation(core: Furniture, layout: List[Furniture], config: Dict[str, Any]) -> List[Furniture]:
    """强制关联检查"""
    related_items = [
        item for item in layout
        if item.type in config["related"]
        and item.polygon.distance(core.polygon) < config.get("radius", 2.0)
    ]
    
    # 不满足最小数量时创建新物品
    if len(related_items) < config.get("min_items", 0):
        new_items = _create_missing_items(core, config)
        layout.extend(new_items)
        related_items.extend(new_items)
    
    return related_items

def _create_missing_items(core: Furniture, config: Dict[str, Any]) -> List[Furniture]:
    """创建缺失的关联物品"""
    # 此处仅为示例，在实际环境中需要完整的家具创建逻辑
    new_items = []
    
    # 确定需要创建的物品类型和数量
    for type_to_create in config["related"]:
        if "min_items" in config:
            # 创建最小数量的物品
            for i in range(config.get("min_items", 0)):
                # 下面的创建逻辑需要根据实际情况调整
                new_item = Furniture(
                    id=f"{core.id}_rel_{len(new_items)}",
                    type=type_to_create,
                    x=core.x + 1.0,  # 默认位置，后续会调整
                    y=core.y + 1.0,
                    width=0.5,
                    height=0.5,
                    rotation=0
                )
                new_items.append(new_item)
    
    return new_items

def find_optimal_position(item: Furniture, core: Furniture, config: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    """为关联家具寻找最佳位置"""
    # 根据家具类型确定理想位置
    if item.type == FurnitureType.CHAIR and core.type == FurnitureType.TABLE:
        # 为餐桌周围的椅子找位置
        angle = random.random() * 2 * math.pi
        radius = 0.8  # 椅子与桌子中心的距离
        return (
            core.x + core.width/2 + math.cos(angle) * radius,
            core.y + core.height/2 + math.sin(angle) * radius
        )
    
    elif item.type == FurnitureType.CHAIR and core.type == FurnitureType.DESK:
        # 为书桌配置椅子
        # 默认椅子位于书桌前方
        angle_rad = math.radians(core.rotation)  # 假设desk.rotation表示桌子朝向
        return (
            core.x + math.cos(angle_rad) * 0.8,
            core.y + math.sin(angle_rad) * 0.8
        )
    
    elif item.type == FurnitureType.COFFEE_TABLE and core.type == FurnitureType.SOFA:
        # 咖啡桌在沙发前方
        # 假设沙发的rotation表示正面朝向
        angle_rad = math.radians(core.rotation)
        return (
            core.x + math.cos(angle_rad) * 0.5,
            core.y + math.sin(angle_rad) * 0.5
        )
    
    elif item.type == FurnitureType.NIGHTSTAND and core.type == FurnitureType.BED:
        # 床头柜放在床两侧
        bed_width = core.width  # 床的宽度
        return (core.x + bed_width + 0.1, core.y)  # 放在床右侧
    
    # 如果没有特定规则，返回None
    return None

def _arrange_dining_set(table: Furniture, chairs: List[Furniture], layout: List[Furniture]) -> None:
    """环形排列餐椅"""
    if not chairs:
        return
    
    # 计算每把椅子的角度间隔
    angle_step = 360 / len(chairs)
    table_width = getattr(table, 'width', 1.0)
    table_height = getattr(table, 'height', 1.0)
    
    # 对每把椅子进行定位
    for i, chair in enumerate(chairs):
        angle = angle_step * i
        rad = math.radians(angle)
        
        # 计算椅子位置 (餐桌中心点 + 偏移量)
        chair.x = table.x + table_width/2 + math.cos(rad) * 0.9
        chair.y = table.y + table_height/2 + math.sin(rad) * 0.9
        
        # 椅子朝向餐桌中心
        chair.rotation = (angle + 180) % 360  # 面向餐桌

def _arrange_office_set(desk: Furniture, items: List[Furniture], layout: List[Furniture]) -> None:
    """调整办公桌和相关物品"""
    # 筛选出椅子
    chairs = [item for item in items if item.type == FurnitureType.CHAIR]
    
    # 如果有椅子，将其放在桌前
    if chairs:
        chair = chairs[0]  # 假设每个办公桌只配一把椅子
        
        # 确定桌子朝向
        desk_facing = getattr(desk, 'rotation', 0)
        angle_rad = math.radians(desk_facing)
        
        # 计算椅子位置 (桌前方空间)
        chair.x = desk.x + math.cos(angle_rad) * 0.7
        chair.y = desk.y + math.sin(angle_rad) * 0.7
        
        # 椅子朝向与桌子相同
        chair.rotation = desk_facing

def _arrange_living_set(sofa: Furniture, items: List[Furniture], layout: List[Furniture]) -> None:
    """调整客厅组合家具"""
    coffee_tables = [item for item in items if item.type == FurnitureType.COFFEE_TABLE]
    tv_stands = [item for item in items if item.type == FurnitureType.TV_STAND]
    
    # 放置咖啡桌
    if coffee_tables:
        coffee_table = coffee_tables[0]
        sofa_facing = getattr(sofa, 'rotation', 0)
        angle_rad = math.radians(sofa_facing)
        
        # 咖啡桌在沙发前方
        coffee_table.x = sofa.x + math.cos(angle_rad) * 0.5
        coffee_table.y = sofa.y + math.sin(angle_rad) * 0.5
    
    # 放置电视柜
    if tv_stands:
        tv_stand = tv_stands[0]
        sofa_facing = getattr(sofa, 'rotation', 0)
        angle_rad = math.radians(sofa_facing)
        
        # 电视柜在沙发对面，距离远一些
        tv_stand.x = sofa.x + math.cos(angle_rad) * 3.0
        tv_stand.y = sofa.y + math.sin(angle_rad) * 3.0
        
        # 电视柜面向沙发
        tv_stand.rotation = (sofa_facing + 180) % 360

def _arrange_bedroom_set(bed: Furniture, items: List[Furniture], layout: List[Furniture]) -> None:
    """调整卧室组合家具"""
    nightstands = [item for item in items if item.type == FurnitureType.NIGHTSTAND]
    wardrobes = [item for item in items if item.type == FurnitureType.WARDROBE]
    
    # 床头柜放置
    if nightstands:
        bed_width = getattr(bed, 'width', 2.0)
        bed_height = getattr(bed, 'height', 1.0)
        
        # 床头的两侧
        if len(nightstands) == 1:
            nightstands[0].x = bed.x + bed_width + 0.1
            nightstands[0].y = bed.y
        elif len(nightstands) >= 2:
            # 左边床头柜
            nightstands[0].x = bed.x - nightstands[0].width - 0.1
            nightstands[0].y = bed.y
            # 右边床头柜
            nightstands[1].x = bed.x + bed_width + 0.1
            nightstands[1].y = bed.y
    
    # 衣柜放置
    if wardrobes:
        wardrobe = wardrobes[0]
        # 放在床对面或者旁边远一点的地方
        wardrobe.x = bed.x
        wardrobe.y = bed.y + bed.height + 1.0  # 床对面放置
