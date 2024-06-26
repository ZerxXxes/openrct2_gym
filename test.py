import sys
import openrct2_gym

import gymnasium as gym

def test_environment():
    env = gym.make('OpenRCT2-v0')
    
    for episode in range(3):  # Run 3 episodes
        print(f"\nStarting episode {episode + 1}")
        observation, info = env.reset()
        terminated = truncated = False
        total_reward = 0
        step_count = 0
        
        while not (terminated or truncated):
            action = env.action_space.sample()  # Random action
            print(f"Step {step_count + 1}, Action: {action}")
            observation, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            step_count += 1
            
        print(f"Episode {episode + 1} finished with reward {total_reward} after {step_count} steps")
    
    env.close()
if __name__ == "__main__":
    test_environment()

