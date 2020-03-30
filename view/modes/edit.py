from view.modes import NormalMode


class EditMode(NormalMode):
    key_mapping = {
        27: "normal_mode",  # RETURN TO NORMAL MODE
        127: "delete_char",      # BACKSPACE
        9: "indent",             # TAB
        10: "open_below",        # ENTER
        (27, 91, 90): "unindent",   # SHIFT-TAB
        (27, 91, 67): "nav_right",  # RIGHT ARROW
    }

    @property
    def eol_offset(self):
        return 1

    @property
    def note(self):
        return "Edit Mode"

    def get_command(self, screen):
        dict_to_inspect = self.key_mapping
        while True:
            try:
                keypress = self.get_keypress(screen)
                result = dict_to_inspect[keypress]
                if isinstance(result, dict):
                    dict_to_inspect = result
                elif isinstance(result, str):
                    return (result, {})
            except KeyError:
                if isinstance(keypress, int):
                    return ("add_char", {"char": chr(keypress)})
                dict_to_inspect = self.key_mapping
