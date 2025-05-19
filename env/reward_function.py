import yaml
from rules.reward_components.alignment import alignment_reward
from rules.reward_components.clearance import clearance_reward
from rules.reward_components.rotation_bonus import get_rotation_alignment_reward
from rules.reward_components.window_bonus import get_window_proximity_reward
from rules.reward_components.path_score import compute_astar_path_score
from rules.reward_components.relation_rewards import must_be_near_reward, must_face_reward
from rules.rule_stats_logger import RuleStatsLogger

logger = RuleStatsLogger()

def compute_total_reward(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return compute_total_reward_from_dict(config)

def compute_total_reward_from_dict(config: dict):
    """
    构建一个 reward_fn: (room, furniture_list, current_furniture) → float
    使用传入的 reward config dict 而非读取文件
    """
    def reward_fn(room, furniture_list, current_furniture):
        total = 0.0

        if config.get("clearance_weight", 0) > 0:
            score = clearance_reward(room, current_furniture, furniture_list)
            logger.record_reward("clearance", score)
            total += config["clearance_weight"] * score

        if config.get("alignment_weight", 0) > 0:
            score = alignment_reward(current_furniture, room)
            logger.record_reward("alignment", score)
            total += config["alignment_weight"] * score

        if config.get("rotation_weight", 0) > 0:
            score = get_rotation_alignment_reward(current_furniture, target_angle=0)
            logger.record_reward("rotation", score)
            total += config["rotation_weight"] * score

        if config.get("window_weight", 0) > 0:
            score = get_window_proximity_reward(current_furniture, room.windows)
            logger.record_reward("window", score)
            total += config["window_weight"] * score

        if config.get("path_weight", 0) > 0:
            score = compute_astar_path_score(room.to_grid(), room.door_position, (current_furniture.x, current_furniture.y))
            logger.record_reward("path", score)
            total += config["path_weight"] * score

        if config.get("near_weight", 0) > 0:
            score = must_be_near_reward(current_furniture, furniture_list)
            logger.record_reward("near", score)
            total += config["near_weight"] * score

        if config.get("face_weight", 0) > 0:
            score = must_face_reward(current_furniture, furniture_list)
            logger.record_reward("face", score)
            total += config["face_weight"] * score

        return total

    return reward_fn