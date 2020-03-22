from view.modes import NormalMode


class EditMode(NormalMode):
    key_mapping = {
        (27,): "normal_mode",  # RETURN TO NORMAL MODE
        (127,): "delete_char",      # BACKSPACE
        (9,): "indent",             # TAB
        (27, 91, 90): "unindent",   # SHIFT-TAB
        (10,): "open_below",        # ENTER
    }

    @property
    def eol_offset(self):
        return 1

    @property
    def note(self):
        return "Edit Mode"

    def get_command(self):
        key_combo = self.get_keycombo()
        if key_combo in self.key_mapping:
            return (self.key_mapping[key_combo],)
        else:
            if key_combo[0] == 27:  # ESC
                return ("normal_mode",)
            else:  # WRITABLE KEY
                return ("add_char", {"char": chr(key_combo[0])})
