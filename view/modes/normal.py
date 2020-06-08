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
        ord('r'): "render",
        ord('s'): "save_data",
        ord('u'): "undo",
        ord('0'): "zero",
        ord('$'): "dollar_sign",
        curses.KEY_RESIZE: "render",
        9: "indent",              # TAB
        10: "open_below",         # ENTER
        18: "redo",               # CTRL+R
        (27, 91, 90): "unindent"  # SHIFT-TAB
    }

    @property
    def indicators(self):
        return {
            "closed": "✚",
            "open": "v",
            "item": "-",
            "complete_item": "✓",
            "complete_parent": "✷",
        }

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

    @property
    def border_attr(self):
        return curses.color_pair(0)

    def get_command(self, keygen):
        dict_to_inspect = self.key_mapping
        while True:
            try:
                keypress = next(keygen)
                result = dict_to_inspect[keypress]
                if isinstance(result, dict):
                    dict_to_inspect = result
                elif isinstance(result, str):
                    return (result, {})
            except KeyError:
                log.error("No command for {}".format(keypress))
                dict_to_inspect = self.key_mapping
