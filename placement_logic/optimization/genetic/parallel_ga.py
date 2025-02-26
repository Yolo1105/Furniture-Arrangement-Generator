import random
import copy
import multiprocessing
from typing import List
from core.furniture import Furniture
from core.room import Room
from evaluation.scorer import RuleIntegratedScorer  # Updated scorer import
from generation.collision.buffer_check import CollisionChecker
from crossover import StructuredCrossover  # Modularized crossover
from mutation import GuidedMutation  # Modularized mutation

class ParallelGeneticAlgorithm:
    def __init__(self, population_size: int, mutation_rate: float, crossover_rate: float, room: Room, max_workers: int = 4):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.room = room
        self.max_workers = max_workers
        self.population = self._init_population()
        
    def _init_population(self) -> List[List[Furniture]]:
        """初始化种群：基于规则引擎生成合规布局"""
        return [self._generate_valid_layout() for _ in range(self.population_size)]
    
    def _generate_valid_layout(self) -> List[Furniture]:
        """生成通过基础检测的布局"""
        while True:
            layout = self.room.generate_random_layout()
            if CollisionChecker(layout).validate_all():
                return layout
    
    def evolve(self, generations: int) -> List[Furniture]:
        """多进程进化流程"""
        with multiprocessing.Pool(self.max_workers) as pool:
            for _ in range(generations):
                copied_pop = [copy.deepcopy(ind) for ind in self.population]  # Deep copy to avoid shared state
                scores = pool.map(self._evaluate, copied_pop)
                
                sorted_pop = [x for _, x in sorted(zip(scores, copied_pop), reverse=True)]
                elites = sorted_pop[:int(self.population_size * 0.5)]
                
                children = []
                while len(children) < self.population_size - len(elites):
                    parents = random.choices(elites, k=2)
                    child = StructuredCrossover.perform(parents[0], parents[1], self.room)  # Use modularized crossover
                    child = GuidedMutation.perform(child, self.room)  # Use modularized mutation
                    children.append(child)
                
                self.population = elites + children
        
        return self.get_best_solution()
    
    def _evaluate(self, layout: List[Furniture]) -> float:
        """适应度函数：改用 scorer.py"""
        base_score = RuleIntegratedScorer.calculate_layout_score(layout, self.room.config)
        uniqueness = len({f"{item.x},{item.y}" for item in layout}) / len(layout)
        return base_score * (1 + 0.2 * uniqueness)
    
    def get_best_solution(self) -> List[Furniture]:
        """获取历史最优解"""
        return max(self.population, key=lambda x: self._evaluate(x))
