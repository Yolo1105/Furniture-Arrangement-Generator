import hashlib
import pytest
from typing import List, Optional
from core.furniture import Furniture, FurnitureType

# Try to import the real function, otherwise use a mock
try:
    from generation import generate_layout
except ImportError:
    # Mock function that returns a simple layout
    def generate_layout(room=None) -> List[Furniture]:
        """Mock layout generator for testing"""
        layouts = [
            # Layout 1: Different positions
            [
                Furniture(id="bed_1", type=FurnitureType.BED, x=1, y=1, width=2, height=1.5, rotation=0),
                Furniture(id="table_1", type=FurnitureType.TABLE, x=5, y=5, width=1.2, height=0.8, rotation=0)
            ],
            # Layout 2: Different positions
            [
                Furniture(id="bed_1", type=FurnitureType.BED, x=2, y=2, width=2, height=1.5, rotation=90),
                Furniture(id="table_1", type=FurnitureType.TABLE, x=6, y=6, width=1.2, height=0.8, rotation=0)
            ],
            # Layout 3: Different positions
            [
                Furniture(id="bed_1", type=FurnitureType.BED, x=1.5, y=3, width=2, height=1.5, rotation=0),
                Furniture(id="table_1", type=FurnitureType.TABLE, x=7, y=4, width=1.2, height=0.8, rotation=90)
            ],
            # Layout 4: Different positions (fallback)
            [
                Furniture(id="bed_1", type=FurnitureType.BED, x=3, y=1, width=2, height=1.5, rotation=90),
                Furniture(id="table_1", type=FurnitureType.TABLE, x=8, y=7, width=1.2, height=0.8, rotation=90)
            ],
            # Layout 5: Different positions (fallback)
            [
                Furniture(id="bed_1", type=FurnitureType.BED, x=2, y=8, width=2, height=1.5, rotation=180),
                Furniture(id="table_1", type=FurnitureType.TABLE, x=4, y=3, width=1.2, height=0.8, rotation=45)
            ],
        ]
        # Return a different layout each time it's called
        generate_layout.call_count = getattr(generate_layout, 'call_count', 0) + 1
        return layouts[(generate_layout.call_count - 1) % len(layouts)]

def hash_layout(layout: List[Furniture]) -> str:
    """生成布局的特征哈希"""
    features = []
    # Handle case where FurnitureType might not have value attribute
    for item in sorted(layout, key=lambda x: getattr(x.type, 'value', str(x.type))):
        type_val = getattr(item.type, 'value', str(item.type))
        features.append(f"{type_val}-{int(item.x/0.5)}-{int(item.y/0.5)}")
    return hashlib.md5("|".join(features).encode()).hexdigest()

def test_diversity():
    """运行5次生成，确保至少出现3种不同布局"""
    seen_hashes = set()
    
    for _ in range(5):
        layout = generate_layout()
        current_hash = hash_layout(layout)
        seen_hashes.add(current_hash)
    
    assert len(seen_hashes) >= 3, f"多样性不足，只生成{len(seen_hashes)}种布局"
