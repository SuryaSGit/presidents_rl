from typing import List
import random
from typing import Optional
import numpy as np
import gymnasium as gym
from gymnasium.utils.env_checker import check_env
import torch
import environment
from torch import nn
from collections import deque
import itertools
import torch.nn.functional as F


GAMMA = 0.99
BATCH_SIZE = 32
BUFFER_SIZE = 50000
MIN_REPLAY_SIZE = 1000
EPSILON_START = 1.0
EPSILON_END = 0.02
EPSILON_DECAY = 10000
TARGET_UPDATE_FREQ = 1000

class Network(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, output_dim)
        )

    def forward(self, x):
        return self.net(x)
    def act(self,obs):
        obs_t = torch.as_tensor(obs, dtype=torch.float32)
        q_values = self(obs_t.unsqueeze(0))
        return q_values

env = gym.make("gymnasium_env/presidents-rl")
replay_buffer = deque(maxlen=BUFFER_SIZE)
rew_buffer = deque([0.0],maxlen=100)

episode_reward = 0.0

online_net = Network(108,92)
target_net = Network(108,92)
target_net.load_state_dict(online_net.state_dict())
optimizer = torch.optim.Adam(online_net.parameters(), lr = 5e-4)

obs =  env.reset()[0]
for _ in range(MIN_REPLAY_SIZE):
    action = env.unwrapped.action_space_sample()
    new_obs, reward, terminated, truncated, info = env.step(action)
    replay_buffer.append((obs, action, reward, terminated, new_obs))
    obs = new_obs
    if terminated:
        obs = env.reset()[0]
#main training

obs = env.reset()[0]
for step in itertools.count():
    epsilon = np.interp(step, [0, EPSILON_DECAY], [EPSILON_START, EPSILON_END])
    rnd_sample = random.random()
    if(rnd_sample < epsilon):
        action = env.unwrapped.action_space_sample()
    else:
        q_vals = online_net.act(obs)
        action = env.unwrapped.getaction(q_vals)
    new_obs, reward, terminated, truncated, info = env.step(action)
    replay_buffer.append((obs, action, reward, terminated, new_obs))
    obs = new_obs
    episode_reward += reward    
    if terminated:
        obs = env.reset()[0]    
        rew_buffer.append(episode_reward)
        episode_reward = 0.0


    transitions = random.sample(replay_buffer, BATCH_SIZE)

    obses = np.asarray([t[0] for t in transitions])
    actions = np.asarray([t[1] for t in transitions])
    rews = np.asarray([t[2] for t in transitions])
    dones = np.asarray([t[3] for t in transitions])
    newobses = np.asarray([t[4] for t in transitions])

    obses_t = torch.as_tensor(obses,dtype = torch.float32)
    actions_t = torch.as_tensor(actions,dtype = torch.int64).unsqueeze(-1)
    rews_t = torch.as_tensor(rews,dtype = torch.float32).unsqueeze(-1)
    dones_t = torch.as_tensor(dones,dtype = torch.float32).unsqueeze(-1)
    newobses_t   = torch.as_tensor(newobses,dtype = torch.float32)

    target_q_values = target_net(newobses_t)
    max_target_q_values = target_q_values.max(dim=1, keepdim = True)[0]
    targets = rews_t + GAMMA * (1-dones_t) * max_target_q_values

    q_values = online_net(obses_t)

    action_q_values = torch.gather(input = q_values, dim = 1, index = actions_t)

    loss = F.smooth_l1_loss(action_q_values,targets)


    optimizer.zero_grad()
    loss.backward()
    optimizer.step()


    if step%TARGET_UPDATE_FREQ == 0:
        target_net.load_state_dict(online_net.state_dict())
    if(step%1000 == 0):
        print()
        print('Step',step)
        print('Avg_Rew', np.mean(rew_buffer))
