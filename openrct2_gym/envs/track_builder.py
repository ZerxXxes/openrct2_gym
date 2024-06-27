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
            return self.ui_controller.add_track_piece("large_left_level_noroll")
        elif action == 3:
            return self.ui_controller.add_track_piece("small_left_level_noroll")
        elif action == 4:
            return self.ui_controller.add_track_piece("right_level_noroll")
        elif action == 5:
            return self.ui_controller.add_track_piece("large_right_level_noroll")
        elif action == 6:
            return self.ui_controller.add_track_piece("small_right_level_noroll")
        elif action == 7:
            return self.ui_controller.add_track_piece("straight_down_noroll")
        elif action == 8:
            return self.ui_controller.add_track_piece("straight_up_noroll")
        elif action == 9:
            return self.ui_controller.add_track_piece("left_up_noroll")
        elif action == 10:
            return self.ui_controller.add_track_piece("right_up_noroll")
        elif action == 11:
            return self.ui_controller.add_track_piece("left_down_noroll")
        elif action == 12:
            return self.ui_controller.add_track_piece("right_down_noroll")
        elif action == 13:
            return self.ui_controller.add_track_piece("left_level_leftroll")
        elif action == 14:
            return self.ui_controller.add_track_piece("right_level_rightroll")
        elif action == 15:
            return self.ui_controller.add_track_piece("straight_up_noroll_chain")
        elif action == 16:
            return self.ui_controller.remove_piece()

