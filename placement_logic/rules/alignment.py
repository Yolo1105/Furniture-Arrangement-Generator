import math
from core.furniture import FurnitureType
from shapely.geometry import Polygon

def align_all_items(layout):
    """统一对齐规则入口"""
    layout = align_bed(layout)
    layout = align_sofa_tv(layout)
    layout = align_table_chairs(layout)
    layout = align_wardrobe_mirror(layout)
    layout = align_desk(layout)
    layout = align_bookshelf(layout)
    layout = align_shoe_cabinet(layout)
    layout = align_coffee_table(layout)
    layout = align_combination_sofa(layout)
    return layout

def align_bed(layout):
    beds = [i for i in layout if i.type == FurnitureType.BED]
    for bed in beds:
        # 靠最长墙面居中，并避免床头正对门窗（具体逻辑可根据房间信息细化）
        if bed.width > bed.height:
            bed.x = 0.5  # 靠中
            bed.rotation = 0
        else:
            bed.y = 0.5
            bed.rotation = 90
    return layout

def align_sofa_tv(layout):
    sofas = [i for i in layout if i.type == FurnitureType.SOFA]
    tvs = [i for i in layout if i.type == FurnitureType.TV_STAND]
    for sofa in sofas:
        # 正对最近的电视柜
        if tvs:
            nearest_tv = min(tvs, key=lambda tv: sofa.polygon.distance(tv.polygon))
            dx = nearest_tv.x - sofa.x
            dy = nearest_tv.y - sofa.y
            sofa.rotation = (math.degrees(math.atan2(dy, dx)) + 180) % 360
    return layout

def align_table_chairs(layout):
    tables = [i for i in layout if i.type == FurnitureType.TABLE]
    chairs = [i for i in layout if i.type == FurnitureType.CHAIR]
    for table in tables:
        # 环绕排列餐椅，距离设为0.75m（70-80cm区间取中值）
        chairs_near = [c for c in chairs if c.polygon.distance(table.polygon) < 1.0]
        if not chairs_near:
            continue
        angle_step = 360 / len(chairs_near)
        for i, chair in enumerate(chairs_near):
            rad = math.radians(angle_step * i)
            chair.x = table.x + math.cos(rad) * 0.75
            chair.y = table.y + math.sin(rad) * 0.75
            chair.rotation = (math.degrees(rad) + 180) % 360
    return layout

def align_wardrobe_mirror(layout):
    # 对于衣柜，若存在穿衣镜（假设FurnitureType.MIRROR存在），则将镜子与衣柜对齐摆放
    wardrobes = [i for i in layout if i.type == FurnitureType.WARDROBE]
    mirrors = [i for i in layout if i.type == FurnitureType.MIRROR] if hasattr(FurnitureType, 'MIRROR') else []
    for wardrobe in wardrobes:
        # 将与之最近的镜子，放置在衣柜右侧（示例逻辑，可根据房间入口侧优化）
        if mirrors:
            related_mirror = min(mirrors, key=lambda m: wardrobe.polygon.distance(m.polygon))
            # 设定镜子紧贴衣柜右侧，留出0.05m缝隙
            related_mirror.x = wardrobe.x + wardrobe.width + 0.05
            related_mirror.y = wardrobe.y
    return layout

def align_desk(layout):
    # 书桌临窗布置，假设窗户在房间左侧
    desks = [i for i in layout if i.type == FurnitureType.DESK]
    for desk in desks:
        desk.x = 0.1  # 靠近左墙
        desk.y = 0.5  # 垂直方向居中（如有房间信息可细化）
        # 根据书桌尺寸或朝向调整rotation（此处示例设为0）
        desk.rotation = 0
    return layout

def align_bookshelf(layout):
    # 书柜沿墙连续布置，假设沿北墙排列
    bookshelves = [i for i in layout if i.type == FurnitureType.BOOKSHELF]
    if not bookshelves:
        return layout
    # 统一沿北墙（y坐标固定）并依次排列
    start_x = 0.05
    gap = 0.05
    for shelf in sorted(bookshelves, key=lambda s: s.x):
        shelf.y = 0.1  # 靠近北墙
        shelf.x = start_x
        start_x += shelf.width + gap
    return layout

def align_shoe_cabinet(layout):
    # 鞋柜靠近入口处放置，假设入口在房间左下角
    shoe_cabinets = [i for i in layout if i.type == FurnitureType.SHOE_CABINET]
    for cabinet in shoe_cabinets:
        cabinet.x = 0.1
        cabinet.y = 0.9  # 示例位置，可根据入口实际位置调整
    return layout

def align_coffee_table(layout):
    # 咖啡桌距离沙发前缘40cm，长边与沙发对齐
    coffee_tables = [i for i in layout if i.type == FurnitureType.COFFEE_TABLE]
    sofas = [i for i in layout if i.type == FurnitureType.SOFA]
    for table in coffee_tables:
        if sofas:
            # 选择最近的沙发
            sofa = min(sofas, key=lambda s: table.polygon.distance(s.polygon))
            rad = math.radians(sofa.rotation)
            # 将咖啡桌放在沙发前方0.4m处
            table.x = sofa.x + math.cos(rad) * 0.4
            table.y = sofa.y + math.sin(rad) * 0.4
            table.rotation = sofa.rotation
    return layout

def align_combination_sofa(layout):
    # 对于组合沙发，确保各组成部分夹角>90°
    sofas = [i for i in layout if i.type == FurnitureType.SOFA and getattr(i, 'is_combination', False)]
    for sofa in sofas:
        # 这里假设 sofa.segments 存在并记录各部分朝向（示例逻辑）
        if hasattr(sofa, 'segments') and len(sofa.segments) >= 2:
            angle = abs(sofa.segments[0] - sofa.segments[1])
            if angle < 90:
                # 调整其中一部分，使夹角达到90度（此处为简单示例）
                sofa.segments[1] = (sofa.segments[0] + 90) % 360
    return layout

def align_desk(layout, room):
    """书桌临窗布置（根据实际窗户位置）"""
    desks = [i for i in layout if i.type == FurnitureType.DESK]
    windows = room.windows  # 假设 room 有 windows 属性记录窗户位置
    for desk in desks:
        if windows:
            nearest_window = min(windows, key=lambda w: desk.polygon.distance(w.polygon))
            desk.x = nearest_window.x + 0.1  # 沿窗边偏移
            desk.rotation = 0  # 朝向房间内部
    return layout

def align_bookshelf(layout, room):
    bookshelves = [i for i in layout if i.type == FurnitureType.BOOKSHELF]
    if not bookshelves:
        return layout
    # 获取北墙坐标（假设room提供墙面信息）
    north_wall_y = room.walls["north"].y
    start_x = 0.05
    gap = 0.05
    for shelf in sorted(bookshelves, key=lambda s: s.x):
        shelf.y = north_wall_y + 0.1  # 沿北墙偏移
        shelf.x = start_x
        start_x += shelf.width + gap
    return layout