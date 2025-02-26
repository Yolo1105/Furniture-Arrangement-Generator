import copy
from typing import List, Dict, Optional
from core.furniture import Furniture
from core.room import Room
from rules.evaluation import RuleEvaluator
from generation.collision.buffer_check import CollisionChecker
from optimization.genetic.nsga2 import NSGA2Optimizer
from evaluation.scorer import MultiObjectiveScorer
from rules.rule_engine import RuleEngine  # 确保导入增强版规则引擎
from scipy.optimize import minimize
from constraints import ConstraintManager

class TryFailOptimizer:
    def __init__(self, max_attempts: int = 100):
        """初始化局部优化器"""
        self.max_attempts = max_attempts
        self.constraint_manager = ConstraintManager()

    def optimize(
        self,
        layout: List[Furniture],
        room: Room,
        constraints: Optional[Dict[str, tuple]] = None,
        verbose: bool = False
    ) -> List[Furniture]:
        """执行带约束的局部搜索优化"""
        current_layout = copy.deepcopy(layout)
        current_score = RuleEvaluator.evaluate(current_layout, room)
        if verbose:
            print(f"Initial score: {current_score:.2f}")

        # 加载用户约束
        if constraints:
            for fid, (x, y) in constraints.items():
                self.constraint_manager.add_fixed_position(fid, x, y)  # 使用统一约束方法

        for attempt in range(self.max_attempts):
            hints = RuleEvaluator.get_optimization_hints(current_layout, room)
            valid_hints = {k: v for k, v in hints.items() if not self.constraint_manager.is_constrained(k)}

            if not valid_hints:
                if verbose:
                    print(f"Stopping early at attempt {attempt}: No valid hints")
                break

            target_id, suggestion = self._select_best_hint(valid_hints)
            new_layout = self._apply_suggestion(current_layout, target_id, suggestion, room)

            # 规则引擎检查
            if new_layout is not None and self._is_valid(new_layout, room):
                new_score = RuleEvaluator.evaluate(new_layout, room)
                if new_score > current_score:
                    current_layout = new_layout
                    current_score = new_score
                    if verbose:
                        print(f"Attempt {attempt}: Score improved to {new_score:.2f}")

        return current_layout

    def _select_best_hint(self, hints: dict) -> tuple:
        """选择最有价值的优化建议"""
        return max(hints.items(), key=lambda item: item[1]["delta_score"])

    def _apply_suggestion(
        self,
        layout: List[Furniture],
        target_id: str,
        suggestion: dict,
        room: Room
    ) -> Optional[List[Furniture]]:
        """尝试应用优化建议"""
        new_layout = copy.deepcopy(layout)
        
        target_item = next((item for item in new_layout if item.id == target_id), None)
        if not target_item:
            return None

        original_position = (target_item.x, target_item.y)
        target_item.x = suggestion["suggested_x"]
        target_item.y = suggestion["suggested_y"]
        
        if self._is_valid(new_layout, room):
            return new_layout
        
        target_item.x, target_item.y = original_position
        return None

    def _is_valid(self, layout: List[Furniture], room: Room) -> bool:
        """全面有效性检查（新增规则引擎验证）"""
        if not CollisionChecker(layout).validate_all():
            return False

        for item in layout:
            if not room.is_within_bounds(item.x, item.y, item.width, item.height):
                return False

        if not self.constraint_manager.validate(layout):
            return False

        # 规则引擎检查
        engine = RuleEngine(room.config)
        validated_layout = engine.apply_rules(copy.deepcopy(layout), room)
        return validated_layout == layout  # 未被修正才视为有效

class ConstraintManager:
    """约束管理模块"""
    def __init__(self):
        self.constraints = {
            "position": {},      
            "relative": {}       
        }

    def add_position_constraints(self, constraints: Dict[str, tuple]):
        """添加绝对位置约束"""
        self.constraints["position"].update(constraints)

    def add_relative_constraint(self, item_a_id: str, item_b_id: str, min_distance: float, max_distance: float):
        """添加相对位置约束"""
        key = tuple(sorted([item_a_id, item_b_id]))
        self.constraints["relative"][key] = (min_distance, max_distance)

    def is_constrained(self, item_id: str) -> bool:
        """检查是否受位置约束"""
        return item_id in self.constraints["position"]

    def validate(self, layout: List[Furniture]) -> bool:
        """验证所有约束"""
        for item in layout:
            if item.id in self.constraints["position"]:
                req_x, req_y = self.constraints["position"][item.id]
                if not (abs(item.x - req_x) < 0.1 and abs(item.y - req_y) < 0.1):
                    return False
        
        for (id_a, id_b), (min_d, max_d) in self.constraints["relative"].items():
            item_a = next((i for i in layout if i.id == id_a), None)
            item_b = next((i for i in layout if i.id == id_b), None)
            if not item_a or not item_b:
                continue
                
            distance = item_a.polygon.distance(item_b.polygon)
            if not (min_d <= distance <= max_d):
                return False
        
        return True
    

class MultiObjectiveLocalSearch:
    def __init__(self, max_iterations, objective_weights):
        self.max_iter = max_iterations
        self.weights = objective_weights
        self.nm = NelderMead()

    def refine(self, layout, room):
        """多目标Nelder-Mead优化"""
        problem = {
            'fun': self._multi_objective_loss,
            'x0': self._layout_to_vector(layout),
            'bounds': self._get_bounds(layout),
            'args': (room,)
        }
        
        result = minimize(**problem, method='Nelder-Mead', options={'maxiter': self.max_iter})
        
        return self._vector_to_layout(result.x)

    def _multi_objective_loss(self, x, room):
        """多目标损失函数（新增规则修正）"""
        layout = self._vector_to_layout(x)
        engine = RuleEngine(room.config)
        validated_layout = engine.apply_rules(layout, room)  # 强制规则修正
        return (
            -MultiObjectiveScorer.comfort_score(validated_layout, room) * self.weights['comfort'] +
            -MultiObjectiveScorer.space_utilization_score(validated_layout, room) * self.weights['space_utilization'] +
            -MultiObjectiveScorer.aesthetic_score(validated_layout, room) * self.weights['aesthetics']
        )
