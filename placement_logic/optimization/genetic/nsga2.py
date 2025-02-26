import numpy as np
import copy
import multiprocessing
from deap import base, creator, tools
from core.room import Room
from evaluation.scorer import MultiObjectiveScorer
from rules.rule_engine import RuleEngine  

class NSGA2Optimizer:
    def __init__(self, room: Room, population_size: int = 100, max_workers: int = 8, mutation_rate: float = 0.2, crossover_rate: float = 0.7):
        creator.create("FitnessMulti", base.Fitness, weights=(-1.0, 1.0, 1.0))
        creator.create("Individual", list, fitness=creator.FitnessMulti)
        
        self.room = room
        self.toolbox = base.Toolbox()
        self.pool = multiprocessing.Pool(max_workers)
        self._init_genetic_operators()
        
        self.population = self.toolbox.population(n=population_size)
        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("min", np.min, axis=0)
        self.stats.register("avg", np.mean, axis=0)
        self.stats.register("max", np.max, axis=0)

    def _init_genetic_operators(self):
        """配置并行化遗传操作"""
        self.toolbox.register("attr_float", np.random.uniform, 0, 1)
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self._encode_layout)
        self.toolbox.register("map", self.pool.map)
        self.toolbox.register("mate", self._structured_crossover)
        self.toolbox.register("mutate", self._guided_mutation)
        self.toolbox.register("select", tools.selNSGA2)
        self.toolbox.register("evaluate", self._multi_objective_evaluate)

    def _decode_layout(self, vector):
        """从优化向量解码布局，并强制规则修正"""
        layout = []
        n = len(vector) // 2
        for i in range(n):
            x = vector[i] * self.room.width
            y = vector[i + n] * self.room.height
            item = copy.deepcopy(self.room.default_layout[i])
            item.x, item.y = x, y
            layout.append(item)
        return RuleEngine(self.room.config).apply_rules(layout, self.room)  # Apply rule validation

    def _multi_objective_evaluate(self, individual):
        """统一评分逻辑"""
        layout = self._decode_layout(individual)
        return (
            MultiObjectiveScorer.comfort_score(layout, self.room),
            MultiObjectiveScorer.space_utilization_score(layout, self.room),
            MultiObjectiveScorer.aesthetic_score(layout, self.room)
        )
