from typing import List, Dict, Any
from core.furniture import Furniture
from core.room import Room
from rules.relation_rules import FURNITURE_GROUPS

class RuleEvaluator:
    @staticmethod
    def evaluate(layout: List[Furniture], room: Room) -> float:
        """综合规则评分（越高越好）"""
        score = 0.0
        
        # 功能性评分
        score += 10 * RuleEvaluator._group_completeness(layout)
        score += 5 * RuleEvaluator._door_accessibility(layout, room)
        
        # 美学评分
        score += 3 * RuleEvaluator._symmetry_score(layout)
        
        return score

    @staticmethod
    def get_optimization_hints(layout: List[Furniture]) -> Dict[str, Any]:
        """返回优化建议（示例）"""
        hints = {}
        for i, item in enumerate(layout):
            if item.type == "chair":
                nearest_table = RuleEvaluator._find_nearest(item, layout, "table")
                if nearest_table:
                    hints[f"item_{i}"] = {
                        "suggested_x": nearest_table.x + 0.8,
                        "suggested_y": nearest_table.y
                    }
        return hints

    @staticmethod
    def _group_completeness(layout: List[Furniture]) -> float:
        """检查组合完整性"""
        complete_groups = 0
        for config in FURNITURE_GROUPS.values():
            cores = [item for item in layout if item.type == config["core"]]
            for core in cores:
                related = [item for item in layout if item.type in config["related"]]
                if len(related) >= config.get("min_items", 1):
                    complete_groups += 1
        return min(1.0, complete_groups / max(1, len(FURNITURE_GROUPS)))

    @staticmethod
    def _door_accessibility(layout: List[Furniture], room: Room) -> float:
        """检查门口通道畅通度"""
        # 简化评估：检查家具是否远离门区域
        if not hasattr(room, 'doors') or not room.doors:
            return 1.0  # 无门信息则默认满分
            
        # 检查每个门前1米区域内是否有家具
        blocked_doors = 0
        for door in room.doors:
            x, y, w, h = door
            # 创建门前1米区域
            door_area = {
                'x1': x - 1.0, 'y1': y - 1.0,
                'x2': x + w + 1.0, 'y2': y + h + 1.0
            }
            
            # 检查是否有家具在此区域
            for item in layout:
                if (item.x < door_area['x2'] and 
                    item.x + item.width > door_area['x1'] and
                    item.y < door_area['y2'] and
                    item.y + item.height > door_area['y1']):
                    blocked_doors += 1
                    break
                    
        return 1.0 - (blocked_doors / len(room.doors))

    @staticmethod
    def _symmetry_score(layout: List[Furniture]) -> float:
        """评估布局对称性"""
        # 简单示例：评估成对家具的对称摆放
        pairs = {
            "nightstand": [],
            "chair": [],
            "lamp": []
        }
        
        # 收集成对家具
        for item in layout:
            if str(item.type).lower() in pairs:
                pairs[str(item.type).lower()].append(item)
        
        # 评估对称性
        symmetry_score = 0
        total_pairs = 0
        
        for type_name, items in pairs.items():
            if len(items) >= 2:
                total_pairs += len(items) // 2
                # 根据x坐标排序
                items.sort(key=lambda i: i.x)
                
                # 检查每对家具的y坐标差异
                for i in range(0, len(items), 2):
                    if i + 1 < len(items):
                        y_diff = abs(items[i].y - items[i+1].y)
                        if y_diff < 0.1:  # 视为对称摆放
                            symmetry_score += 1
        
        return symmetry_score / max(1, total_pairs)

    @staticmethod
    def _find_nearest(item: Furniture, layout: List[Furniture], type_name: str) -> Furniture:
        """查找最近的指定类型家具"""
        candidates = [i for i in layout if str(i.type).lower() == type_name.lower()]
        if not candidates:
            return None
            
        return min(candidates, key=lambda x: ((x.x - item.x)**2 + (x.y - item.y)**2)**0.5)
