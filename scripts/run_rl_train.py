from train.curriculum_trainer import run_curriculum_training

if __name__ == "__main__":
    config = {
        "curriculum_schedule_path": "configs/curriculum_schedule.yaml",
        "room_config_path": "configs/room_config.json",
        "total_steps": 5000,
        "save_every": 500,
        "record_gif": True,
    }

    run_curriculum_training(config)