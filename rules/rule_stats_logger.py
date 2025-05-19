from collections import defaultdict

class RuleStatsLogger:
    def __init__(self):
        self.rule_calls = defaultdict(int)
        self.rule_success = defaultdict(int)
        self.rule_rewards = defaultdict(float)

    def record_call(self, rule_name: str):
        self.rule_calls[rule_name] += 1

    def record_success(self, rule_name: str):
        self.rule_success[rule_name] += 1

    def record_reward(self, rule_name: str, reward: float):
        self.rule_rewards[rule_name] += reward

    def summarize(self):
        print("\n📊 Rule Stats Summary:")
        for rule in self.rule_calls:
            print(f"Rule: {rule}")
            print(f"  Calls: {self.rule_calls[rule]}")
            print(f"  Success: {self.rule_success[rule]}")
            print(f"  Total Reward: {self.rule_rewards[rule]:.3f}")
            print("-" * 30)
