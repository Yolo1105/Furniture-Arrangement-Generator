from evaluation.pathfinder import astar

def compute_astar_path_score(room_grid, start, goal):
    """
    Computes a normalized path score between two points.
    - Returns 1.0 if path exists and is short.
    - Returns 0.0 if path is blocked.
    """
    path = astar(room_grid, start, goal)
    if path:
        length = len(path)
        max_len = room_grid.width + room_grid.height
        return max(0.0, 1.0 - (length / max_len))
    return 0.0
