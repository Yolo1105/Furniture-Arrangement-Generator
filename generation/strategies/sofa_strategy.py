# generation/strategies/sofa_strategy.py
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
import random
from tv_stand_strategy import TvStandStrategy

class SofaStrategy:
    @staticmethod
    def place(room, existing_items):
        """
        沙发策略：
        1. 优先在 `living_room` 区域放置。
        2. 如果有 `TV_STAND`，则与其对齐放置。
        3. 无 `TV_STAND`，则智能选择墙面靠放。
        """
        config = ConfigLoader.get_furniture_config(FurnitureType.SOFA)
        width, height = config["default_size"]

        # 优先在 `living_room` 放置
        if hasattr(room, "zones"):
            living_room_zones = [z for z in room.zones if z['type'] == 'living_room']
            if living_room_zones:
                zone = random.choice(living_room_zones)
                return Furniture(
                    random.uniform(zone['x1'], zone['x2'] - width),
                    random.uniform(zone['y1'], zone['y2'] - height),
                    width,
                    height,
                    FurnitureType.SOFA
                )

        # 查找 TV_STAND
        tv_stand = next((item for item in existing_items if item.type == FurnitureType.TV_STAND), None)
        if tv_stand:
            return Furniture(
                tv_stand.x,
                tv_stand.y - height - 0.5,
                width,
                height,
                FurnitureType.SOFA
            )
        if not tv_stand:
            tv_stand = TvStandStrategy.place(room, existing_items)

        # 靠墙放置
        return Furniture(
            (room.width - width) / 2,
            1.0,
            width,
            height,
            FurnitureType.SOFA
        )
