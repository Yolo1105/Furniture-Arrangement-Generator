from shapely.strtree import STRtree
from shapely.geometry import Polygon
from core.furniture import FurnitureType
from core.config_loader import ConfigLoader
import math
from generation.collision.furniture_relations import FURNITURE_RELATIONS, get_relation_rule

class CollisionChecker:
    def __init__(self, layout):
        self.layout = layout
        # 生成带缓冲区的多边形（确保 Furniture.get_buffered_polygon() 已正确处理旋转）
        self.buffered_polys = [item.get_buffered_polygon() for item in self.layout]
        # 构建空间索引
        self.tree = STRtree(self.buffered_polys) if self.buffered_polys else None
        # 加载关系规则
        self.relation_rules = FURNITURE_RELATIONS

    def check_collision(self, new_item):
        """检测新家具是否与现有布局碰撞（带缓冲区）"""
        if not self.tree:
            return False
            
        query_poly = new_item.get_buffered_polygon()
        # 使用空间索引查询潜在碰撞对象
        possible_collisions = self.tree.query(query_poly)
        
        # 精确检查每个潜在碰撞
        for i, poly in enumerate(possible_collisions):
            if poly.intersects(query_poly) and self.layout[i].id != new_item.id:
                return True
        return False

    def check_relation_rules(self, item, ref_items):
        """检查与所有关联家具的规则（如沙发必须正对电视柜）"""
        if not hasattr(item, 'type') or not item.type:
            return True
            
        item_type_name = item.type.name if hasattr(item.type, 'name') else str(item.type)
        
        # 检查方向规则
        facing_rule = self.relation_rules.get(item_type_name, {}).get('facing', None)
        if facing_rule:
            target_type = facing_rule['type']
            targets = [i for i in ref_items if hasattr(i, 'type') and 
                      (i.type.name == target_type if hasattr(i.type, 'name') else str(i.type) == target_type)]
            
            threshold = facing_rule.get('threshold', 30)
            if targets and not any(self._check_facing(item, target, threshold) for target in targets):
                return False
                
        return True

    def _check_face_to_face(self, item1, item2):
        """检查两个家具是否相互朝向"""
        if not (hasattr(item1, 'polygon') and hasattr(item2, 'polygon')):
            return True
            
        item1_rect = item1.polygon.bounds
        item2_rect = item2.polygon.bounds
        
        # 计算中心点
        center1 = ((item1_rect[0] + item1_rect[2]) / 2, (item1_rect[1] + item1_rect[3]) / 2)
        center2 = ((item2_rect[0] + item2_rect[2]) / 2, (item2_rect[1] + item2_rect[3]) / 2)
        
        # 计算方向向量
        dx = center2[0] - center1[0]
        dy = center2[1] - center1[1]
        angle = math.degrees(math.atan2(dy, dx))
        
        # 检查物体朝向与这个方向的夹角
        facing_angle1 = getattr(item1, 'rotation', 0)
        facing_angle2 = getattr(item2, 'rotation', 0)
        
        angle_diff1 = abs((facing_angle1 - angle) % 360)
        angle_diff2 = abs((facing_angle2 - (angle + 180) % 360) % 360)
        
        # 阈值设为30度
        return min(angle_diff1, 360 - angle_diff1) <= 30 and min(angle_diff2, 360 - angle_diff2) <= 30

    def check_all(self, new_item):
        """综合检查碰撞、邻近规则和方向规则"""
        return (
            not self.check_collision(new_item) and
            self.check_proximity_rules(new_item) and
            self.check_orientation_rules(new_item)
        )

    def check_proximity_rules(self, item):
        """检查必须邻近的家具（如椅子必须靠近桌子）"""
        if not hasattr(item, 'type') or not item.type:
            return True
            
        item_type_name = item.type.name if hasattr(item.type, 'name') else str(item.type)
        required_types = get_relation_rule(item_type_name).get("must_near", [])
        
        if not required_types:  # 没有必须邻近的类型
            return True
            
        # 检查是否有至少一个必要的邻近物品
        for req_type in required_types:
            required_items = [i for i in self.layout if 
                             hasattr(i, 'type') and 
                             (i.type.name == req_type if hasattr(i.type, 'name') else str(i.type) == req_type)]
            
            for ref_item in required_items:
                if hasattr(item, 'polygon') and hasattr(ref_item, 'polygon'):
                    clearance = get_relation_rule(item_type_name).get("clearance", 1.0)
                    if item.polygon.buffer(clearance).intersects(ref_item.polygon):
                        return True
                        
        # 如果required_types非空但没找到任何满足条件的物品
        return len(required_types) == 0

    def check_orientation_rules(self, item):
        """检查方向性规则（如床不能正对门）"""
        if not hasattr(item, 'type') or not item.type:
            return True
            
        item_type_name = item.type.name if hasattr(item.type, 'name') else str(item.type)
        rule = get_relation_rule(item_type_name)
        if not rule.get("facing"):
            return True
        
        target_type = rule["facing"]["type"]
        targets = [i for i in self.layout if 
                  hasattr(i, 'type') and 
                  (i.type.name == target_type if hasattr(i.type, 'name') else str(i.type) == target_type)]
                  
        if not targets:  # 没有目标物品，规则不适用
            return True
            
        threshold = rule["facing"].get("threshold", 30)  # 默认允许 30 度偏差
        
        return any(
            self._check_facing(item, target, threshold)
            for target in targets
        )

    def _check_facing(self, item, target, threshold):
        """计算两个家具的朝向角度差"""
        if not (hasattr(item, 'polygon') and hasattr(target, 'polygon')):
            return True
            
        item_center = item.polygon.centroid
        target_center = target.polygon.centroid
        
        # 计算目标相对于当前家具的方向角度
        dx = target_center.x - item_center.x
        dy = target_center.y - item_center.y
        target_angle = math.degrees(math.atan2(dy, dx))
        
        # 计算当前家具的旋转角度差
        item_rotation = getattr(item, 'rotation', 0)
        angle_diff = abs((item_rotation - target_angle) % 360)
        return min(angle_diff, 360 - angle_diff) <= threshold

    def update_layout(self, new_layout):
        """更新布局时重新构建索引"""
        self.layout = new_layout
        self.buffered_polys = [item.get_buffered_polygon() for item in self.layout]
        self.tree = STRtree(self.buffered_polys) if self.buffered_polys else None

    def validate(self, item):
        """验证单个物品是否符合所有规则"""
        # 创建一个临时布局，不包括当前物品
        temp_layout = [i for i in self.layout if i.id != item.id]
        # 创建临时检查器
        temp_checker = CollisionChecker(temp_layout)
        # 综合检查
        return temp_checker.check_all(item)
