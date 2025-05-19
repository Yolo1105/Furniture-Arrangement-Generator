import numpy as np
from typing import List
from core.furniture import Furniture
from core.room import Room
from core.config_loader import FURNITURE_TYPES  # 假设你有一个类型列表常量

MAX_FURNITURE = 12     # 最大家具数（固定维度）
TYPE_VEC_LEN = len(FURNITURE_TYPES)  # 每种家具的 one-hot 类型长度

def encode_furniture(f: Furniture):
    """
    Encode a single Furniture object as a vector:
    [x, y, width, height, rotation, type_onehot...]
    Normalized to room size
    """
    vec = [
        f.x,
        f.y,
        f.width,
        f.height,
        f.rotation / 360.0
    ]
    one_hot = [0] * TYPE_VEC_LEN
    if f.type in FURNITURE_TYPES:
        one_hot[FURNITURE_TYPES.index(f.type)] = 1
    return vec + one_hot

def encode_layout_state(room: Room, furniture_list: List[Furniture], current_index: int):
    """
    Encode full state for PPO: current furniture + already placed furniture
    Output shape: (MAX_FURNITURE * feature_len,)
    """
    feature_vecs = []
    placed = furniture_list[:current_index]
    current = furniture_list[current_index] if current_index < len(furniture_list) else None

    # Encode already-placed furniture
    for f in placed:
        vec = encode_furniture(f)
        normed = [x / room.width if i % 2 == 0 else x / room.height for i, x in enumerate(vec[:4])]
        feature_vecs.append(normed + vec[4:])  # normalize x/y/w/h, keep rotation/type

    # Pad with zeros if less than MAX_FURNITURE - 1
    while len(feature_vecs) < MAX_FURNITURE - 1:
        feature_vecs.append([0] * (5 + TYPE_VEC_LEN))

    # Encode current furniture to place
    if current:
        current_vec = encode_furniture(current)
        normed = [x / room.width if i % 2 == 0 else x / room.height for i, x in enumerate(current_vec[:4])]
        current_vec = normed + current_vec[4:]
    else:
        current_vec = [0] * (5 + TYPE_VEC_LEN)

    feature_vecs.append(current_vec)

    # Flatten
    flat = [x for vec in feature_vecs for x in vec]
    return np.array(flat, dtype=np.float32)
