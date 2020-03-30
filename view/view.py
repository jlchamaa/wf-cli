from view.modes import NormalMode, EditMode
import curses
import logging
log = logging.getLogger("wfcli")


class LateralCursor:
    def __init__(self):
        self._index = float("-Inf")
        self.allowed_offset = 0

    def align_cursor(self, current_node):
        if self._index != self.in_line(current_node):
            self._index = self.in_line(current_node)
            return True
        return False

    def in_line(self, node_pair):
        current_node = node_pair[0]
        linelength = max(
            len(current_node.name) - 1 + self.allowed_offset,
            0,
        )
        current = max(0, self._index)
        res = min(linelength, current)
        log.info("Comp {}:{}, return {}".format(linelength, current, res))
        return res

    def nav_left(self, current_node):
        found_x = self.in_line(current_node)
        if found_x > 0:
            self._index = found_x - 1
        else:
            self._index = 0

    def nav_right(self, current_node):
        found_x = self.in_line(current_node)
        log.info("Nav_right found_x: {}".format(found_x))
        max_allowed = len(current_node[0].name) - 1 + self.allowed_offset
        log.info("Nav_right max: {}".format(max_allowed))
        if found_x < max_allowed:
            self._index = found_x + 1
        else:
            self._index = max_allowed

    def dollar_sign(self):
        self._index = float("Inf")

    def zero(self):
        self._index = float("-Inf")


class View:
    # SETUP METHODS
    def __init__(self):
        self.lc = LateralCursor()
        self.active_message = None
        self.indent_size = 2
        self.inset = 1
        self.downset = 2
        self.mode_map = {
            "normal": NormalMode(),
            "edit": EditMode(),
        }
        self.change_mode("normal")

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
        return self

    def __exit__(self, *args):
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def send_command(self):
        while self.open:
            yield self.mode.get_command(self.sc)

    # MODE METHODS
    def change_mode(self, mode):
        if mode in self.mode_map:
            self.mode = self.mode_map[mode]
            self.lc.allowed_offset = self.mode.eol_offset
        else:
            raise ValueError("There isn't a {} mode".format(mode))

    # CURSOR METHODS
    def align_cursor(self, current_node):
        return self.lc.align_cursor(current_node)

    def cursor_x(self, current_node):
        return self.lc.in_line(current_node)

    def nav_left(self, current_node):
        self.lc.nav_left(current_node)

    def nav_right(self, current_node):
        self.lc.nav_right(current_node)

    # PRINTING METHODS
    def generate_line(self, node_tuple):
        def strikethrough(text):
            result = ''
            for c in text:
                result = result + c + '\u0336'
            return result
        node, depth = node_tuple
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
            message = self.generate_line(node_tuple)
            attribute = self.mode.selection_attr if height == curs_y else curses.A_NORMAL
            self.sc.addstr(height + self.downset,
                           self.inset,
                           message,
                           attribute)
            if height == curs_y:
                cursor_x = (self.inset
                            + 3
                            + self.indent_size * node_tuple[1]
                            + self.cursor_x(node_tuple)
                            )
                self.sc.chgat(height + self.downset, cursor_x, 1, self.mode.cursor_attr)

        self.sc.refresh()
