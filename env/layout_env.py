import gym
import numpy as np
from core.room import Room
from core.furniture import Furniture
from core.config_loader import load_room_config, load_furniture_config
from core.layout_state import encode_layout_state
from env.reward_function import compute_total_reward, compute_total_reward_from_dict
import random

class FurniturePlacementEnv(gym.Env):
    def __init__(self, room_config_path, furniture_config_path, reward_config_path):
        super().__init__()
        self.room_config_path = room_config_path
        self.furniture_config_path = furniture_config_path
        self.reward_config_path = reward_config_path

        self.room: Room = None
        self.furniture: list[Furniture] = []
        self.current_index = 0
        self.episode_rewards = []
        self.allow_rotation = True
        self.reward_fn = compute_total_reward(reward_config_path)

        self._load_configs()
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(self._get_obs().shape[0],), dtype=np.float32)
        self.action_space = gym.spaces.Box(low=np.array([0.0, 0.0, 0]), high=np.array([1.0, 1.0, 3]), dtype=np.float32)  # x, y, rotation index

    def _load_configs(self):
        self.room = load_room_config(self.room_config_path)
        self.furniture = load_furniture_config(self.furniture_config_path)
        random.shuffle(self.furniture)
        self.current_index = 0
        self.episode_rewards = []

    def reset(self):
        self._load_configs()
        return self._get_obs()

    def _get_obs(self):
        return encode_layout_state(self.room, self.furniture, self.current_index)

    def step(self, action):
        if self.current_index >= len(self.furniture):
            return self._get_obs(), 0.0, True, {}

        current_f = self.furniture[self.current_index]
        x, y, rot_idx = action
        room_w, room_h = self.room.width, self.room.height
        current_f.x = x * room_w
        current_f.y = y * room_h

        if self.allow_rotation:
            current_f.rotation = int(rot_idx) * 90
        else:
            current_f.rotation = 0

        reward = self.reward_fn(self.room, self.furniture, current_f)
        self.episode_rewards.append(reward)
        self.current_index += 1
        done = self.current_index >= len(self.furniture)
        return self._get_obs(), reward, done, {}

    # 🧠 外部调度支持接口：
    def set_max_furniture(self, max_num):
        self.furniture = self.furniture[:max_num]

    def set_rotation_enabled(self, enabled: bool):
        self.allow_rotation = enabled

    def update_reward_weights(self, weights_dict: dict):
        self.reward_fn = compute_total_reward_from_dict(weights_dict)