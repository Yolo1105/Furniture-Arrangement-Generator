import math
from pathfinder import DynamicPathFinder

class RuleIntegratedScorer:
    def __init__(self, room_config):
        self.room_config = room_config
        self.path_finder = DynamicPathFinder(room_config)
        self.weights = room_config.get("scoring_weights", {
            "bed_window_proximity": 1.0,
            "chair_table_proximity": 1.0,
            "furniture_spacing": 1.0,
            "door_accessibility": 1.0,
            "alignment": 1.0,
            "space_utilization": 1.0  # Added missing weight
        })
        
    def calculate_dynamic_score(self, layout):
        """动态综合评分（入口函数）"""
        return {
            'comfort': self._comfort_score(layout),
            'accessibility': self._accessibility_score(layout),
            'space_utilization': self._space_utilization(layout),
            'total': self._total_score(layout)
        }

    def calculate_layout_score(self, layout):
        """兼容旧接口的布局总分"""
        return self._total_score(layout)

    # --------------------------
    # 以下是所有评分子项的独立实现
    # --------------------------
    def _comfort_score(self, layout):
        """舒适性评分（床与窗户距离）"""
        score = 0
        windows = self.room_config.get("windows", [])
        for item in layout:
            if hasattr(item, 'type') and isinstance(item.type, str) and item.type.lower() == "bed":
                bed_x, bed_y = item.x, item.y
                if windows:
                    wx, wy = windows[0][0], windows[0][1]
                    dist = math.sqrt((bed_x - wx)**2 + (bed_y - wy)**2)
                    score += self.weights["bed_window_proximity"] * max(0, 10 - dist)
        return score

    def _accessibility_score(self, layout):
        """门可访问性评分（依赖DynamicPathFinder）"""
        self.path_finder.update_layout(layout)
        score = 0
        doors = self.room_config.get("doors", [])
        if not doors:
            return 10 * self.weights["door_accessibility"]  # If no doors, assume perfect accessibility
            
        room_center = (
            self.room_config.get("room_width", 10) / 2,
            self.room_config.get("room_height", 10) / 2
        )
        for door in doors:
            door_center = (door[0] + door[2]/2, door[1] + door[3]/2)
            if self.path_finder.find_path(door_center, room_center):
                score += 10
            else:
                score -= 20
        return max(0, score) * self.weights["door_accessibility"]

    def _space_utilization(self, layout):
        """空间利用率评分"""
        if not layout:
            return 0
            
        used_area = sum(item.width * item.height for item in layout if hasattr(item, 'width') and hasattr(item, 'height'))
        total_area = self.room_config.get("room_width", 10) * self.room_config.get("room_height", 10)
        if total_area == 0:
            return 0
            
        util_score = (used_area / total_area) * 100
        return util_score * self.weights.get("space_utilization", 1.0)

    def _furniture_spacing_score(self, layout):
        """家具间距评分"""
        score = 0
        for i in range(len(layout)):
            for j in range(i+1, len(layout)):
                if hasattr(layout[i], 'x') and hasattr(layout[i], 'y') and \
                   hasattr(layout[j], 'x') and hasattr(layout[j], 'y'):
                    x1, y1 = layout[i].x, layout[i].y
                    x2, y2 = layout[j].x, layout[j].y
                    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                    if distance < 1.0:
                        score += self.weights.get("furniture_spacing", 1.0) * (distance - 1.0)
        return score

    def _alignment_score(self, layout):
        """对齐评分"""
        score = 0
        for item in layout:
            if hasattr(item, 'x') and hasattr(item, 'y'):
                if abs(item.x - round(item.x)) < 0.2:
                    score += self.weights.get("alignment", 1.0)
                if abs(item.y - round(item.y)) < 0.2:
                    score += self.weights.get("alignment", 1.0)
        return score

    def _total_score(self, layout):
        """总分计算（权重公式）"""
        return (
            self._comfort_score(layout) * 0.4 +
            self._accessibility_score(layout) * 0.4 +
            self._space_utilization(layout) * 0.2 +
            self._furniture_spacing_score(layout) +
            self._alignment_score(layout)
        )


class MultiObjectiveScorer:
    @staticmethod
    def calculate(layout, room):
        """多目标评分入口"""
        scorer = RuleIntegratedScorer(room.config if hasattr(room, 'config') else {})
        return scorer.calculate_layout_score(layout)

    @staticmethod
    def comfort_score(layout, room):
        """舒适性评分（复用核心逻辑）"""
        scorer = RuleIntegratedScorer(room.config if hasattr(room, 'config') else {})
        return scorer._comfort_score(layout)

    @staticmethod
    def space_utilization_score(layout, room):
        """空间利用率"""
        scorer = RuleIntegratedScorer(room.config if hasattr(room, 'config') else {})
        return scorer._space_utilization(layout)

    @staticmethod
    def aesthetic_score(layout, room):
        """美学评分（对称性+对齐性）"""
        if not layout:
            return 0
            
        # 对称性：检查家具是否围绕房间中心对称
        symmetry_score = 0
        room_center_x = room.width / 2 if hasattr(room, 'width') else 5  # default if not available
        for item in layout:
            if hasattr(item, 'x') and hasattr(item, 'width'):
                if abs(item.x + item.width/2 - room_center_x) < 0.5:
                    symmetry_score += 1
        symmetry_score = (symmetry_score / len(layout)) * 50
        
        # 对齐性：检查坐标是否为整数
        alignment_score = 0
        for item in layout:
            if hasattr(item, 'x') and hasattr(item, 'y'):
                if abs(item.x - round(item.x)) < 0.1 or abs(item.y - round(item.y)) < 0.1:
                    alignment_score += 1
        alignment_score = (alignment_score / len(layout)) * 50
        
        return symmetry_score + alignment_score
