from view.keypress import key_mapping
from collections import namedtuple
import curses
import logging
import os
log = logging.getLogger("wfcli")

Mode = namedtuple("Mode", "indicators note selection")
NormalMode = Mode({"closed": ">", "open": "v", "item": "-"}, "Normal Mode", curses.A_REVERSE)
EditMode = Mode({"closed": ">", "open": "v", "item": "-"}, "Edit Mode", curses.A_REVERSE)


class View:
    def __init__(self):
        self.mode = NormalMode
        self.mode_map = {
            "normal": NormalMode,
            "edit": EditMode,
        }
        self.active_message = None

    def __enter__(self):
        self.sc = curses.initscr()
        curses.noecho()
        curses.curs_set(False)
        curses.cbreak()
        try:
            curses.start_color()
        except:
            pass
        self.sc.nodelay(True)
        self.render_content([], 0)
        self.open = True
        return self

    def __exit__(self, *args):
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def change_mode(self, mode):
        if mode in self.mode_map:
            self.mode = self.mode_map[mode]
        else:
            raise ValueError("There isn't a {} mode".format(mode))

    def get_keypress(self):
        while True:
            keypress = self.sc.getch()
            if keypress < 0:
                continue
            if keypress == 27:  # an ESCAPE code
                key_combo = []
                while keypress >= 0:
                    key_combo.append(keypress)
                    keypress = self.sc.getch()
            else:
                key_combo = [keypress]
            key_combo = tuple(key_combo)
            log.info("KEYPRESS: {}".format(str(key_combo)))
            return key_combo

    def send_command(self):
        while self.open:
            keypress = self.get_keypress()
            if keypress in key_mapping:
                result = key_mapping[keypress]
                yield (result, self.view_status)

    @property
    def view_status(self):
        return None
        # try:
        #     id_under_cursor = self.content[self.cursor_index].uuid
        #     return {"id_selected": id_under_cursor}
        # except IndexError:
        #     return {"id_selected": None}

    def print_message(self, message):
        self.active_message = message

    def render_content(self, content, cursor_position):
        displayed = []
        for node, depth in content:
            message = "{} {} {}".format("  "*depth, self.mode.indicators[node.state], node.name)
            displayed.append(message)
        self.sc.clear()
        self.sc.border()
        message = self.active_message if self.active_message is not None else self.mode.note
        self.sc.addstr(1, 1, message)
        self.active_message = None
        for height, line in enumerate(displayed):
            attribute = self.mode.selection if height == cursor_position else curses.A_NORMAL
            self.sc.addstr(height + 2,
                           1,
                           line,
                           attribute)
        self.sc.refresh()
