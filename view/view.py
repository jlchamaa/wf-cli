from view.modes import NormalMode, EditMode
import curses
import logging
log = logging.getLogger("wfcli")


class View:
    def __init__(self):
        self.active_message = None

    def __enter__(self):
        self.sc = curses.initscr()
        curses.noecho()
        curses.curs_set(False)
        curses.cbreak()
        # try:
        #     curses.start_color()
        # except :
        #     pass
        self.sc.nodelay(True)
        self.open = True
        self.mode_map = {
            "normal": NormalMode(self.sc),
            "edit": EditMode(self.sc),
        }
        self.change_mode("normal")
        self.render_content([], 0)
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
            "  "*depth,
            self.mode.indicators[node.state],
            label,
        )

    def render_content(self, content, cursor_position):
        displayed = []
        for node, depth in content:
            message = self.generate_line(node, depth)
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
