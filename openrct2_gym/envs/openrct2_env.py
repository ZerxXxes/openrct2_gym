import gymnasium as gym
import numpy as np
from .track_builder import TrackBuilder
from .ui_controller import UIController

class OpenRCT2Env(gym.Env):
    def __init__(self, render_mode=None):
        super(OpenRCT2Env, self).__init__()
        self.render_mode = render_mode
        self.ui_controller = UIController()
        self.track_builder = TrackBuilder(self.ui_controller)
        
        # Define action and observation space
        self.action_space = gym.spaces.Discrete(17)
        self.observation_space = gym.spaces.Box(
            low=np.array([0, 0, 0, 0]),
            high=np.array([1000, 1000, 100, 3]),
            dtype=np.float32
        )

        # Initialize state variables
        self.current_position = [500, 500, 0]
        self.current_direction = 0
        self.track_length = 0
        self.max_track_length = 30
        self.max_steps = 30
        self.steps = 0
        self.loop_completed = False

    def step(self, action):
        success = self.track_builder.take_action(action)
        if success:
            print(f"Track piece placed, increase reward")
        observation = self._get_observation()
        reward = self._calculate_reward(success)

        # Check for loop completion
        self.loop_completed = self.ui_controller.is_loop_completed()
        terminated = self.loop_completed
        
        # Check if episode was truncated
        truncated = self._is_trunkated()
        self.steps += 1
        info = {}
        return observation, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.ui_controller.demolish_rollercoaster()
        self.current_position = [500, 500, 0]
        self.current_direction = 0
        self.track_length = 0
        self.steps = 0
        self.loop_completed = False
        self.ui_controller.start_new_rollercoaster()
        observation = self._get_observation()
        info = {}
        return observation, info

    def _calculate_reward(self, success):
        if self.loop_completed:
            return 100  # Big reward for completing the loop
        elif success:
            return 1
        else:
            return -0.5

    def _is_trunkated(self):
        return (self.steps >= self.max_steps or 
                self.track_length >= self.max_track_length)

    def _get_observation(self):
        return np.array([
            self.current_position[0],
            self.current_position[1],
            self.current_position[2],
            self.current_direction
        ], dtype=np.float32)

    def close(self):
        pass

    def render(self):
        if self.render_mode == "human":
            pass

