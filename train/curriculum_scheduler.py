import yaml

class CurriculumScheduler:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.schedule = yaml.safe_load(f)["phases"]
        self.current_phase_index = 0

    def update(self, global_step):
        # Advance to next phase if step threshold is passed
        if (self.current_phase_index + 1 < len(self.schedule) and
            global_step >= self.schedule[self.current_phase_index + 1]["step_threshold"]):
            self.current_phase_index += 1

    def get_current_config(self):
        return self.schedule[self.current_phase_index]
