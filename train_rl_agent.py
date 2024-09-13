import gymnasium as gym
import openrct2_gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import BaseCallback
import os
import argparse

class TensorboardCallback(BaseCallback):
    """
    Custom callback for plotting additional values in tensorboard.
    """
    def __init__(self, verbose=0):
        super(TensorboardCallback, self).__init__(verbose)
        self.loop_completed_count = 0
        self.episode_count = 0

    def _on_step(self) -> bool:
        # Log scalar value (here a random variable)
        track_length = self.model.get_env().get_attr('track_length')[0]
        self.logger.record('track_length', track_length)
        # Check if episode is done
        if self.locals['dones'][0]:
            self.episode_count += 1
            
            # Check if the episode terminated (loop completed) or was truncated
            terminated = self.locals['infos'][0].get('terminal_observation') is not None
            
            if terminated:
                self.loop_completed_count += 1
                self.logger.record('loop_completed', 1.0)
                self.logger.record('completed_track_length', track_length)
            else:
                self.logger.record('loop_completed', 0.0)
            
            # Log the percentage of episodes where loop was completed
            loop_completion_rate = self.loop_completed_count / self.episode_count
            self.logger.record('loop_completion_rate', loop_completion_rate)

        return True

class ProgressCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(ProgressCallback, self).__init__(verbose)
        self.episode_count = 0

    def _on_step(self) -> bool:
        if self.locals['dones'][0]:
            self.episode_count += 1
            total_timesteps = self.num_timesteps
            
            # Check if the episode terminated (loop completed) or was truncated
            terminated = self.locals['infos'][0].get('terminal_observation') is not None
            
            print(f"Episode: {self.episode_count}")
            print(f"Total timesteps: {total_timesteps}")
            print(f"Episode reward: {self.locals['rewards'][0]:.2f}")
            print(f"Loop completed: {terminated}")
            print("------")
        return True

def create_env():
    env = gym.make('OpenRCT2-v0')
    env = Monitor(env)  # Wrap the environment
    return DummyVecEnv([lambda: env])

def train_agent(total_timesteps, checkpoint_freq, eval_freq, model_path=None):
    env = create_env()

    if model_path and os.path.exists(model_path):
        print(f"Loading model from {model_path}")
        model = PPO.load(model_path, env=env)
    else:
        print("Creating new model")
        policy_kwargs = dict(
            net_arch=dict(pi=[256, 256], vf=[256, 256]),
        )
        model = PPO("MultiInputPolicy", env, policy_kwargs=policy_kwargs, verbose=1, tensorboard_log="./ppo_openrct2_tensorboard/")

    # Callbacks
    checkpoint_callback = CheckpointCallback(save_freq=checkpoint_freq, save_path='./logs/', name_prefix='ppo_openrct2_model')
    eval_callback = EvalCallback(env, best_model_save_path='./logs/best_model', log_path='./logs/', eval_freq=eval_freq)
    tensorboard_callback = TensorboardCallback()
    progress_callback = ProgressCallback()

    # Create log directory
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=checkpoint_freq,
        save_path=log_dir,
        name_prefix="ppo_openrct2_model"
    )
    
    eval_callback = EvalCallback(
        env,
        best_model_save_path=log_dir,
        log_path=log_dir,
        eval_freq=eval_freq,
        deterministic=True,
        render=False
    )

    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[checkpoint_callback, eval_callback, tensorboard_callback, progress_callback],
            reset_num_timesteps=False  # Important for continuing training
        )
    except Exception as e:
        print(f"An error occurred during training: {e}")
    
    # Save the final model
    final_model_path = os.path.join(log_dir, "final_model")
    model.save(final_model_path)
    print(f"Final model saved to {final_model_path}")

    return model, env

def evaluate_agent(model, env):
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10)
    print(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")

def main():
    parser = argparse.ArgumentParser(description="Train RL agent for OpenRCT2")
    parser.add_argument("--timesteps", type=int, default=200000, help="Total timesteps to train")
    parser.add_argument("--checkpoint-freq", type=int, default=10000, help="Frequency of checkpoints")
    parser.add_argument("--eval-freq", type=int, default=10000, help="Frequency of evaluations")
    parser.add_argument("--model-path", type=str, help="Path to a saved model to continue training")
    args = parser.parse_args()

    model, env = train_agent(args.timesteps, args.checkpoint_freq, args.eval_freq, args.model_path)
    evaluate_agent(model, env)

    env.close()

if __name__ == "__main__":
    main()
