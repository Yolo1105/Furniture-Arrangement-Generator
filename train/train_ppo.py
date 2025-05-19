import os
import torch
import torch.nn as nn
import torch.optim as optim
import imageio
from env.layout_env import FurniturePlacementEnv
from model.ppo_agent import FurniturePPOAgent
from train.curriculum_scheduler import CurriculumScheduler
from visualization.layout_plot import plot_layout

# ==== 超参数 ====
NUM_EPISODES = 200
GAMMA = 0.99
CLIP_EPS = 0.2
LEARNING_RATE = 3e-4
UPDATE_INTERVAL = 4
RENDER_EVERY_N_EPISODES = 25
RECORD_LAST_N_EPISODES = 10
DEFAULT_DPI = 150
ROOM_WIDTH = 10  # 仅用于绘图
ROOM_HEIGHT = 10

# ==== 返回值计算 ====
def compute_returns(rewards, gamma=0.99):
    returns = []
    R = 0
    for r in reversed(rewards):
        R = r + gamma * R
        returns.insert(0, R)
    return returns

# ==== 主训练入口 ====
def train():
    os.makedirs("output", exist_ok=True)
    os.makedirs("videos", exist_ok=True)

    scheduler = CurriculumScheduler("configs/curriculum_schedule.yaml")
    env = FurniturePlacementEnv(
        room_config_path="configs/room_config.json",
        furniture_config_path="configs/furniture_rules.json",
        reward_config_path="configs/reward_config.yaml"
    )

    state_dim = len(env.reset())
    action_dim = env.action_space.shape[0]
    agent = FurniturePPOAgent(state_dim, action_dim)
    optimizer = optim.Adam(agent.parameters(), lr=LEARNING_RATE)

    frames = []

    for episode in range(NUM_EPISODES):
        # ✅ Curriculum 阶段调度
        scheduler.update(episode)
        phase = scheduler.get_current_config()
        env.set_max_furniture(phase["max_furniture"])
        env.set_rotation_enabled(phase["allow_rotation"])
        env.update_reward_weights(phase["reward_weights"])

        state = torch.tensor(env.reset(), dtype=torch.float32)
        rewards, log_probs, values, states, actions = [], [], [], [], []
        done = False

        while not done:
            action_vec, log_prob = agent.act(state)
            next_state_raw, reward, done, _ = env.step(action_vec)
            next_state = torch.tensor(next_state_raw, dtype=torch.float32)

            value = agent.forward(state)[1]
            states.append(state)
            actions.append(torch.tensor(action_vec, dtype=torch.float32))
            log_probs.append(log_prob)
            values.append(value)
            rewards.append(torch.tensor(reward, dtype=torch.float32))
            state = next_state

            if episode >= NUM_EPISODES - RECORD_LAST_N_EPISODES:
                frame_path = "output/temp_frame.png"
                plot_layout(env.furniture, ROOM_WIDTH, ROOM_HEIGHT,
                            save_path=frame_path,
                            title=f"Episode {episode+1}",
                            dpi=DEFAULT_DPI)
                frames.append(imageio.v2.imread(frame_path))

        # PPO 更新
        returns = compute_returns(rewards, GAMMA)
        log_probs = torch.stack(log_probs)
        values = torch.stack(values).squeeze()
        actions = torch.stack(actions)
        returns = torch.stack(returns).detach()
        advantages = returns - values.detach()

        for _ in range(UPDATE_INTERVAL):
            log_probs_new, values_new, entropy = agent.evaluate(torch.stack(states), actions)
            ratios = torch.exp(log_probs_new - log_probs.detach())
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1.0 - CLIP_EPS, 1.0 + CLIP_EPS) * advantages
            actor_loss = -torch.min(surr1, surr2).mean()
            critic_loss = (returns - values_new).pow(2).mean()
            loss = actor_loss + 0.5 * critic_loss - 0.01 * entropy.mean()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        total_reward = sum([r.item() for r in rewards])
        print(f"🎮 Episode {episode+1}/{NUM_EPISODES} | Total reward: {total_reward:.2f}")

        if (episode + 1) % RENDER_EVERY_N_EPISODES == 0:
            save_path = f"output/episode_{episode+1}.png"
            plot_layout(env.furniture, ROOM_WIDTH, ROOM_HEIGHT,
                        save_path=save_path,
                        title=f"Episode {episode+1}",
                        dpi=DEFAULT_DPI)
            print(f"📸 Saved layout to {save_path}")

    # ✅ 训练后保存动图
    gif_path = "videos/final_ppo_run.gif"
    if frames:
        imageio.mimsave(gif_path, frames, fps=2)
        print(f"🌀 Saved training gif to {gif_path}")
    else:
        print("⚠️ No frames recorded. GIF not saved.")

if __name__ == "__main__":
    train()
