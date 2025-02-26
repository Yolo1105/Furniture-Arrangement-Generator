import random
import copy
from typing import List
from core.furniture import Furniture
from core.room import Room
from optimization.local_search import TryFailOptimizer  # Ensure structure repair

class StructuredCrossover:
    @staticmethod
    def perform(parent_a: List[Furniture], parent_b: List[Furniture], room: Room):
        """基于家具类型的结构化交叉"""
        type_map_a = {item.type: item for item in parent_a}
        type_map_b = {item.type: item for item in parent_b}
        
        child = []
        for furn_type in set(type_map_a.keys()) | set(type_map_b.keys()):
            if random.random() < 0.7:
                donor = random.choice([type_map_a, type_map_b])
                if furn_type in donor:
                    new_item = copy.deepcopy(donor[furn_type])
                    new_item.x += random.uniform(-0.5, 0.5)
                    new_item.y += random.uniform(-0.5, 0.5)
                    child.append(new_item)
        
        return TryFailOptimizer.repair(child, room)  # Ensure repaired layout
