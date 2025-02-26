# Fixed version of rule_engine.py
from typing import List
import copy
import math
from core.furniture import Furniture, FurnitureType
from core.room import Room
from rules.position_rules import apply_position_rules
from rules.clearance import check_all_clearances
from rules.relation_rules import enforce_relationships, apply_group_rules
from rules.alignment import align_all_items
from shapely.geometry import LineString
from shapely.geometry import Polygon, LineString

try:
    from rtree import index
except ImportError:
    # 如果rtree不可用，使用简单的替代
    class SimpleSpatialIndex:
        def __init__(self):
            self.items = []
            
        def insert(self, id, bounds):
            self.items.append((id, bounds))
            
        def intersection(self, bounds):
            min_x, min_y, max_x, max_y = bounds
            results = []
            for id, item_bounds in self.items:
                i_min_x, i_min_y, i_max_x, i_max_y = item_bounds
                if (max_x >= i_min_x and min_x <= i_max_x and
                    max_y >= i_min_y and min_y <= i_max_y):
                    results.append(id)
            return results
    
    class index:
        Index = SimpleSpatialIndex

class CollisionChecker:
    """简单碰撞检测器"""
    def __init__(self, layout):
        self.layout = layout
        
    def validate(self, item):
        """检查item是否与其他物品碰撞"""
        for other in self.layout:
            if other.id != item.id and item.polygon.intersects(other.polygon):
                return False
        return True

class PathFinder:
    """简化的路径查找器"""
    def __init__(self, room_config):
        self.room_config = room_config
        self.layout = []
        
    def update_layout(self, layout):
        self.layout = layout
        
    def find_path(self, start, end):
        """简单判断路径是否被阻塞"""
        path = LineString([start, end])
        for item in self.layout:
            if item.polygon.intersects(path):
                return False
        return True

