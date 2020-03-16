from view.modes import NormalMode, EditMode
import curses
import logging
log = logging.getLogger("wfcli")


class View:
    def __init__(self):
        self.active_message = None
        self.indent_size = 2
        self.inset = 1
        self.downset = 2

    @staticmethod
    def init_colors():
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)

    def __enter__(self):
        self.sc = curses.initscr()
        curses.start_color()
        self.init_colors()
        curses.noecho()
        curses.curs_set(False)
        curses.cbreak()
        self.sc.nodelay(True)
        self.open = True
        self.mode_map = {
            "normal": NormalMode(self.sc),
            "edit": EditMode(self.sc),
        }
        self.change_mode("normal")
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

    def send_command(self):
        while self.open:
            yield self.mode.get_command()

    @property
    def view_status(self):
        return None

    def print_message(self, message):
        self.active_message = message

    def generate_line(self, node, depth):
        def strikethrough(text):
            result = ''
            for c in text:
                result = result + c + '\u0336'
            return result
        label = strikethrough(node.name) if node.complete else node.name
        return "{} {} {}".format(
            " " * self.indent_size * depth,
            self.mode.indicators[node.state],
            label,
        )

    def render_content(self, content, cursor_position):
        displayed = []
        cline, ccol = cursor_position
        for node, depth in content:
            message = self.generate_line(node, depth)
            displayed.append(message)
        self.sc.clear()
        self.sc.border()
        message = self.active_message if self.active_message is not None else self.mode.note
        self.sc.addstr(1, 1, message)
        self.active_message = None
        for height, line in enumerate(displayed):
            attribute = self.mode.selection_attr if height == cline else curses.A_NORMAL
            self.sc.addstr(height + self.downset,
                           self.inset,
                           line,
                           attribute)
            if height == cline:
                cursor_y = self.inset + 3 + self.indent_size * content[height][1] + ccol
                log.info("Cursor_y" + str(cursor_y))
                self.sc.chgat(height + self.downset, cursor_y, 1, self.mode.cursor_attr)

        self.sc.refresh()
