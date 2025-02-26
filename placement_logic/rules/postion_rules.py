import math
from core.furniture import FurnitureType

# 定义各家具的定位规则及优先级和硬性/软性分类
POSITION_RULES = {
    FurnitureType.BED: [
        {"rule": "against_wall", "priority": 0, "type": "hard"},
        {"rule": "headboard_north", "priority": 1, "type": "soft"}
    ],
    FurnitureType.SOFA: [
        {"rule": "face_tv", "priority": 0, "type": "hard"},
        {"rule": "group_coffee_table", "priority": 1, "type": "soft"},
        {"rule": "combination_angle", "priority": 2, "type": "soft"}
    ],
    FurnitureType.TABLE: [
        {"rule": "center_room", "priority": 0, "type": "hard"},
        {"rule": "chair_distance", "priority": 1, "type": "soft"}
    ],
    FurnitureType.WARDROBE: [
        {"rule": "against_wall", "priority": 0, "type": "hard"},
        {"rule": "door_clearance", "priority": 0, "type": "hard"},
        {"rule": "mirror_alignment", "priority": 1, "type": "soft"}
    ],
    FurnitureType.TV_STAND: [
        {"rule": "sofa_distance", "priority": 0, "type": "hard"},
        {"rule": "symmetry_decor", "priority": 1, "type": "soft"},
        {"rule": "cable_management", "priority": 2, "type": "soft"}
    ],
    FurnitureType.DESK: [
        {"rule": "near_window", "priority": 0, "type": "hard"},
        {"rule": "chair_space", "priority": 0, "type": "hard"},
        {"rule": "avoid_light", "priority": 1, "type": "soft"}
    ],
    FurnitureType.BOOKSHELF: [
        {"rule": "along_wall", "priority": 0, "type": "hard"},
        {"rule": "adjacent_reading", "priority": 1, "type": "soft"},
        {"rule": "max_height", "priority": 0, "type": "hard"}
    ],
    FurnitureType.SHOE_CABINET: [
        {"rule": "near_entrance", "priority": 0, "type": "hard"},
        {"rule": "bench_space", "priority": 1, "type": "soft"},
        {"rule": "door_direction", "priority": 0, "type": "hard"}
    ],
    FurnitureType.COFFEE_TABLE: [
        {"rule": "in_front_sofa", "priority": 0, "type": "hard"},
        {"rule": "edge_alignment", "priority": 1, "type": "soft"},
        {"rule": "no_sharp_angle", "priority": 1, "type": "soft"}
    ],
    FurnitureType.CHAIR: [
        {"rule": "table_distance", "priority": 0, "type": "hard"},
        {"rule": "group_symmetry", "priority": 1, "type": "soft"},
        {"rule": "back_clearance", "priority": 0, "type": "hard"}
    ]
}

def apply_position_rules(layout):
    """执行所有定位规则"""
    for item in layout:
        rules = POSITION_RULES.get(item.type, [])
        sorted_rules = sorted(rules, key=lambda x: x["priority"])
        
        for rule in sorted_rules:
            if rule["rule"] == "against_wall":
                _enforce_wall_alignment(item)
            elif rule["rule"] == "headboard_north":
                _enforce_headboard_north(item)
            elif rule["rule"] == "face_tv":
                _enforce_tv_facing(item, layout)
            elif rule["rule"] == "group_coffee_table":
                _enforce_group_coffee_table(item, layout)
            elif rule["rule"] == "combination_angle":
                _enforce_combination_angle(item)
            elif rule["rule"] == "center_room":
                _enforce_center_room(item)
            elif rule["rule"] == "chair_distance":
                _enforce_chair_distance(item, layout)
            elif rule["rule"] == "door_clearance":
                _enforce_door_clearance(item)
            elif rule["rule"] == "mirror_alignment":
                _enforce_mirror_alignment(item, layout)
            elif rule["rule"] == "sofa_distance":
                _enforce_sofa_distance(item, layout)
            elif rule["rule"] == "symmetry_decor":
                _enforce_symmetry_decor(item, layout)
            elif rule["rule"] == "cable_management":
                _enforce_cable_management(item)
            elif rule["rule"] == "near_window":
                _enforce_near_window(item)
            elif rule["rule"] == "chair_space":
                _enforce_chair_space(item, layout)
            elif rule["rule"] == "avoid_light":
                _enforce_avoid_light(item)
            elif rule["rule"] == "along_wall":
                _enforce_along_wall(item)
            elif rule["rule"] == "adjacent_reading":
                _enforce_adjacent_reading(item, layout)
            elif rule["rule"] == "max_height":
                _enforce_max_height(item)
            elif rule["rule"] == "near_entrance":
                _enforce_near_entrance(item)
            elif rule["rule"] == "bench_space":
                _enforce_bench_space(item)
            elif rule["rule"] == "door_direction":
                _enforce_door_direction(item)
            elif rule["rule"] == "in_front_sofa":
                _enforce_in_front_sofa(item, layout)
            elif rule["rule"] == "edge_alignment":
                _enforce_edge_alignment(item, layout)
            elif rule["rule"] == "no_sharp_angle":
                _enforce_no_sharp_angle(item)
            elif rule["rule"] == "table_distance":
                _enforce_table_distance(item, layout)
            elif rule["rule"] == "group_symmetry":
                _enforce_group_symmetry(item, layout)
            elif rule["rule"] == "back_clearance":
                _enforce_back_clearance(item)
    return layout

