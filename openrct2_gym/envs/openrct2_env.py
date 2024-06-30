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
        self.action_space = gym.spaces.Discrete(19)

        # Initialize state variables
        self.current_position = None
        self.goal_position = None
        self.current_direction = 0
        self.track_pieces = []
        self.track_length = 0
        self.max_track_length = 100
        self.max_steps = 200
        self.station_length = self.ui_controller.station_length
        self.steps = 0
        self.loop_completed = False
        self.chain_lift_used = False
        self.last_piece_type = 0

        # Define observation space
        self.observation_space = gym.spaces.Dict({
            'track_pieces': gym.spaces.Box(low=0, high=19, shape=(self.max_track_length,), dtype=np.int32),
            'current_height': gym.spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
            'current_direction': gym.spaces.Discrete(4),
            'distance_to_start': gym.spaces.Box(low=0, high=np.sqrt(2000**2 + 2000**2), shape=(1,), dtype=np.float32),
            'track_length': gym.spaces.Discrete(self.max_track_length + 1),
            'last_piece_type': gym.spaces.Discrete(19),
            'chain_lift_used': gym.spaces.Discrete(2),
        })

    def step(self, action):
        success, new_position, new_direction = self.track_builder.take_action(action, self.current_position, self.current_direction)
        if success:
            if action == 18:  # Remove piece
                print(f"Track piece removed, current position: {self.current_position} current direction: {self.current_direction}")
                if self.track_pieces:
                    self.track_pieces.pop()
                    self.track_length -= 1
            else:
                print(f"Track piece placed, current position: {self.current_position} current direction: {self.current_direction}")
                self.track_length += 1
                self.track_pieces.append(action)
                if action == 15:
                    self.chain_lift_used = True # Chain lift was used, good job!

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
            self.ui_controller._place_entrance_exit()
            self.ui_controller.run_ride_evaluation()
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
        observation = {
            'track_pieces': np.array(self.track_pieces + [0] * (self.max_track_length - len(self.track_pieces)), dtype=np.int32),
            'current_height': np.array([self.current_position[2]], dtype=np.int32),
            'current_direction': self.current_direction,
            'distance_to_start': np.array([np.sqrt((self.current_position[0] - self.goal_position[0])**2 + 
                                                   (self.current_position[1] - self.goal_position[1])**2)], dtype=np.float32),
            'track_length': self.track_length,
            'last_piece_type': self.last_piece_type,
            'chain_lift_used': int(self.chain_lift_used),
        }
        
        # Add logging to check observation values
        for key, value in observation.items():
            if isinstance(value, np.ndarray):
                print(f"{key}: min={value.min()}, max={value.max()}, shape={value.shape}")
            else:
                print(f"{key}: value={value}")
        
        # Check if any values exceed their space
        track_pieces_space = self.observation_space['track_pieces']
        if isinstance(track_pieces_space, gym.spaces.Box):
            if np.any(observation['track_pieces'] < track_pieces_space.low) or np.any(observation['track_pieces'] > track_pieces_space.high):
                raise ValueError(f"track_pieces values are outside the defined space: {observation['track_pieces']}")
        
        if observation['current_direction'] >= self.observation_space['current_direction'].n:
            raise ValueError(f"current_direction value exceeds the defined space: {observation['current_direction']}")
        
        if observation['track_length'] >= self.observation_space['track_length'].n:
            raise ValueError(f"track_length value exceeds the defined space: {observation['track_length']}")
        
        if observation['last_piece_type'] >= self.observation_space['last_piece_type'].n:
            raise ValueError(f"last_piece_type value exceeds the defined space: {observation['last_piece_type']}")
        
        return observation

    def evaluate_ride(self):
        excitement, intensity, nausea = self.ui_controller.run_ride_evaluation()
        if excitement is None or intensity is None or nausea is None:
            print("Failed to get ride ratings, using random values")
            return {
                'excitement': np.random.randint(0, 100),
                'intensity': np.random.randint(0, 100),
                'nausea': np.random.randint(0, 100)
            }
        else:
            return {
                'excitement': excitement,
                'intensity': intensity,
                'nausea': nausea
            }

    def close(self):
        pass

    def render(self):
        if self.render_mode == "human":
            pass

