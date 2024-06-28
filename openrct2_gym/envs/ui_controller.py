import pyautogui
import time
from PIL import ImageGrab
import numpy as np

class UIController:
    def __init__(self):
        self.station_length = 6
        self.delay = 0.2
        self.faded_color = np.array([123, 103, 75])
        self.build_button_bg = np.array([143, 127, 107])
        self.color_threshold = 2
        self.build_coaster_coords = (983, 85)
        self.choose_coaster_coords = (143, 206)
        self.custom_coster_coords = (179, 152)
        self.place_coords = (269, 598)
        self.build_coords = (170, 350)
        self.exit_builder_coords = (269, 106)
        self.demolish_ride_coords = (1026, 257)
        self.confirm_demolish_coords = (502, 399)
        self.remove_piece_coords = (170, 445)
        
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
        

    def click(self, coords):
        if self._is_button_clickable(coords):
            pyautogui.click(coords)
            time.sleep(self.delay)
            if coords == self.chain_lift:
                # If we clicked on chain lift, we need to click again to disable it
                pyautogui.click(coords)
            return True
        else:
            return False

    def _is_button_clickable(self, coords):
        # Define a small region around the button to check, larger area if we check the build button
        region_size = 25 if coords == self.build_coords else 5
        x, y = coords
        bbox = (x - region_size, y - region_size, x + region_size, y + region_size)
        
        # Capture the region around the button
        button_region = np.array(ImageGrab.grab(bbox=bbox))
        
        if coords == self.build_coords:
            # Check if the entire button region matches the background color
            region_size = 25
            color_match = np.all(np.abs(button_region - self.build_button_bg) < self.color_threshold, axis=2)
            return not np.all(color_match)  # If all pixels match, button is not clickable (loop completed)
        else:
            # Original check for other buttons
            color_match = np.all(np.abs(button_region - self.faded_color) < self.color_threshold, axis=2)
            return not np.any(color_match)

    def is_loop_completed(self):
        return not self._is_button_clickable(self.build_coords)

    def start_new_rollercoaster(self):
        print(f"Creating a new rollercoaster with {self.station_length} station segments")
        self.click(self.build_coaster_coords)
        self.click(self.choose_coaster_coords)
        self.click(self.custom_coster_coords)
        self.click(self.place_coords)
        for _ in range(self.station_length):
            self.click(self.build_coords)

    def demolish_rollercoaster(self):
        print(f"Destroying old rollercoaster")
        self.click(self.exit_builder_coords)
        self.click(self.demolish_ride_coords)
        self.click(self.confirm_demolish_coords)

    def remove_piece(self):
        # Remove last piece
        print(f"Remove last track piece")
        pyautogui.click(self.remove_piece_coords)
        return True

    def add_track_piece(self, piece_type):
        # Helper function to click if button is clickable
        print(f"Trying to place: {piece_type}")
        def safe_click(coords):
            if not self._is_button_clickable(coords):
                print(f"Piece {piece_type} not possible to place here, decrease reward")
                return False
            self.click(coords)
            return True

        # Check direction 
        if "straight" in piece_type:
            if not safe_click(self.direction_straight):
                return False
        elif "large_left" in piece_type:
            if not safe_click(self.direction_left_large):
                return False
        elif "small_left" in piece_type:
            if not safe_click(self.direction_left_small):
                return False
        elif "left" in piece_type:
            if not safe_click(self.direction_left):
                return False
        elif "large_right" in piece_type:
            if not safe_click(self.direction_right_large):
                return False
        elif "small_right" in piece_type:
            if not safe_click(self.direction_right_small):
                return False
        elif "right" in piece_type:
            if not safe_click(self.direction_right):
                return False
       
        # Check slope
        if "level" in piece_type:
            if not safe_click(self.slope_level):
                return False
        elif "up" in piece_type:
            if not safe_click(self.slope_up):
                return False
        elif "down" in piece_type:
            if not safe_click(self.slope_down):
                return False
        
        # Check roll
        if "noroll" in piece_type:
            if not safe_click(self.roll_none):
                return False
        if "leftroll" in piece_type:
            if not safe_click(self.roll_left):
                return False
        if "rightroll" in piece_type:
            if not safe_click(self.roll_right):
                return False
        
        # Check chain lift
        if "chain" in piece_type:
            if not safe_click(self.chain_lift):
                return False

        # Click build segment
        if not safe_click(self.build_coords):
            return False

        # Check for error after building
        return not self._check_for_error()

    def _check_for_error(self):
        try:
            error_region = np.array(ImageGrab.grab(bbox=self.error_area))
            error_red = np.array([199, 0, 0])
            red_match = np.sum(np.all(error_region == error_red, axis=2)) / error_region.size

            if red_match > 0.1:
                print(f"Error detected: {red_match:.2%} red, decrease reward")
                return True
            else:
                return False
        except Exception as e:
            print(f"Error in _check_for_error: {e}")
            return False
