import random
from typing import List
from core.furniture import Furniture
from core.room import Room

class GuidedMutation:
    @staticmethod
    def perform(layout: List[Furniture], room: Room):
        """基于规则引导的智能变异"""
        for item in layout:
            if random.random() < 0.1:
                # 沿关联方向移动
                related_items = [i for i in layout if i.type in item.must_near]
                if related_items:
                    target = random.choice(related_items)
                    item.x = target.x + random.uniform(-1, 1)
                    item.y = target.y + random.uniform(-1, 1)
                else:
                    item.x += random.uniform(-1, 1)
                    item.y += random.uniform(-1, 1)
                
                # 边界修正
                item.x = max(0, min(room.width - item.width, item.x))
                item.y = max(0, min(room.height - item.height, item.y))
        return layout
