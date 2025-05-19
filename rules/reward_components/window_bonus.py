def get_window_proximity_reward(furniture, windows, max_distance=2.0):
    """
    Reward furniture (like desks or beds) for being near a window.
    windows: list of (x, y) center positions
    """
    fx = furniture.x + furniture.width / 2
    fy = furniture.y + furniture.height / 2
    min_dist = float("inf")
    for wx, wy in windows:
        dist = ((fx - wx) ** 2 + (fy - wy) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
    if min_dist <= max_distance:
        return 1.0 - (min_dist / max_distance)
    return 0.0
