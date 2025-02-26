import json
from pathlib import Path
from typing import List, Dict, Optional
from core.furniture import Furniture
from core.room import Room
from optimization.genetic.parallel_ga import ParallelGeneticAlgorithm
from optimization.genetic.nsga2 import NSGA2Optimizer
from optimization.local_search import TryFailOptimizer, MultiObjectiveLocalSearch
from evaluation.scorer import MultiObjectiveScorer

class HybridOptimizer:
    def __init__(
        self,
        # 公共参数
        enable_hotstart: bool = False,
        # 单目标模式参数
        ga_population_size: int = 50,
        ga_mutation_rate: float = 0.3,
        ga_crossover_rate: float = 0.7,
        max_local_search_attempts: int = 100,
        # 多目标模式参数
        multi_objective: bool = False,
        objectives: Optional[dict] = None,
        mo_ga_population_size: int = 100,
        max_generations: int = 50,
        local_search_iters: int = 200
    ):
        self.enable_hotstart = enable_hotstart
        self.user_constraints = {}
        self.multi_objective = multi_objective

        # 初始化优化器组件
        if not self.multi_objective:
            # 单目标模式：遗传算法 + TryFail局部搜索
            self.ga = ParallelGeneticAlgorithm(
                population_size=ga_population_size,
                mutation_rate=ga_mutation_rate,
                crossover_rate=ga_crossover_rate
            )
            self.local_optimizer = TryFailOptimizer(max_attempts=max_local_search_attempts)
        else:
            # 多目标模式：NSGA-II + 多目标局部搜索
            self.objectives = objectives or {'comfort': 0.4, 'space_utilization': 0.3, 'aesthetics': 0.3}
            self.ga = NSGA2Optimizer(
                population_size=mo_ga_population_size,
                objectives=list(self.objectives.keys()),
                mutation_rate=0.2
            )
            self.local_optimizer = MultiObjectiveLocalSearch(
                max_iterations=local_search_iters,  # 修正拼写错误：iterations
                objective_weights=self.objectives
            )
            self.pareto_front = []
        self.max_generations = max_generations

    def optimize(self, room: Room, generations: Optional[int] = None) -> List[Furniture]:
        """统一优化入口"""
        if self.multi_objective:
            return self._optimize_multi_objective(room)
        else:
            return self._optimize_single_objective(room, generations or 100)

    def _optimize_single_objective(self, room: Room, generations: int) -> List[Furniture]:
        """单目标优化流程"""
        if self.enable_hotstart and Path("best_layout.json").exists():
            initial_pop = self.load_previous_best("best_layout.json")
            self.ga.population = initial_pop + self.ga._init_population()
        
        ga_result = self.ga.evolve(room, generations)
        final_layout = self.local_optimizer.optimize(ga_result, room, self.user_constraints)  # 传递约束
        self.save_current_best(final_layout)
        return final_layout

    def _optimize_multi_objective(self, room: Room) -> List[Furniture]:
        """多目标优化流程"""
        # NSGA-II生成Pareto前沿
        self.pareto_front = self.ga.evolve(room, self.max_generations)
        
        # 局部搜索优化每个解
        optimized_layouts = [
            self.local_optimizer.refine(solution, room)
            for solution in self.pareto_front
        ]
        
        # 选择最佳折中解
        return self._select_best_compromise(optimized_layouts)

    def _select_best_compromise(self, layouts: List[List[Furniture]]) -> List[Furniture]:
        """多目标模式下的加权评分选择"""
        scores = []
        for layout in layouts:
            comfort = MultiObjectiveScorer.comfort_score(layout)
            space = MultiObjectiveScorer.space_utilization_score(layout)
            aesthetics = MultiObjectiveScorer.aesthetic_score(layout)
            total_score = (
                comfort * self.objectives['comfort'] +
                space * self.objectives['space_utilization'] +
                aesthetics * self.objectives['aesthetics']
            )
            scores.append((total_score, layout))
        return max(scores, key=lambda x: x[0])[1]

    # 公共方法
    def add_constraint(self, constraints: Dict[str, tuple]):
        """添加用户约束（单目标模式使用绝对坐标，多目标需额外处理）"""
        self.user_constraints.update(constraints)

    def save_current_best(self, layout: List[Furniture], filename: str = "best_layout.json"):
        """保存布局（兼容多目标模式）"""
        serialized = [
            {
                "id": item.id,
                "type": item.type.value,
                "x": item.x,
                "y": item.y,
                "width": item.width,
                "height": item.height
            }
            for item in layout
        ]
        with open(filename, 'w') as f:
            json.dump(serialized, f)

    def load_previous_best(self, filename: str) -> List[Furniture]:
        """加载布局（兼容多目标模式）"""
        with open(filename, 'r') as f:
            data = json.load(f)
        return [
            Furniture(
                id=item["id"],
                x=item["x"],
                y=item["y"],
                width=item["width"],
                height=item["height"],
                f_type=item["type"]
            ) for item in data
        ]