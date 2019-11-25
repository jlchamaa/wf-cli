from view.keypress import key_mapping
import curses
import logging
import os
log = logging.getLogger("wfcli")


class View:
    def __init__(self):
        self.displayed = []
        self.indicators = {"closed": ">", "open": "v", "item": "-"}

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

    def __exit__(self, exc_type, exc_val, exc_tb):
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def send_command(self):
        while self.open:
            keypress = self.sc.getch()
            if keypress < 0:
                continue
            if keypress == 27:  # an ESCAPE code
                key_combo = []
                while keypress >= 0:
                    key_combo.append(keypress)
                    keypress = self.sc.getch()
                keypress = tuple(key_combo)
            log.info("KEYPRESS: {}".format(str(keypress)))
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
        self.sc.addstr(1, 1, message)

    def render_content(self, content, cursor_position):
        self.displayed = []
        for node, depth in content:
            message = "{} {} {}".format("  "*depth, self.indicators[node.state], node.name)
            self.displayed.append(message)
        self.sc.clear()
        self.sc.border()
        self.print_message("This is WorkFlowy-CLI")
        for height, line in enumerate(self.displayed):
            attribute = curses.A_REVERSE if height == cursor_position else curses.A_NORMAL
            self.sc.addstr(height + 2,
                           1,
                           line,
                           attribute)
        self.sc.refresh()
