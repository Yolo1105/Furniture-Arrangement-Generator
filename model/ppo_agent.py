import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal

class FurniturePPOAgent(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim=128):
        super(FurniturePPOAgent, self).__init__()
        self.actor = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim)
        )
        self.critic = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        self.log_std = nn.Parameter(torch.zeros(action_dim))

    def forward(self, state):
        action_mean = self.actor(state)
        value = self.critic(state)
        return action_mean, value

    def act(self, state):
        with torch.no_grad():
            action_mean, _ = self.forward(state)
            std = self.log_std.exp()
            dist = Normal(action_mean, std)
            action = dist.sample()
            log_prob = dist.log_prob(action).sum()

            clipped = torch.clamp(action, 0.0, 1.0)
            clipped[2] = torch.floor(clipped[2] * 4) / 4
            return clipped.detach().numpy(), log_prob

    def evaluate(self, states, actions):
        action_mean, value = self.forward(states)
        std = self.log_std.exp()
        dist = Normal(action_mean, std)
        log_probs = dist.log_prob(actions).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)
        return log_probs, value, entropy
