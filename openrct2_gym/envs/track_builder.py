class TrackBuilder:
    def __init__(self, ui_controller):
        self.ui_controller = ui_controller

    def take_action(self, action):
        # Map action to track piece and call appropriate method
        if action == 0:
            return self.ui_controller.add_track_piece("straight_level_noroll")
        elif action == 1:
            return self.ui_controller.add_track_piece("left_level_noroll")
        elif action == 2:
            return self.ui_controller.add_track_piece("right_level_noroll")
        elif action == 3:
            return self.ui_controller.add_track_piece("straight_down_noroll")
        elif action == 4:
            return self.ui_controller.add_track_piece("straight_up_noroll")
        elif action == 10:
            return self.ui_controller.remove_piece()