# 以下为各规则的简单实现（示例，可根据实际需求扩展细化）

def _enforce_wall_alignment(item):
    # 强制靠墙规则（示例：若item已接近任一房间边界，则认为符合规则）
    # 此处假设房间尺寸信息由item.room提供，若无则略过
    return True

def _enforce_headboard_north(item):
    # 确保床头朝向北方（即床头不正对门窗），示例中将rotation调整为0
    item.rotation = 0
    return True

def _enforce_tv_facing(item, layout):
    # 对于沙发，确保正对电视柜
    tvs = [i for i in layout if i.type == FurnitureType.TV_STAND]
    if tvs:
        tv = min(tvs, key=lambda x: item.polygon.distance(x.polygon))
        dx = tv.x - item.x
        dy = tv.y - item.y
        item.rotation = math.degrees(math.atan2(dy, dx))
    return True

def _enforce_group_coffee_table(item, layout):
    """调整沙发与咖啡桌的协调距离"""
    coffee_tables = [i for i in layout if i.type == FurnitureType.COFFEE_TABLE]
    # 仅处理与当前沙发最近的咖啡桌
    if coffee_tables:
        nearest_table = min(coffee_tables, key=lambda t: item.polygon.distance(t.polygon))
        current_dist = item.polygon.distance(nearest_table.polygon)
        min_dist, max_dist = 0.4, 0.6
        if current_dist < min_dist:
            dx = nearest_table.x - item.x
            dy = nearest_table.y - item.y
            move_dist = min_dist - current_dist
            norm = (dx**2 + dy**2) ** 0.5 or 1
            nearest_table.x += (dx / norm) * move_dist
            nearest_table.y += (dy / norm) * move_dist
        elif current_dist > max_dist:
            dx = nearest_table.x - item.x
            dy = nearest_table.y - item.y
            move_dist = current_dist - max_dist
            norm = (dx**2 + dy**2) ** 0.5 or 1
            nearest_table.x -= (dx / norm) * move_dist
            nearest_table.y -= (dy / norm) * move_dist
    return True

def _enforce_sofa_distance(item, layout, room):
    sofas = [i for i in layout if i.type == FurnitureType.SOFA]
    if sofas:
        if 0 <= new_x <= room.width and 0 <= new_y <= room.height:
            item.x, item.y = new_x, new_y
        nearest_sofa = min(sofas, key=lambda s: item.polygon.distance(s.polygon))
        current_dist = item.polygon.distance(nearest_sofa.polygon)
        desired_dist = 2.0  # 设定合理距离
        dx, dy = nearest_sofa.x - item.x, nearest_sofa.y - item.y
        norm = (dx**2 + dy**2) ** 0.5 or 1
        move_dist = desired_dist - current_dist
        new_x = item.x + (dx / norm) * move_dist
        new_y = item.y + (dy / norm) * move_dist

        # 边界检查
        if 0 < new_x < room.width and 0 < new_y < room.height:
            item.x, item.y = new_x, new_y
    return True

