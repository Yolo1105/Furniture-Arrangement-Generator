import json
from pathlib import Path
from typing import Dict, Any
from core.furniture import FurnitureType

class ConfigLoader:
    _furniture_config = None
    _room_config = None
    
    @classmethod
    def _load_config(cls, filename: str) -> Dict[str, Any]:
        config_path = Path(__file__).parent.parent / f"configs/{filename}"
        with open(config_path, 'r') as f:
            return json.load(f)

    @classmethod
    def get_furniture_config(cls, f_type: FurnitureType):
        if not cls._furniture_config:
            cls._furniture_config = cls._load_config("furniture_rules.json")
        
        config = cls._furniture_config.get(f_type.value, {})
        # 转换字符串到FurnitureType
        if "must_near" in config:
            config["must_near"] = FurnitureType(config["must_near"])
        return config

    @classmethod
    def get_room_config(cls):
        if not cls._room_config:
            cls._room_config = cls._load_config("room_config.json")
            
            # 坐标系验证
            doors = cls._room_config.get("doors", [])
            windows = cls._room_config.get("windows", [])
            cls._room_config["doors"] = [tuple(map(float, d)) for d in doors]
            cls._room_config["windows"] = [tuple(map(float, w)) for w in windows]
            
        return cls._room_config

    @classmethod
    def get_scoring_weights(cls):
        return cls.get_room_config().get("scoring_weights", {})