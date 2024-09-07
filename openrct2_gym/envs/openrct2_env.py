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
        self.max_track_length = 250
        self.max_steps = 256
        self.station_length = self.ui_controller.station_length
        self.steps = 0
        self.loop_completed = False
        self.last_piece_type = 0
        self.chain_lift_count = 0
        self.max_chain_lifts = 15
        self.last_action = None

        # Define observation space
        self.observation_space = gym.spaces.Dict({
            'track_pieces': gym.spaces.Box(low=0, high=19, shape=(self.max_track_length,), dtype=np.int32),
            'current_height': gym.spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
            'current_direction': gym.spaces.Discrete(4),
            'distance_to_start': gym.spaces.Box(low=0, high=np.sqrt(2000**2 + 2000**2), shape=(1,), dtype=np.float32),
            'track_length': gym.spaces.Discrete(self.max_track_length + 1),
            'last_piece_type': gym.spaces.Discrete(19),
        })

    def step(self, action):
        success, new_position, new_direction = self.track_builder.take_action(action, self.current_position, self.current_direction)
        if success:
            if action == 18:  # Remove piece
                if self.track_pieces:
                    self.track_pieces.pop()
                    self.track_length -= 1
            else:
                self.track_length += 1
                self.track_pieces.append(action)

            self.last_piece_type = action
            self.current_position = new_position
            self.current_direction = new_direction
        
        self.last_action = action
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
        print("Current step: %s, Track length: %s, Current position: %s, Last piece: %s, Distance to goal: %f, Chainlifts: %s, Direction: %s, Goal: %s" % (self.steps, self.track_length, self.current_position, self.last_piece_type, self._calculate_distance_to_start(), self.chain_lift_count, self.current_direction, self.goal_position))
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
        self.goal_position = [500, 500 - self.station_length, 0]

        self.current_direction = 0
        self.track_pieces = []
        self.track_length = 0
        self.steps = 0
        self.loop_completed = False
        self.last_piece_type = 0
        self.chain_lift_count = 0
        self.last_action = None
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
        reward = 0
        if success:
            # Base reward for successful action
            reward += 1

            # Reward for placing chain lifts in the beginning
            if self.track_length < 17 and self.last_piece_type == 15:
                if self.chain_lift_count < self.max_chain_lifts:
                    reward += 5
                    self.chain_lift_count += 1
            
            # Penalty for removing pieces
            if self.last_action == 18:
                reward -= 2

            # Reward for continuous building
            #if self.last_action != 18 and self.last_action == self.last_piece_type:
            #    reward += 0.2

            # Big reward for completing the loop
            if self.loop_completed:
                reward += 100
            
            # Penalty for excessive height to discourage sky-high coasters
            if self.current_position[2] > 22:  # Adjust the height threshold as needed
                reward -= 0.2

            # Reward for building a longer track
            #if self.track_length > 50:
            #    reward += 0.5

            # Punish going far away from start
            if self._calculate_distance_to_start() > 40:
                distance_to_start = self._calculate_distance_to_start()
                reward -= max(0, distance_to_start - 40) * 0.1

            # Encourage returning to start for longer tracks
            if self.track_length > 40:
                distance_to_start = self._calculate_distance_to_start()
                reward += max(0, 40 - distance_to_start) * 0.1
        else:
            # If segment could not be placed, punish the agent
            reward -= 0.5
        print("Reward was: %s" % reward)
        return reward

    def _calculate_distance_to_start(self):
        point_a = np.array(self.current_position)
        point_b = np.array(self.goal_position)
        distance = float(np.linalg.norm(point_a - point_b))
        return np.array([distance], dtype=np.float32)

    def _is_trunkated(self):
        return (self.steps >= self.max_steps or 
                self.track_length >= self.max_track_length)

    def _get_observation(self):
        observation = {
            'track_pieces': np.array(self.track_pieces + [0] * (self.max_track_length - len(self.track_pieces)), dtype=np.int32),
            'current_height': np.array([self.current_position[2]], dtype=np.int32),
            'current_direction': self.current_direction,
            'distance_to_start': self._calculate_distance_to_start(),
            'track_length': self.track_length,
            'last_piece_type': self.last_piece_type,
        }
        
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
    #TODO Fix run_ride_evaluation() and stop returning random values
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

