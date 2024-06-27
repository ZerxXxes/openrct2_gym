import pyautogui
import time
from PIL import ImageGrab
import numpy as np

class UIController:
    def __init__(self):
        self.delay = 0.2
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
        

    def click(self, coords):
        pyautogui.click(coords)
        time.sleep(self.delay)

    def start_new_rollercoaster(self):
        self.click(self.build_coaster_coords)
        self.click(self.choose_coaster_coords)
        self.click(self.custom_coster_coords)
        self.click(self.place_coords)
        for _ in range(7):
            self.click(self.build_coords)

    def demolish_rollercoaster(self):
        self.click(self.exit_builder_coords)
        self.click(self.demolish_ride_coords)
        self.click(self.confirm_demolish_coords)

    def remove_piece(self):
        # Remove last piece
        self.click(self.remove_piece)

    def add_track_piece(self, piece_type):
        # Check direction 
        if "straight" in piece_type:
            self.click(self.direction_straight)
        elif "left" in piece_type:
            self.click(self.direction_left)
        elif "right" in piece_type:
            self.click(self.direction_right)
       
        # Check slope
        if "level" in piece_type:
            self.click(self.slope_level)
        elif "up" in piece_type:
            self.click(self.slope_up)
        elif "down" in piece_type:
            self.click(self.slope_down)
        
        # Check roll
        if "noroll" in piece_type:
            self.click(self.roll_none)
        if "leftroll" in piece_type:
            self.click(self.roll_left)
        if "rightroll" in piece_type:
            self.click(self.roll_right)
        
        # Check chain lift
        if "chain" in piece_type:
            self.click(self.chain_lift)

        # Click build segment
        self.click(self.build_coords)

        return not self._check_for_error()

    def _check_for_error(self):
        try:
            error_region = np.array(ImageGrab.grab(bbox=self.error_area))
            error_red = np.array([199, 0, 0])
            red_match = np.sum(np.all(error_region == error_red, axis=2)) / error_region.size

            if red_match > 0.1:
                print(f"Error detected: {red_match:.2%} red")
                return True
            else:
                return False
        except Exception as e:
            print(f"Error in _check_for_error: {e}")
            return False
