from view.modes import NormalMode, EditMode
import curses
import logging
log = logging.getLogger("wfcli")


class View:
    # SETUP METHODS
    def __init__(self):
        self.active_message = None
        self._cursor_x = 0
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

    def send_command(self):
        while self.open:
            yield self.mode.get_command()

    # MODE METHODS
    def change_mode(self, mode):
        if mode in self.mode_map:
            self.mode = self.mode_map[mode]
        else:
            raise ValueError("There isn't a {} mode".format(mode))

    # CURSOR METHODS
    def align_cursor(self, current_node):
        if self._cursor_x != self.cursor_x(current_node):
            self._cursor_x = self.cursor_x(current_node)
            return True
        return False

    def cursor_x(self, current_node):
        linelength = max(
            len(current_node.name) - 1 + self.mode.eol_offset,
            0,
        )
        current = self._cursor_x
        res = min(linelength, current)
        log.info("Comp {}:{}, return {}".format(linelength, current, res))
        return res

    def nav_left(self, current_node):
        found_x = self.cursor_x(current_node[0])
        if found_x > 0:
            self._cursor_x = found_x - 1
        else:
            self._cursor_x = 0

    def nav_right(self, current_node):
        found_x = self.cursor_x(current_node[0])
        log.info("Nav_right found_x: {}".format(found_x))
        max_allowed = len(current_node[0].name) - 1 + self.mode.eol_offset
        log.info("Nav_right max: {}".format(max_allowed))
        if found_x < max_allowed:
            self._cursor_x = found_x + 1
        else:
            self._cursor_x = max_allowed

    def dollar_sign(self):
        self._cursor_x = float("Inf")

    def zero(self):
        self._cursor_x = 0

    # PRINTING METHODS
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

    def render_content(self, content, curs_y):
        self.sc.clear()
        self.sc.border()
        message = self.active_message if self.active_message is not None else self.mode.note
        self.sc.addstr(1, 1, message)
        self.active_message = None
        for height, node_tuple in enumerate(content):
            node, depth = node_tuple
            message = self.generate_line(node, depth)
            attribute = self.mode.selection_attr if height == curs_y else curses.A_NORMAL
            self.sc.addstr(height + self.downset,
                           self.inset,
                           message,
                           attribute)
            if height == curs_y:
                cursor_x = (self.inset
                            + 3
                            + self.indent_size * depth
                            + self.cursor_x(node)
                            )
                self.sc.chgat(height + self.downset, cursor_x, 1, self.mode.cursor_attr)

        self.sc.refresh()
