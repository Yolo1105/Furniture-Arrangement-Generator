import os
from train.curriculum_scheduler import CurriculumScheduler
from env.layout_env import LayoutEnv
from model.ppo_agent import PPOAgent
from utils.visualizer import save_gif_from_frames

def run_curriculum_training(config):
    scheduler = CurriculumScheduler(config["curriculum_schedule_path"])

    env = LayoutEnv(config["room_config_path"])
    agent = PPOAgent(env.observation_space, env.action_space)

    total_steps = config.get("total_steps", 10000)
    save_every = config.get("save_every", 1000)

    reward_history = []
    gif_frames = []

    for step in range(total_steps):
        scheduler.update(step)
        phase = scheduler.get_current_config()

        # ✅ 动态配置环境
        env.set_max_furniture(phase.get("max_furniture", 5))
        env.set_rotation_enabled(phase.get("allow_rotation", False))
        env.update_reward_weights(phase.get("reward_weights", {}))

        obs = env.reset()
        done = False
        ep_reward = 0

        while not done:
            action = agent.select_action(obs)
            obs, reward, done, info = env.step(action)
            agent.store_transition(obs, action, reward, done)
            ep_reward += reward

            if config.get("record_gif", False):
                frame = env.render(mode="rgb_array")
                gif_frames.append(frame)

        agent.train()
        reward_history.append(ep_reward)

        if step % save_every == 0:
            agent.save_model(f"models/ppo_step_{step}.pth")
            print(f"✅ Step {step}: reward = {ep_reward:.2f}")

    # 🎥 可选：保存为 GIF
    if config.get("record_gif", False):
        save_gif_from_frames(gif_frames, "output/final_run.gif")

    return reward_history
