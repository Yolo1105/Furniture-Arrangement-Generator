import os
import json
import argparse
import yaml
from core.config_loader import load_room_from_json
from core.layout_state import Layout
from evaluation.scorer import MultiObjectiveScorer

def load_weights_from_yaml(path):
    if not os.path.exists(path):
        print(f"⚠️ Config file not found: {path}")
        return {}
    with open(path, "r") as f:
        config = yaml.safe_load(f)
        return config.get("layout_score_weights", {})

def main():
    parser = argparse.ArgumentParser(description="Evaluate layout score")
    parser.add_argument("--layout", type=str, default="output/final_layout.json", help="Path to layout JSON")
    parser.add_argument("--room_config", type=str, default="configs/room_config.json", help="Path to room config")
    parser.add_argument("--reward_config", type=str, default="configs/reward_config.yaml", help="Path to reward config (YAML)")
    args = parser.parse_args()

    # 1. 加载房间与布局
    room = load_room_from_json(args.room_config)
    with open(args.layout, "r") as f:
        layout_data = json.load(f)
    layout = Layout.from_dict(layout_data)

    # 2. 加载奖励配置
    weights = load_weights_from_yaml(args.reward_config)
    scorer = MultiObjectiveScorer(room=room, weights=weights)

    # 3. 计算得分
    score_details = scorer.compute_all(layout)
    total = scorer.total_score(score_details)

    print("🎯 Layout Evaluation")
    print("----------------------------")
    for k, v in score_details.items():
        print(f"{k:<25}: {v:.4f}")
    print(f"\n✅ Total Score: {total:.4f}")

if __name__ == "__main__":
    main()
