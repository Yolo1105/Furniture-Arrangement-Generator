from core.room import Room
from generation.initial_placer import InitialPlacer
from rules.rule_engine import RuleEngine
from optimization.genetic.parallel_ga import ParallelGeneticAlgorithm
from visualization.plotter import visualize_layout
from core.furniture import FurnitureType


def main():
    # 初始化房间
    room_config = {
        "width": 15,
        "height": 12,
        "doors": [[5, 0, 2, 1]],
        "windows": [[3, 12, 2, 1]]
    }
    room = Room(room_config["width"], room_config["height"], room_config)

    # 生成初始布局
    placer = InitialPlacer()
    furniture_types = [
        FurnitureType.BED,
        FurnitureType.SOFA,
        FurnitureType.TABLE,
        FurnitureType.CHAIR
    ]
    initial_layout = placer.generate(room, furniture_types)

    # 应用规则
    rule_engine = RuleEngine()
    rule_based_layout = rule_engine.apply_rules(initial_layout, room)

    # 优化
    ga = ParallelGeneticAlgorithm(
        population_size=20,
        mutation_rate=0.1,
        room=room
    )
    optimized_layout = ga.evolve(50)

    # 可视化
    visualize_layout(optimized_layout, room_config)

if __name__ == "__main__":
    main()