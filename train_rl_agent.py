import gymnasium as gym
import openrct2_gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy

# Create the environment
env = gym.make('OpenRCT2-v0')

# Wrap the environment in a DummyVecEnv (Stable Baselines3 requires a vectorized environment)
env = DummyVecEnv([lambda: env])

# Initialize the agent
model = PPO("MultiInputPolicy", env, verbose=1)

# Train the agent
total_timesteps = 100000
try:
    model.learn(total_timesteps=total_timesteps)
except Exception as e:
    print(f"An error occurred during training: {e}")
    # You might want to add more detailed error handling here

# Save the trained model
model.save("ppo_openrct2")

# Evaluate the trained agent
mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10)
print(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")

# Test the trained agent
obs = env.reset()
for _ in range(1000):
    action, _states = model.predict(obs, deterministic=True)
    obs, rewards, dones, info = env.step(action)
    env.render()
    if dones:
        obs = env.reset()

env.close()
