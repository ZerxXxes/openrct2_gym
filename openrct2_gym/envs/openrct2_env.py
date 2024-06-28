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

        # Initialize state variables
        self.current_position = None
        self.goal_position = None
        self.current_direction = 0
        self.track_pieces = []
        self.track_length = 0
        self.max_track_length = 30
        self.max_steps = 50
        self.station_length = self.ui_controller.station_length
        self.steps = 0
        self.loop_completed = False
        self.chain_lift_used = False
        self.last_piece_type = 0

        # Define observation space
        self.observation_space = gym.spaces.Dict({
            'track_pieces': gym.spaces.Box(low=0, high=16, shape=(self.max_track_length,), dtype=np.int32),
            'current_height': gym.spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
            'current_direction': gym.spaces.Discrete(4),
            'distance_to_start': gym.spaces.Box(low=0, high=np.sqrt(2000**2 + 2000**2), shape=(1,), dtype=np.float32),
            'track_length': gym.spaces.Discrete(self.max_track_length + 1),
            'last_piece_type': gym.spaces.Discrete(17),
            'chain_lift_used': gym.spaces.Discrete(2),
        })

    def step(self, action):
        success, new_position, new_direction = self.track_builder.take_action(action, self.current_position, self.current_direction)
        if success:
            if action == 16:  # Remove piece
                print(f"Track piece removed, current position: {self.current_position} current direction: {self.current_direction}")
                if self.track_pieces:
                    self.track_pieces.pop()
                    self.track_length -= 1
            else:
                print(f"Track piece placed, current position: {self.current_position} current direction: {self.current_direction}")
                self.track_length += 1
                self.track_pieces.append(action)

            self.last_piece_type = action
            self.current_position = new_position
            self.current_direction = new_direction

        observation = self._get_observation()
        reward = self._calculate_reward(success)

        # Check for loop completion
        self.loop_completed = self.ui_controller.is_loop_completed()
        if self.loop_completed:
            print(f"Loop has been completed, great success!")
        terminated = self.loop_completed
        
        # Check if episode was truncated
        truncated = self._is_trunkated()
        self.steps += 1
        info = {}

        if terminated:
            ride_rating = self.evaluate_ride()
            info['ride_rating'] = ride_rating

        return observation, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.ui_controller.demolish_rollercoaster()

        # Set initial position (north end of the station)
        self.current_position = [500, 500, 0]

        # Set goal position (south end of the station)
        self.goal_position = [500, 500 + self.station_length, 0]

        self.current_direction = 0
        self.track_pieces = []
        self.track_length = 0
        self.steps = 0
        self.loop_completed = False
        self.chain_lift_used = False
        self.last_piece_type = 0
        self.track_builder.history.clear()  # Clear the history when resetting the environment

        # Build inital station
        self.ui_controller.start_new_rollercoaster()

        # Update our state to reflect the built station
        self.track_length = self.station_length
        self.track_pieces = [0] * self.station_length  # Assuming 0 is the action for a straight piece

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
        return {
            'track_pieces': np.array(self.track_pieces + [0] * (self.max_track_length - len(self.track_pieces)), dtype=np.int32),
            'current_height': np.array([self.current_position[2]], dtype=np.int32),
            'current_direction': self.current_direction,
            'distance_to_start': np.array([np.sqrt((self.current_position[0] - self.goal_position[0])**2 + 
                                                   (self.current_position[1] - self.goal_position[1])**2)], dtype=np.float32),
            'track_length': self.track_length,
            'last_piece_type': self.last_piece_type,
            'chain_lift_used': int(self.chain_lift_used),
        }

    def update_current_state(self, action):
        # Update current position, direction, and other state variables based on the action
        # This is a placeholder and should be implemented based on how each action affects the state
        pass

    def evaluate_ride(self):
        # Placeholder for ride evaluation function
        # This should start the ride, run a lap, and return the ride rating
        # For now, we'll return a random rating
        return {
            'excitement': np.random.randint(0, 100),
            'intensity': np.random.randint(0, 100),
            'nausea': np.random.randint(0, 100)
        }
    def close(self):
        pass

    def render(self):
        if self.render_mode == "human":
            pass

