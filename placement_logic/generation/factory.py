from typing import Optional, List
from core.furniture import Furniture, FurnitureType
from core.config_loader import ConfigLoader
from core.room import Room

_strategy_registry = {}

def register_strategy(f_type: FurnitureType):
    """装饰器：将策略类与家具类型关联"""
    def decorator(cls):
        _strategy_registry[f_type] = cls.place
        return cls
    return decorator

class FurnitureFactory:
    @staticmethod
    def create(f_type: FurnitureType, room: Room, ref_item: Optional[Furniture] = None) -> Optional[Furniture]:
        """动态生成家具，支持自定义类型扩展"""
        config = ConfigLoader.get_furniture_config(f_type)
        if not config:
            raise ValueError(f"Missing configuration for {f_type}")
        
        # 校验必要字段
        try:
            width, height = config["default_size"]
        except KeyError:
            raise KeyError(f"Config for {f_type} must contain 'default_size'")

        # 获取注册的策略函数
        strategy = _strategy_registry.get(f_type)
        if not strategy:
            raise NotImplementedError(f"No strategy registered for {f_type}")

        # 调用策略生成家具
        return strategy(room, ref_item)

    @staticmethod
    def list_supported_types() -> List[FurnitureType]:
        """返回所有已注册的家具类型"""
        return list(_strategy_registry.keys())