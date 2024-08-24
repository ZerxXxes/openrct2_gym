import gymnasium as gym
import openrct2_gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

def main():
    # Create and wrap the environment
    env = gym.make('OpenRCT2-v0')
    env = DummyVecEnv([lambda: env])

    # Load the trained model
    model = PPO.load("ppo_openrct2")

    # Run the model
    obs = env.reset()
    done = False
    total_reward = 0

    while not done:
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        total_reward += reward[0]  # reward is returned as a tuple for vectorized environments

        # You might want to add a small delay here to see the coaster being built
        # import time
        # time.sleep(0.1)

    print(f"Coaster building completed. Total reward: {total_reward}")

    # If your environment has a method to get the final coaster stats, you could call it here
    # final_stats = env.get_coaster_stats()
    # print(f"Final coaster stats: {final_stats}")

    env.close()

if __name__ == "__main__":
    main()
