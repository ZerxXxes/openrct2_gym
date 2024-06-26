import gymnasium as gym
import numpy as np
import pyautogui
from PIL import ImageGrab, Image
import time

class OpenRCT2Env(gym.Env):
    def __init__(self, render_mode=None):
        super(OpenRCT2Env, self).__init__()

        self.render_mode = render_mode
        
        # Define action and observation space
        # They must be gym.spaces objects
        # Example: Discrete actions for different track pieces
        self.action_space = gym.spaces.Discrete(3)
        
        self.observation_space = gym.spaces.Box(
            low=np.array([0, 0, 0, 0]),  # Minimum values for x, y, z, direction
            high=np.array([1000, 1000, 100, 3]),  # Maximum values
            dtype=np.float32
        )

        # Initialize state variables
        self.current_position = [500, 500, 0]  # x, y, z
        self.current_direction = 0  # 0: North, 1: East, 2: South, 3: West
        self.track_length = 0

        # Additional parameters
        self.max_track_length = 10  # Maximum allowed track length
        self.max_steps = 20  # Maximum steps per episode

        # Initialize step counter
        self.steps = 0

        # Define the time to wait between each button press
        self.delay = 0.2
        # Define coordinates for various UI elements (you'll need to adjust these)
        self.build_coaster_coords = (983, 85)
        self.choose_coaster_coords = (143, 206)
        self.custom_coster_coords = (179, 152)
        self.place_coords = (269, 598)
        self.build_coords = (170, 350)
        self.exit_builder_coords = (269, 106)
        self.demolish_ride_coords = (1026, 257)
        self.confirm_demolish_coords = (502, 399)
        
        # Track pieces
        ## Direction
        self.direction_straight = (172, 142)
        self.direction_left = (126, 142)
        self.direction_left_large = (149, 142)
        self.direction_left_small = (103, 142)
        self.direction_right = (212, 142)
        self.direction_right_large = (192, 142)
        self.direction_right_small = (236, 142)
        
        ## Slope
        self.slope_level = (172, 200)
        self.slope_steep_down = (125, 200)
        self.slope_down = (146, 200)
        self.slope_up = (197, 200)
        self.slope_steep_up = (220, 200)

        ## Roll
        self.roll_left = (146, 242)
        self.roll_none = (171, 242)
        self.roll_right = (197, 242)

        # Chain lift
        self.chain_lift = (256, 195)

        # Error detection
        self.error_area = (105, 380, 231, 402)  # (left, top, right, bottom)

    def step(self, action):
        # Execute the action
        success = self._take_action(action)
        
        # Get the new observation
        observation = self._get_observation()
        
        # Calculate the reward
        reward = self._calculate_reward(success)
        
        # Check if the episode is done
        terminated = self._is_done()
        truncated = False  # Set this to True if you're ending the episode early due to a time limit or similar constraint

        # Increment step counter
        self.steps += 1
        print(f"Step count: {self.steps}, Current position: {self.current_position}")

        # Additional info
        info = {}
        
        return observation, reward, terminated, truncated, info

    def _take_action(self, action):
        # Map action to track piece
        if action == 0:
            print("Adding straight track")
            return self.add_straight_piece()
        elif action == 1:
            print("Adding left track")
            return self.add_left_piece()
        elif action == 2:
            print("Adding right track")
            return self.add_right_piece()
        else:
            print(f"Invalid action: {action}")
            return False

    def _calculate_reward(self, success):
        if success:
            return 1  # Reward for successfully placing a track piece
        else:
            return -1  # Penalty for failed placement

    def _is_done(self):
        return (self.steps >= self.max_steps or 
                self.track_length >= self.max_track_length)
    def reset(self, seed=None, options=None):
        # Reset the state of the environment to an initial state
        super().reset(seed=seed)
        self.demolish_rollercoaster()
        self.current_position = [500, 500, 0]  # x, y, z
        self.current_direction = 0  # 0: North, 1: East, 2: South, 3: West
        self.track_length = 0
        self.steps = 0
        
        # Start a new rollercoaster
        self.start_new_rollercoaster()
        
        observation = self._get_observation()
        info = {}  # You can add any additional info here

        return observation, info

    def close(self):
        # Perform any necessary cleanup
        pass
       
    def render(self):
        if self.render_mode == "human":
            # Implement rendering logic here if needed
            pass

    def _get_observation(self):
        return np.array([
            self.current_position[0],
            self.current_position[1],
            self.current_position[2],
            self.current_direction
        ], dtype=np.float32)

    def start_new_rollercoaster(self):
        """Start a new rollercoaster by clicking the appropriate menu items."""
        # Click the rollercoaster button
        pyautogui.click(self.build_coaster_coords)
        time.sleep(self.delay)  # Wait for menu to appear
        
        pyautogui.click(self.choose_coaster_coords)
        time.sleep(self.delay)
        
        pyautogui.click(self.custom_coster_coords)
        time.sleep(self.delay)

        pyautogui.click(self.place_coords)
        time.sleep(self.delay)

        # build 7 station segments
        pyautogui.click(self.build_coords)
        time.sleep(self.delay)
        pyautogui.click(self.build_coords)
        time.sleep(self.delay)
        pyautogui.click(self.build_coords)
        time.sleep(self.delay)
        pyautogui.click(self.build_coords)
        time.sleep(self.delay)
        pyautogui.click(self.build_coords)
        time.sleep(self.delay)
        pyautogui.click(self.build_coords)
        time.sleep(self.delay)
        pyautogui.click(self.build_coords)
        time.sleep(self.delay)
        
        return True

    def demolish_rollercoaster(self):
        """Demolish the rollercoaster by clicking the appropriate menu items."""
        pyautogui.click(self.exit_builder_coords)
        time.sleep(self.delay)
        pyautogui.click(self.demolish_ride_coords)
        time.sleep(self.delay)
        pyautogui.click(self.confirm_demolish_coords)
        time.sleep(self.delay)

        return True

    def add_straight_piece(self):
        """Add a straight track piece to the rollercoaster."""
        # Click the straight piece button
        pyautogui.click(self.direction_straight)
        time.sleep(self.delay)
        
        pyautogui.click(self.slope_level)
        time.sleep(self.delay)

        pyautogui.click(self.roll_none)
        time.sleep(self.delay)

        pyautogui.click(self.build_coords)
        time.sleep(self.delay)
        
        # Check for errors
        if self._check_for_error():
            print("Error: Could not place straight track piece")
            return False

        # Update position based on current direction
        if self.current_direction == 0:  # North
            self.current_position[1] -= 1
        elif self.current_direction == 1:  # East
            self.current_position[0] += 1
        elif self.current_direction == 2:  # South
            self.current_position[1] += 1
        elif self.current_direction == 3:  # West
            self.current_position[0] -= 1

        self.track_length += 1
        return True

    def add_left_piece(self):
        """Add a left track piece to the rollercoaster."""
        # Click the straight piece button
        pyautogui.click(self.direction_left)
        time.sleep(self.delay)
        
        pyautogui.click(self.slope_level)
        time.sleep(self.delay)

        pyautogui.click(self.roll_none)
        time.sleep(self.delay)

        pyautogui.click(self.build_coords)
        time.sleep(self.delay)
        
        # Check for errors
        if self._check_for_error():
            print("Error: Could not place left track piece")
            return False

                # Update position and direction
        if self.current_direction == 0:  # North
            self.current_position[0] -= 2
            self.current_position[1] -= 2
            self.current_direction = 3  # Now facing West
        elif self.current_direction == 1:  # East
            self.current_position[0] += 2
            self.current_position[1] -= 2
            self.current_direction = 0  # Now facing North
        elif self.current_direction == 2:  # South
            self.current_position[0] += 2
            self.current_position[1] += 2
            self.current_direction = 1  # Now facing East
        elif self.current_direction == 3:  # West
            self.current_position[0] -= 2
            self.current_position[1] += 2
            self.current_direction = 2  # Now facing South 
        self.track_length += 1

        return True

    def add_right_piece(self):
        """Add a right track piece to the rollercoaster."""
        # Click the straight piece button
        pyautogui.click(self.direction_right)
        time.sleep(self.delay)
        
        pyautogui.click(self.slope_level)
        time.sleep(self.delay)

        pyautogui.click(self.roll_none)
        time.sleep(self.delay)

        pyautogui.click(self.build_coords)
        time.sleep(self.delay)
        
        # Check for errors
        if self._check_for_error():
            print("Error: Could not place right track piece")
            return False

        # Update position and direction
        if self.current_direction == 0:  # North
            self.current_position[0] += 2
            self.current_position[1] -= 2
            self.current_direction = 1  # Now facing East
        elif self.current_direction == 1:  # East
            self.current_position[0] += 2
            self.current_position[1] += 2
            self.current_direction = 2  # Now facing South
        elif self.current_direction == 2:  # South
            self.current_position[0] -= 2
            self.current_position[1] += 2
            self.current_direction = 3  # Now facing West
        elif self.current_direction == 3:  # West
            self.current_position[0] -= 2
            self.current_position[1] -= 2
            self.current_direction = 0  # Now facing North
        
        self.track_length += 1

        return True

    def _check_for_error(self):
        """Check for red error message on screen."""
        try:
            # Capture the error area
            error_region = np.array(ImageGrab.grab(bbox=self.error_area))
            
            # Define the colors we're looking for
            error_red = np.array([199, 0, 0])
            
            # Calculate the percentage of pixels that match the error red color
            red_match = np.sum(np.all(error_region == error_red, axis=2)) / error_region.size
            print("Red match: %s" % red_match)
            
            # Define thresholds for error detection
            red_threshold = 0.1  # At least 10% of pixels should be the error red
            
            # Check if both color conditions are met
            if red_match > red_threshold:
                print(f"Error detected: {red_match:.2%} red")
                return True
            else:
                return False
        
        except Exception as e:
            print(f"Error in _check_for_error: {e}")
            return False
