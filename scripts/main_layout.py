import os
import torch
from core.config_loader import ConfigLoader
from generation.wfc_generator import WFCGenerator
from env.layout_env import FurniturePlacementEnv
from model.ppo_agent import FurniturePPOAgent
from visualization.layout_plot import plot_layout

ROOM_PATH = "configs/room_config.json"
FURNITURE_PATH = "configs/furniture_rules.json"
REWARD_PATH = "configs/reward_config.yaml"
MODEL_PATH = "models/final_ppo.pth"

def main():
    os.makedirs("output", exist_ok=True)

    # 1. 加载配置并生成初始布局（WFC）
    room_config = ConfigLoader.get_room_config()
    furniture_config = ConfigLoader.get_furniture_config()
    room = ConfigLoader.get_room_config()
    furniture_list = WFCGenerator(room).generate()

    # 2. 初始化 RL 环境（可传入初始布局）
    env = FurniturePlacementEnv(ROOM_PATH, FURNITURE_PATH, REWARD_PATH, initial_layout=furniture_list)
    state = env.reset()

    # 3. 加载 PPO Agent
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.shape[0]
    agent = FurniturePPOAgent(state_dim=state_dim, action_dim=action_dim)
    agent.load_state_dict(torch.load(MODEL_PATH))
    agent.eval()

    # 4. 推理优化动作
    done = False
    while not done:
        state_tensor = torch.tensor(state, dtype=torch.float32)
        action_vec, _ = agent.act(state_tensor)
        state, _, done, _ = env.step(action_vec)

    # 5. 可视化保存
    plot_layout(env.furniture, room["width"], room["height"],
                save_path="output/final_layout.png",
                title="Final Layout")

    print("✅ Layout generated and saved to output/final_layout.png")

if __name__ == "__main__":
    main()
