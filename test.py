import sys
import openrct2_gym
import argparse
import gymnasium as gym
parser = argparse.ArgumentParser(description="Execute a test-run of the environment by just taking random actions")
parser.add_argument("-x","--example", help="Creates a predifined ride", action="store_true")
args = parser.parse_args()

def test_environment():
    env = gym.make('OpenRCT2-v0')
    test_ride = [15,15,15,0,3,3,5,5,5,0,0,0,0,0,0,0,3,3] # Create a small hill with chain and then go back to start
    
    for episode in range(3):  # Run 3 episodes
        print(f"\nStarting episode {episode + 1}")
        observation, info = env.reset()
        terminated = truncated = False
        total_reward = 0
        step_count = 0
        
        while not (terminated or truncated):
            if args.example:
                action = test_ride[step_count]
            else:
                action = env.action_space.sample()  # Random action
            print(f"Step {step_count + 1}, Action: {action}")
            observation, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            step_count += 1
            
        print(f"Episode {episode + 1} finished with reward {total_reward} after {step_count} steps")
        print(f"Observations for agent: {observation}")
    
    env.close()
if __name__ == "__main__":
    test_environment()

