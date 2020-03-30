import curses
import logging
log = logging.getLogger("wfcli")


class NormalMode:
    key_mapping = {
        (ord('A'),): "edit_EOL",
        (ord('D'),): "delete_item",
        (ord('c'),): "complete",
        (ord('i'),): "edit_mode",
        (ord('k'),): "nav_up",
        (ord('j'),): "nav_down",
        (ord('h'),): "nav_left",
        (ord('l'),): "nav_right",
        (ord('H'),): "collapse_node",
        (ord('L'),): "expand_node",
        (ord('o'),): "open_below",
        (ord('p'),): "print_data",
        (ord('q'),): "quit_app",
        (ord('s'),): "save_data",
        (ord('u'),): "undo",
        (ord('0'),): "zero",
        (ord('$'),): "dollar_sign",
        (9,): "indent",            # TAB
        (10,): "open_below",       # ENTER
        (27, 91, 90): "unindent",  # SHIFT-TAB
    }

    @property
    def indicators(self):
        return {"closed": ">", "open": "v", "item": "-"}

    @property
    def eol_offset(self):
        return 0

    @property
    def note(self):
        return "Normal Mode"

    @property
    def cursor_attr(self):
        return curses.color_pair(2)

    @property
    def selection_attr(self):
        return curses.color_pair(1)

    def get_keycombo(self, screen):
        while True:
            keypress = screen.getch()
            if keypress < 0:
                continue
            elif keypress == 27:  # an ESCAPE code
                key_combo = []
                while keypress >= 0:
                    key_combo.append(keypress)
                    keypress = screen.getch()
            else:
                key_combo = [keypress]
            key_combo = tuple(key_combo)
            return key_combo

    def get_command(self, screen):
        while True:
            key_combo = self.get_keycombo(screen)
            if key_combo in self.key_mapping:
                result = self.key_mapping[key_combo]
                return (result, {})
            else:
                log.error("This command is dogshit - {}".format(key_combo))