def _enforce_combination_angle(item):
    # 针对组合沙发，确保夹角大于90°
    if hasattr(item, 'segments') and len(item.segments) >= 2:
        angle = abs(item.segments[0] - item.segments[1])
        if angle < 90:
            item.segments[1] = (item.segments[0] + 90) % 360
    return True

def _enforce_center_room(item):
    # 将餐桌放置在居室中心，假设房间尺寸1.0x1.0（示例）
    item.x = 0.5
    item.y = 0.5
    return True

def _enforce_chair_distance(item, layout):
    # 调整与餐桌关联的餐椅距离，具体逻辑在alignment中已安排
    return True

def _enforce_door_clearance(item):
    # 确保衣柜门扇开启方向无阻碍，示例中不做调整，实际需检测门线区域
    return True

def _enforce_mirror_alignment(item, layout):
    # 衣柜的配套穿衣镜位置协调，由alignment模块中的align_wardrobe_mirror处理
    return True

# Fixed version of _enforce_sofa_distance in position_rules.py
def _enforce_sofa_distance(item, layout):
    sofas = [i for i in layout if i.type == FurnitureType.SOFA]
    if sofas:
        nearest_sofa = min(sofas, key=lambda s: item.polygon.distance(s.polygon))
        current_dist = item.polygon.distance(nearest_sofa.polygon)
        desired_dist = 2.0  # 设定合理距离
        dx, dy = nearest_sofa.x - item.x, nearest_sofa.y - item.y
        norm = (dx**2 + dy**2) ** 0.5 or 1
        move_dist = desired_dist - current_dist
        new_x = item.x + (dx / norm) * move_dist
        new_y = item.y + (dy / norm) * move_dist

        # 边界检查（这里需要使用item的属性检查边界，而非引用room）
        # 假设家具自身有边界检查方法或者属性
        if hasattr(item, 'check_bounds'):
            if item.check_bounds(new_x, new_y):
                item.x, item.y = new_x, new_y
    return True


def _enforce_symmetry_decor(item, layout):
    # 对称摆放电视柜两侧装饰柜，示例中暂不做具体调整
    return True

def _enforce_cable_management(item):
    # 隐藏电视柜线缆管理（示例中不做具体调整）
    return True

def _enforce_near_window(item):
    # 将书桌临窗布置，假设窗户在左侧，设置靠近左墙
    item.x = 0.1
    return True

def _enforce_chair_space(item, layout):
    # 确保书桌与书椅间有70cm活动空间，示例中不做具体计算
    return True

def _enforce_avoid_light(item):
    # 避免书桌屏幕正对光源，示例中不做具体调整
    return True

def _enforce_along_wall(item):
    # 书柜沿墙布置，alignment中已处理
    return True

def _enforce_adjacent_reading(item, layout):
    # 书柜与阅读区相邻，示例中不做具体调整
    return True

def _enforce_max_height(item):
    # 限制书柜顶层高度不超过2.2m，假设item.height属性存在
    if getattr(item, 'height', 0) > 2.2:
        item.height = 2.2
    return True

def _enforce_near_entrance(item):
    # 鞋柜靠近入口处，alignment中已处理
    return True

def _enforce_bench_space(item):
    # 预留换鞋凳空间，示例中不做具体调整
    return True

def _enforce_door_direction(item):
    # 开门方向避开动线，示例中不做具体调整
    return True

def _enforce_in_front_sofa(item, layout):
    # 将咖啡桌放置于沙发前40cm处，alignment中已处理
    return True

def _enforce_edge_alignment(item, layout):
    # 长边与沙发对齐，示例中不做具体调整
    return True

def _enforce_no_sharp_angle(item):
    # 避免咖啡桌锐角朝向座位区，示例中不做具体调整
    return True

def _enforce_table_distance(item, layout):
    # 确保餐椅与餐桌距离70-80cm，alignment中已安排
    return True

def _enforce_group_symmetry(item, layout):
    # 餐椅成组对称布置，示例中不做具体调整
    return True

def _enforce_back_clearance(item):
    # 确保餐椅后方保留50cm后退空间，示例中不做具体调整
    return True
