import json
from pathlib import Path
from typing import Dict, Any
from core.furniture import FurnitureType

# ✅ 添加：统一的家具类型列表（供 layout_state 使用）
FURNITURE_TYPES = [ft.value for ft in FurnitureType]

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
        if "must_near" in config and config["must_near"] is not None:
            config["must_near"] = FurnitureType(config["must_near"])
        return config

    @classmethod
    def get_room_config(cls):
        if not cls._room_config:
            cls._room_config = cls._load_config("room_config.json")

            def validate_entry(entry):
                if len(entry) != 4:
                    print(f"⚠️ Invalid door/window entry found: {entry}")
                    return None
                return tuple(map(float, entry))

            cls._room_config["doors"] = [validate_entry(d) for d in cls._room_config.get("doors", []) if validate_entry(d)]
            cls._room_config["windows"] = [validate_entry(w) for w in cls._room_config.get("windows", []) if validate_entry(w)]
        return cls._room_config

    @classmethod
    def get_scoring_weights(cls):
        return cls.get_room_config().get("scoring_weights", {})
