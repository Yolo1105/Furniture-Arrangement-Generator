import numpy as np
import math
from heapq import heappush, heappop

class DynamicPathFinder:
    def __init__(self, room_config, grid_resolution=0.5):
        self.room_config = room_config
        self.grid_resolution = grid_resolution
        self.obstacle_grid = None
        self.path_cache = {}
        self._initialize_grid()
        
    def _initialize_grid(self):
        """Initialize an empty grid based on room dimensions"""
        room_width = self.room_config.get("room_width", 10)
        room_height = self.room_config.get("room_height", 10)
        
        self.obstacle_grid = np.zeros((
            int(room_width / self.grid_resolution) + 1,
            int(room_height / self.grid_resolution) + 1
        ))
        
    def update_layout(self, layout):
        """动态更新障碍物网格"""
        # Re-initialize to clear previous obstacles
        self._initialize_grid()
        
        # 带缓冲区的障碍物标记
        for item in layout:
            if hasattr(item, 'x') and hasattr(item, 'y') and \
               hasattr(item, 'width') and hasattr(item, 'height'):
                clearance = getattr(item, "clearance", 0)
                x0 = max(0, int((item.x - clearance) / self.grid_resolution))
                y0 = max(0, int((item.y - clearance) / self.grid_resolution))
                x1 = min(
                    self.obstacle_grid.shape[0] - 1, 
                    int((item.x + item.width + clearance) / self.grid_resolution)
                )
                y1 = min(
                    self.obstacle_grid.shape[1] - 1, 
                    int((item.y + item.height + clearance) / self.grid_resolution)
                )
                
                # Ensure indices are valid
                if 0 <= x0 <= x1 < self.obstacle_grid.shape[0] and 0 <= y0 <= y1 < self.obstacle_grid.shape[1]:
                    self.obstacle_grid[x0:x1+1, y0:y1+1] = 1
        
        # Clear the path cache when layout changes
        self.path_cache = {}

    def find_path(self, start, end):
        """带缓存的A*路径查找"""
        cache_key = (start[0], start[1], end[0], end[1])  # Convert to hashable type
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]
        
        path = self._a_star_search(start, end)
        self.path_cache[cache_key] = path
        return path
    
    def _a_star_search(self, start, end):
        """
        Implements A* search to check if a clear path exists between two points.
        """
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # Convert world coordinates to grid coordinates
        start_node = (int(start[0] / self.grid_resolution), int(start[1] / self.grid_resolution))
        end_node = (int(end[0] / self.grid_resolution), int(end[1] / self.grid_resolution))

        # Check bounds for start and end
        if not (0 <= start_node[0] < self.obstacle_grid.shape[0] and 0 <= start_node[1] < self.obstacle_grid.shape[1]):
            return False
            
        if not (0 <= end_node[0] < self.obstacle_grid.shape[0] and 0 <= end_node[1] < self.obstacle_grid.shape[1]):
            return False

        # Check if start or end are obstacles
        if self.obstacle_grid[start_node] == 1 or self.obstacle_grid[end_node] == 1:
            return False

        open_set = []
        heappush(open_set, (heuristic(start_node, end_node), start_node))
        closed_set = set()
        g_score = {start_node: 0}
        
        while open_set:
            _, current = heappop(open_set)
            
            if current == end_node:
                return True
                
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            # Check all four cardinal directions
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # Check if neighbor is valid
                if not (0 <= neighbor[0] < self.obstacle_grid.shape[0] and 0 <= neighbor[1] < self.obstacle_grid.shape[1]):
                    continue
                    
                # Check if neighbor is an obstacle or already evaluated
                if neighbor in closed_set or self.obstacle_grid[neighbor] == 1:
                    continue
                
                # Calculate new g_score for this neighbor
                tentative_g = g_score.get(current, float('inf')) + 1
                
                # If this is a better path to neighbor
                if tentative_g < g_score.get(neighbor, float('inf')):
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, end_node)
                    heappush(open_set, (f_score, neighbor))
                    
        # No path found
        return False

    def get_bounds(self, item):
        """Helper to get furniture bounds consistently"""
        if hasattr(item, 'get_bounds'):
            return item.get_bounds()
        else:
            return (item.x, item.y, item.width, item.height)
            
    @staticmethod
    def door_accessibility_score(layout, room_config):
        """
        Static method for door accessibility scoring
        """
        path_finder = DynamicPathFinder(room_config)
        path_finder.update_layout(layout)
        
        doors = room_config.get("doors", [])
        if not doors:
            return 10  # If no doors, assume perfect accessibility
            
        room_center = (
            room_config.get("room_width", 10) / 2,
            room_config.get("room_height", 10) / 2
        )
        
        score = 0
        for door in doors:
            door_center = (door[0] + door[2]/2, door[1] + door[3]/2)
            if path_finder.find_path(door_center, room_center):
                score += 10
            else:
                score -= 20
                
        return max(0, score)

    @staticmethod
    def calculate_layout_score(layout, room_config):
        """
        Static method for calculating a comprehensive layout score
        """
        weights = room_config.get("scoring_weights", {
            "bed_window_proximity": 1.0,
            "chair_table_proximity": 1.0,
            "furniture_spacing": 1.0, 
            "door_accessibility": 1.0,
            "alignment": 1.0
        })
        
        score = 0.0

        # (A) Bed-Window Proximity
        windows = room_config.get("windows", [])
        for item in layout:
            if hasattr(item, 'type') and isinstance(item.type, str) and item.type.lower() == "bed":
                if hasattr(item, 'get_bounds'):
                    bounds = item.get_bounds()
                    bed_x, bed_y = bounds[0], bounds[1]
                else:
                    bed_x, bed_y = item.x, item.y
                    
                if windows:
                    wx, wy, wwidth, wheight = windows[0]
                    dist = math.sqrt((bed_x - wx) ** 2 + (bed_y - wy) ** 2)
                    score += weights.get("bed_window_proximity", 1.0) * max(0, 10 - dist)

        # (B) Chair-Table Proximity
        chairs = [f for f in layout if hasattr(f, 'type') and isinstance(f.type, str) and f.type.lower() == "chair"]
        tables = [f for f in layout if hasattr(f, 'type') and isinstance(f.type, str) and f.type.lower() == "table"]
        
        for chair in chairs:
            if hasattr(chair, 'get_bounds'):
                cbounds = chair.get_bounds()
                cx, cy = cbounds[0], cbounds[1]
            else:
                cx, cy = chair.x, chair.y
                
            for table in tables:
                if hasattr(table, 'get_bounds'):
                    tbounds = table.get_bounds()
                    tx, ty = tbounds[0], tbounds[1]
                else:
                    tx, ty = table.x, table.y
                    
                dist = math.sqrt((cx - tx) ** 2 + (cy - ty) ** 2)
                score += weights.get("chair_table_proximity", 1.0) * max(0, 5 - dist)

        # (C) Furniture Spacing
        for i in range(len(layout)):
            for j in range(i + 1, len(layout)):
                item_i, item_j = layout[i], layout[j]
                
                if hasattr(item_i, 'get_bounds') and hasattr(item_j, 'get_bounds'):
                    ibounds = item_i.get_bounds()
                    jbounds = item_j.get_bounds()
                    x1, y1 = ibounds[0], ibounds[1]
                    x2, y2 = jbounds[0], jbounds[1]
                elif hasattr(item_i, 'x') and hasattr(item_i, 'y') and \
                     hasattr(item_j, 'x') and hasattr(item_j, 'y'):
                    x1, y1 = item_i.x, item_i.y
                    x2, y2 = item_j.x, item_j.y
                else:
                    continue
                    
                distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                if distance < 1.0:
                    score += weights.get("furniture_spacing", 1.0) * (distance - 1.0)

        # (D) Door Accessibility
        score += weights.get("door_accessibility", 1.0) * DynamicPathFinder.door_accessibility_score(layout, room_config)

        # (E) Alignment
        for item in layout:
            if hasattr(item, 'get_bounds'):
                bounds = item.get_bounds()
                x, y = bounds[0], bounds[1]
            elif hasattr(item, 'x') and hasattr(item, 'y'):
                x, y = item.x, item.y
            else:
                continue
                
            if abs(x - round(x)) < 0.2:
                score += weights.get("alignment", 1.0)
            if abs(y - round(y)) < 0.2:
                score += weights.get("alignment", 1.0)

        return score
