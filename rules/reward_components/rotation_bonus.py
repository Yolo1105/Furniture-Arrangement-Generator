import math

def get_rotation_alignment_reward(furniture, target_angle, threshold=20):
    """
    Reward furniture for being aligned with target_angle (0, 90, 180, 270).
    """
    diff = abs(furniture.rotation - target_angle) % 360
    diff = min(diff, 360 - diff)  # smallest angle difference
    if diff <= threshold:
        return 1.0 - diff / threshold  # scaled reward
    return 0.0
