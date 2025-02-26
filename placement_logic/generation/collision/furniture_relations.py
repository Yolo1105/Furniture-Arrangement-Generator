"""
Defines the relationships between different furniture types.
Used primarily during initial layout generation and validation.
"""
from typing import Dict, List, Any, Optional, Union

# Dictionary mapping furniture types to their relationship rules
FURNITURE_RELATIONS = {
    "SOFA": {
        "must_near": ["COFFEE_TABLE"],  # Furniture types that should be nearby
        "facing": {
            "type": "TV_STAND",
            "threshold": 30  # Maximum angle deviation in degrees
        }
    },
    "BED": {
        "must_near": ["WARDROBE"],
        "clearance": 1.2  # Minimum clearance in meters
    },
    "CHAIR": {
        "must_near": ["DESK", "TABLE"],
        "facing": {
            "type": "DESK",
            "threshold": 45
        }
    },
    "TV_STAND": {
        "facing": {
            "type": "SOFA",
            "threshold": 35
        }
    },
    "COFFEE_TABLE": {
        "must_near": ["SOFA"],
        "clearance": 0.4  # Close to sofa
    },
    "NIGHTSTAND": {
        "must_near": ["BED"],
        "clearance": 0.3  # Very close to bed
    },
    "WARDROBE": {
        "clearance": 1.0,  # Need space for doors
        "avoid_facing": ["BED"]  # Avoid having doors open toward bed
    },
    "BOOKSHELF": {
        "must_near": ["WALL"],  # Should be against a wall
        "clearance": 0.8  # Need space to access books
    },
    "DESK": {
        "must_near": ["CHAIR"],
        "clearance": 0.7  # Space for chair and leg room
    },
    "TABLE": {
        "must_near": ["CHAIR"],
        "clearance": 0.8  # Space for chairs around
    }
}

# Compatibility matrix: 1 = compatible, 0 = neutral, -1 = avoid placing together
COMPATIBILITY_MATRIX: Dict[tuple, int] = {
    ("SOFA", "TV_STAND"): 1,
    ("SOFA", "COFFEE_TABLE"): 1,
    ("BED", "NIGHTSTAND"): 1,
    ("BED", "WARDROBE"): 0,
    ("BED", "TV_STAND"): -1,  # Typically avoid TVs in sleeping areas
    ("DESK", "CHAIR"): 1,
    ("TABLE", "CHAIR"): 1,
    ("BOOKSHELF", "DESK"): 1,
    ("NIGHTSTAND", "LAMP"): 1
}

# Furniture groups for layout generation
FURNITURE_GROUPS: Dict[str, List[str]] = {
    "living_area": ["SOFA", "TV_STAND", "COFFEE_TABLE"],
    "dining_area": ["TABLE", "CHAIR"],
    "work_area": ["DESK", "CHAIR", "BOOKSHELF"],
    "sleeping_area": ["BED", "NIGHTSTAND", "WARDROBE"]
}

def get_relation_rule(furniture_type: str) -> Dict[str, Any]:
    """Get relation rules for a specific furniture type"""
    # Handle both string types and enum types with name attribute
    if hasattr(furniture_type, 'name'):
        type_name = furniture_type.name
    else:
        type_name = str(furniture_type)
        
    return FURNITURE_RELATIONS.get(type_name, {})

def get_compatibility(type1: Any, type2: Any) -> int:
    """Return compatibility score between two furniture types"""
    # Handle both string types and enum types with name attribute
    type1_name = type1.name if hasattr(type1, 'name') else str(type1)
    type2_name = type2.name if hasattr(type2, 'name') else str(type2)
    
    key = (type1_name, type2_name)
    reverse_key = (type2_name, type1_name)
    
    if key in COMPATIBILITY_MATRIX:
        return COMPATIBILITY_MATRIX[key]
    elif reverse_key in COMPATIBILITY_MATRIX:
        return COMPATIBILITY_MATRIX[reverse_key]
    return 0  # Default: neutral

def get_furniture_group(furniture_type: Any) -> Optional[str]:
    """Get the functional group a furniture type belongs to"""
    # Handle both string types and enum types with name attribute
    type_name = furniture_type.name if hasattr(furniture_type, 'name') else str(furniture_type)
    
    for group, types in FURNITURE_GROUPS.items():
        if type_name in types:
            return group
    return None

def get_clearance(furniture_type: Any) -> float:
    """Get the recommended clearance for a furniture type"""
    rule = get_relation_rule(furniture_type)
    return rule.get("clearance", 0.5)  # Default 0.5m if not specified

def should_face(furniture_type: Any, target_type: Any) -> Optional[Dict[str, Any]]:
    """Check if furniture_type should face target_type"""
    rule = get_relation_rule(furniture_type)
    facing = rule.get("facing", None)
    
    if facing:
        target_name = target_type.name if hasattr(target_type, 'name') else str(target_type)
        if facing.get("type") == target_name:
            return facing
    return None

def must_be_near(furniture_type: Any, target_type: Any) -> bool:
    """Check if furniture_type must be near target_type"""
    rule = get_relation_rule(furniture_type)
    must_near = rule.get("must_near", [])
    
    target_name = target_type.name if hasattr(target_type, 'name') else str(target_type)
    return target_name in must_near
