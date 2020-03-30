import curses
import logging
log = logging.getLogger("wfcli")


class NormalMode:
    key_mapping = {
        ord('A'): "edit_EOL",
        ord('D'): "delete_item",
        ord('G'): "bottom",
        ord('c'): "complete",
        ord('g'): {
            ord('g'): "top"
        },
        ord('i'): "edit_mode",
        ord('k'): "nav_up",
        ord('j'): "nav_down",
        ord('h'): "nav_left",
        ord('l'): "nav_right",
        ord('H'): "collapse_node",
        ord('L'): "expand_node",
        ord('o'): "open_below",
        ord('p'): "print_data",
        ord('q'): "quit_app",
        ord('s'): "save_data",
        ord('u'): "undo",
        ord('0'): "zero",
        ord('$'): "dollar_sign",
        9: "indent",            # TAB
        10: "open_below",       # ENTER
        (27, 91, 90): "unindent"  # SHIFT-TAB
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

    def get_keypress(self, screen, wait=True):
        while True:
            keypress = screen.getch()
            if keypress < 0:
                if wait:
                    continue
                else:
                    return keypress
            # 27 is a special case, because it could mean I pressed
            # the escape key, or it could mean it's an escape code
            if keypress == 27:
                a = self.get_keypress(screen, wait=False)
                if a == -1:
                    return 27
                else:
                    b = self.get_keypress(screen, wait=False)
                    return (27, a, b)

            return keypress

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
                log.error("This command is dogshit")
                dict_to_inspect = self.key_mapping
