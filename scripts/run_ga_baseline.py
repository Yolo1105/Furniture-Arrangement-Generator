# scripts/run_ga_baseline.py

from core.config_loader import ConfigLoader
from generation.wfc_generator import WFCGenerator
from optimization.genetic.parallel_ga import ParallelGA
from evaluation.scorer import compute_layout_score
from visualization.layout_plot import plot_layout
import os

def main():
    room = ConfigLoader.get_room_config()
    reward_weights = ConfigLoader.get_reward_config().get("weights", {})

    # Step 1: 初始布局生成（WFC）
    initial_layout = WFCGenerator(room).generate()

    # Step 2: GA优化（以WFC为种子）
    ga = ParallelGA(room, reward_weights)
    best_layout = ga.optimize(initial_layout=initial_layout, generations=20)

    # Step 3: 打分与可视化
    score = compute_layout_score(best_layout, room)
    os.makedirs("output", exist_ok=True)
    plot_layout(best_layout, room["width"], room["height"],
                save_path="output/ga_baseline_layout.png",
                title=f"GA Result | Score: {score:.2f}")

    print(f"✅ GA baseline completed. Score: {score:.2f}")

if __name__ == "__main__":
    main()
