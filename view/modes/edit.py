from view.modes import NormalMode


class EditMode(NormalMode):
    @property
    def note(self):
        return "Edit Mode"

    @property
    def normal_mode_return_value(self):
        return ("change_view_mode", {"mode": "normal"})

    def get_command(self):
        key_combo = self.get_keypress()
        if len(key_combo) > 1:
            return self.normal_mode_return_value
        else:
            if key_combo[0] == 27:  # ESC
                return self.normal_mode_return_value
            elif key_combo[0] == 127:  # BACKSPACE
                return ("delete_char", {"num": 1})
            elif key_combo[0] == 10:  # ENTER
                return ("open_below", {})
            else:  # WRITABLE KEY
                return ("add_char", {"chr": chr(key_combo[0])})
