from view.keypress import key_mapping
import curses
import logging
import os
log = logging.getLogger("wfcli")


class View:
    def __init__(self):
        self.cursor_index = 0
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
        self.render_homescreen()
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
            else:
                if keypress in key_mapping:
                    result = key_mapping[keypress]
                    yield (result, self.view_status)
                log.info("KEYPRESS: {}".format(chr(keypress)))

    @property
    def view_status(self):
        try:
            id_under_cursor = self.content[self.cursor_index].uuid
            return {"id_selected": id_under_cursor}
        except IndexError:
            return {"id_selected": None}

    def print_message(self, message):
        self.sc.addstr(1, 1, message)

    def render_content(self, content):
        self.displayed = []
        self.content = content
        for name, depth, state in content:
            message = "{} {} {}".format("  "*depth, self.indicators[state], name)
            self.displayed.append(message)
        self.sc.clear()
        self.sc.border()
        self.print_message("This is WorkFlowy-CLI")
        for height, line in enumerate(self.displayed):
            attribute = curses.A_REVERSE if height == self.cursor_index else curses.A_NORMAL
            self.sc.addstr(height + 2,
                           1,
                           line,
                           attribute)
        self.sc.refresh()

    def nav_left(self):
        original_depth = self.displayed[self.cursor_index].depth
        original_index = self.cursor_index
        current_index = original_index + 1
        while current_index < len(self.displayed) and self.displayed[current_index].depth > original_depth:
            del self.displayed[current_index]
        self.render_homescreen()

    def nav_right(self, children):
        current_depth = self.displayed[self.cursor_index].depth
        original_index = self.cursor_index
        for child in children:
            original_index += 1
            new_node = Node(child.uuid, child.name, current_depth + 1)
            self.displayed.insert(original_index, new_node)
        self.render_homescreen()

    def nav_up(self):
        if self.cursor_index > 0:
            self.cursor_index -= 1
            self.render_homescreen()

    def nav_down(self):
        if self.cursor_index < len(self.displayed) - 1:
            self.cursor_index += 1
            self.render_homescreen()