class RuleEngine:
    def __init__(self, room_config):
        """统一规则引擎，包含所有布局优化逻辑"""
        self.rule_priority = {
            "collision_fix": 0,
            "door_clearance": 1,
            "functional_groups": 2,
            "aesthetic_rules": 3,
            "path_optimization": 4
        }

        self.active_rules = {
            "chair_alignment": True,
            "sofa_tv_facing": True,
            "desk_chair_position": True,
            "path_optimization": True
        }

        self.path_finder = PathFinder(room_config)
        self.room_config = room_config
        self.room = self._create_room_from_config(room_config)
        self.rule_config = {
            "collision_fix": {"weight": 10, "type": "hard"},
            "door_clearance": {"weight": 8, "type": "hard"},
            "functional_groups": {"weight": 5, "type": "soft"},
            "aesthetic_rules": {"weight": 3, "type": "soft"}
        }
        self.rule_stats = {}   # 规则执行统计

    def _create_room_from_config(self, config):
        """从配置创建房间对象"""
        # 简化示例，实际可能需要更完整的Room类实现
        class SimpleRoom:
            def __init__(self, width, height, doors=None):
                self.width = width
                self.height = height
                self.doors = doors or []
                
            def is_within_bounds(self, x, y, width, height):
                return 0 <= x <= self.width - width and 0 <= y <= self.height - height
                
        return SimpleRoom(
            config.get("room_width", 10),
            config.get("room_height", 10),
            config.get("doors", [])
        )

    def apply_rules(self, layout: List[Furniture], room: Room) -> List[Furniture]:
        """按优先级顺序应用所有规则"""
        # 更新路径规划
        self.path_finder.update_layout(layout)

        # 深拷贝，避免修改原始数据
        current_layout = [copy.deepcopy(item) for item in layout]

        # 1. 硬性规则
        current_layout = self._apply_hard_rules(current_layout, room)

        # 2. 软性优化
        current_layout = self._optimize_soft_rules(current_layout, room)

        # 3. 路径优化
        if self.active_rules.get("path_optimization"):
            current_layout = self._apply_path_rules(current_layout)

        return current_layout

    def _apply_hard_rules(self, layout, room):
        """执行硬性规则"""
        # 移除发生碰撞的家具
        checker = CollisionChecker(layout)
        layout = [item for item in layout if checker.validate(item)]
        
        # 处理通道问题
        clearance_issues = check_all_clearances(layout, room)
        for issue in clearance_issues:
            layout = self._fix_clearance(issue, layout)

        return layout

    def _fix_clearance(self, issue, layout):
        """修复通道问题"""
        # 简化示例，实际可能需要根据具体的issue结构调整
        if hasattr(issue, 'blocking_id') and hasattr(issue, 'offset_x') and hasattr(issue, 'offset_y'):
            for item in layout:
                if item.id == issue.blocking_id:
                    item.x += issue.offset_x
                    item.y += issue.offset_y
        return layout

    def _apply_soft_rules(self, layout, room):
        """执行软性规则"""
        layout = align_all_items(layout)
        layout = apply_position_rules(layout)
        layout = enforce_relationships(layout)
        return layout

    def _optimize_soft_rules(self, layout, room):
        """软性规则优化（带权重评估）"""
        best_layout = layout
        best_score = self._evaluate_layout(layout, room)

        for _ in range(5):  # 进行多轮优化
            # 创建当前轮次的布局副本
            modified_layout = copy.deepcopy(best_layout)
            
            # 依次应用各规则
            for rule_name, cfg in self.rule_config.items():
                if cfg["type"] == "soft":
                    modified_layout = self._execute_rule(rule_name, modified_layout, room)
                    self.rule_stats[rule_name] = self.rule_stats.get(rule_name, 0) + 1

            # 评估新布局
            current_score = self._evaluate_layout(modified_layout, room)
            if current_score > best_score:
                best_layout = modified_layout
                best_score = current_score

        return best_layout

    def _apply_path_rules(self, layout):
        """执行路径优化规则"""
        critical_paths = [
            (
                (door[0] + door[2]/2, door[1] + door[3]/2),  # 计算门中心
                (self.room_config.get("room_width", 10)/2, self.room_config.get("room_height", 10)/2)
            )
            for door in self.room_config.get("doors", [])
        ]

        for path in critical_paths:
            if not self.path_finder.find_path(*path):
                layout = self._adjust_for_path(layout, path)
        return layout

    def _adjust_for_path(self, layout, path):
        """修正路径受阻情况"""
        blockage = self._find_path_blockage(path)

        for item in layout:
            if item in blockage:
                self._nudge_item(item)
        return layout

    def _find_path_blockage(self, path):
        """查找阻塞路径的家具"""
        start, end = path
        path_line = LineString([start, end])
        
        # 找出与路径相交的家具
        blocked_items = []
        for item in self.path_finder.layout:
            if item.polygon.intersects(path_line):
                blocked_items.append(item)
                
        return blocked_items

    def _nudge_item(self, item):
        """微调家具以避开路径"""
        original_x, original_y = item.x, item.y
        
        # 简单的偏移尝试
        offsets = [(0.2, 0), (-0.2, 0), (0, 0.2), (0, -0.2)]
        for dx, dy in offsets:
            item.x = original_x + dx
            item.y = original_y + dy
            
            # 检查新位置是否有效
            if self.room.is_within_bounds(item.x, item.y, item.width, item.height):
                # 检查是否还阻塞路径
                path_line = LineString([(0, 0), (self.room.width, self.room.height)])  # 示例路径
                if not item.polygon.intersects(path_line):
                    return
                    
        # 如果所有尝试都失败，恢复原位置
        item.x, item.y = original_x, original_y

    def _execute_rule(self, rule_name, layout, room):
        """执行具体规则"""
        if rule_name == "collision_fix":
            return self._fix_collisions(layout, room)
        elif rule_name == "door_clearance":
            return self._apply_door_rules(layout, room)
        elif rule_name == "functional_groups":
            return self._apply_functional_groups(layout, room)
        elif rule_name == "aesthetic_rules":
            return self._apply_aesthetic_rules(layout, room)
        return layout

    def _check_collision(self, item, layout):
        """使用空间索引加速碰撞检测"""
        idx = index.Index()
        for i, other in enumerate(layout):
            if other.id != item.id:  # 排除自身
                idx.insert(i, other.polygon.bounds)
                
        # 查找可能碰撞的对象
        potential_collisions = list(idx.intersection(item.polygon.bounds))
        
        # 精确检查
        for i in potential_collisions:
            if layout[i].polygon.intersects(item.polygon):
                return False
                
        return True

    def _evaluate_layout(self, layout, room):
        """评估当前布局质量"""
        score = 0
        
        # 碰撞检查（硬性要求）
        checker = CollisionChecker(layout)
        if not all(checker.validate(item) for item in layout):
            return 0  # 有碰撞，评分为0
            
        # 通道检查
        clearance_issues = check_all_clearances(layout, room)
        if clearance_issues:
            score -= len(clearance_issues) * 2
            
        # 功能性评分
        # 示例：评估冰箱与炉灶距离、沙发与电视距离等
        sofa_tv_score = self._eval_sofa_tv_distance(layout)
        score += sofa_tv_score
        
        return max(0, score)  # 确保评分不为负

    def _eval_sofa_tv_distance(self, layout):
        """评估沙发与电视的距离是否合理"""
        sofas = [item for item in layout if item.type == FurnitureType.SOFA]
        tvs = [item for item in layout if item.type == FurnitureType.TV_STAND]
        
        if not sofas or not tvs:
            return 0
            
        # 找最近的沙发-电视组合
        best_dist = float('inf')
        for sofa in sofas:
            for tv in tvs:
                dist = sofa.polygon.distance(tv.polygon)
                if dist < best_dist:
                    best_dist = dist
                    
        # 理想距离范围
        ideal_min, ideal_max = 2.0, 3.5
        if ideal_min <= best_dist <= ideal_max:
            return 5  # 满分
        elif best_dist < ideal_min:
            return 5 - (ideal_min - best_dist) * 2
        else:  # best_dist > ideal_max
            return 5 - (best_dist - ideal_max) * 1
            
    def _fix_collisions(self, layout, room):
        """碰撞解决（最高优先级）"""
        checker = CollisionChecker(layout)
        return [item for item in layout if checker.validate(item)]

    def _apply_door_rules(self, layout, room):
        """门窗通行区规则"""
        # 简化示例：移除位于门附近的家具
        door_zones = []
        for door in room.doors:
            x, y, w, h = door
            # 创建门前通行区多边形
            door_zone = Polygon([
                (x-0.8, y-0.8),
                (x+w+0.8, y-0.8),
                (x+w+0.8, y+h+0.8),
                (x-0.8, y+h+0.8)
            ])
            door_zones.append(door_zone)
            
        # 检查并调整家具位置
        for item in layout:
            for zone in door_zones:
                if item.polygon.intersects(zone):
                    # 尝试移动家具
                    self._move_away_from_zone(item, zone)
                    
        return layout

    def _move_away_from_zone(self, item, zone):
        """将家具移离禁区"""
        # 简单示例：向四个方向尝试移动
        original_x, original_y = item.x, item.y
        
        # 尝试不同方向和距离
        for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for distance in [0.5, 1.0, 1.5]:
                dx, dy = direction
                item.x = original_x + dx * distance
                item.y = original_y + dy * distance
                
                # 检查新位置是否有效
                if (self.room.is_within_bounds(item.x, item.y, item.width, item.height) and
                    not item.polygon.intersects(zone)):
                    return
                    
        # 如果所有尝试都失败，恢复原位置
        item.x, item.y = original_x, original_y

    def _apply_functional_groups(self, layout, room):
        """功能组合规则"""
        return apply_group_rules(layout, room)

    def _apply_aesthetic_rules(self, layout, room):
        """美学规则"""
        return align_all_items(layout)
