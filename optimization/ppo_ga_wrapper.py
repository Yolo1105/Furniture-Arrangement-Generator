import os
import json
import yaml
from optimization.genetic.parallel_ga import ParallelGeneticAlgorithm
from optimization.genetic.nsga2 import NSGA2Optimizer
from optimization.local_search import MultiObjectiveLocalSearch
from core.config_loader import load_room_from_json
from core.layout_state import Layout
from evaluation.scorer import MultiObjectiveScorer
from utils.logger import log_info


def load_reward_weights_from_yaml(yaml_path: str) -> dict:
    """从 reward_config.yaml 中提取 layout_score_weights"""
    if not os.path.exists(yaml_path):
        log_info(f"⚠️ Reward config file not found at {yaml_path}, using default weights.")
        return {}

    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)
    weights = config.get("layout_score_weights", {})
    log_info(f"✅ Loaded reward weights from YAML: {weights}")
    return weights


class PPOGABoostedOptimizer:
    def __init__(self,
                 room_config_path: str,
                 reward_config_path: str = None,
                 use_nsga: bool = False,
                 objectives: dict = None,
                 seed_layout_path: str = "output/best_layout.json",
                 max_seeds: int = 10):
        self.room = load_room_from_json(room_config_path)
        self.use_nsga = use_nsga

        # 优先使用外部 reward 配置
        if reward_config_path:
            yaml_weights = load_reward_weights_from_yaml(reward_config_path)
            self.objectives = yaml_weights if yaml_weights else objectives
        else:
            self.objectives = objectives or {
                "comfort": 1.0,
                "spacing": 1.0,
                "alignment": 1.0,
                "accessibility": 1.0,
            }

        self.seed_layouts = []
        self._init_seed_population(seed_layout_path, max_seeds)

    def _init_seed_population(self, seed_layout_path: str, max_seeds: int):
        """从 PPO 输出中加载初始 layout（支持 JSON 文件）"""
        if os.path.exists(seed_layout_path):
            with open(seed_layout_path) as f:
                data = json.load(f)
                layout = Layout.from_dict(data)
                self.seed_layouts.append(layout)
                log_info("✅ PPO layout loaded as seed for GA.")
        else:
            log_info("⚠️ No PPO layout found. Using random initialization.")
        self.seed_layouts = self.seed_layouts[:max_seeds]

    def run(self, generations=10, population_size=20):
        if self.use_nsga:
            return self._run_nsga(generations, population_size)
        else:
            return self._run_ga(generations, population_size)

    def _run_ga(self, generations, population_size):
        ga = ParallelGeneticAlgorithm(
            room=self.room,
            population_size=population_size,
            seed_layouts=self.seed_layouts
        )
        result = ga.evolve(generations=generations)
        result.save("output/ga_final.json")
        return result

    def _run_nsga(self, generations, population_size):
        scorer = MultiObjectiveScorer(room=self.room, weights=self.objectives)
        nsga = NSGA2Optimizer(
            room=self.room,
            population_size=population_size,
            seed_layouts=self.seed_layouts,
            objective_fn=scorer
        )
        pareto_front = nsga.evolve(generations=generations)

        # 局部搜索精修
        refined = []
        local = MultiObjectiveLocalSearch(self.room, scorer)
        for ind in pareto_front:
            improved = local.refine(ind)
            refined.append(improved)

        log_info(f"✅ Refined {len(refined)} layouts after NSGA-II")
        return refined
