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
        self.indent_size = 2
        self.inset = 1
        self.downset = 1
        self.mode_map = {
            "normal": NormalMode(),
            "edit": EditMode(),
        }
        self.change_mode("normal")

    @staticmethod
    def init_colors():
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    def __enter__(self):
        self.sc = curses.initscr()
        curses.start_color()
        self.init_colors()
        curses.noecho()
        curses.curs_set(False)
        curses.cbreak()
        self.sc.nodelay(True)
        self.open = True
        self.keygen = self.get_keypress_wait()
        return self

    def __exit__(self, *args):
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def send_command(self):
        while self.open:
            yield self.mode.get_command(self.keygen)

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

    # KEYPRESS METHODS

    def get_keypress_no_wait(self):
        return self.sc.getch()

    def get_keypress_wait(self):
        while True:
            keypress = self.sc.getch()
            if keypress < 0:
                continue
            # 27 is a special case, because it could mean I pressed
            # the escape key, or it could mean it's an escape code
            if keypress == 27:
                a = self.get_keypress_no_wait()
                if a == -1:
                    yield 27
                else:
                    b = self.get_keypress_no_wait()
                    if b == -1:
                        yield 27
                        yield a
                    else:
                        yield (27, a, b)

            yield keypress

    # PRINTING METHODS
    def generate_lines(self, text, text_width):
        if text == "":
            return [""]
        res = []
        lead_index = 0
        while lead_index < len(text):
            res.append(text[lead_index:lead_index + text_width])
            lead_index += text_width
        return res

    def render_content(self, content, curs_y):
        additional_lines = 0
        rows, cols = self.sc.getmaxyx()
        for height, node_tuple in enumerate(content):
            node, depth = node_tuple
            indent_width = self.indent_size * depth + 3
            text_width = cols - indent_width - 2
            lines = self.generate_lines(node.name, text_width)
            attribute = self.mode.selection_attr if height == curs_y else curses.A_NORMAL
            if height + self.downset + additional_lines + len(lines) >= rows - 1:
                break  # stop us from going past the end of the screen!
            new_additional_lines = -1

            # Actual text
            for line in lines:
                new_additional_lines += 1
                # indent space
                self.sc.addstr(height + self.downset + additional_lines + new_additional_lines,
                               self.inset,
                               indent_width * " ",
                               attribute)
                # indicator
                if new_additional_lines == 0:
                    self.sc.addstr(height + self.downset + additional_lines,
                                   self.inset + indent_width - 2,
                                   self.mode.indicators[node.state],
                                   attribute)

                # real content
                self.sc.addstr(height + self.downset + additional_lines + new_additional_lines,
                               self.inset + indent_width,
                               line,
                               attribute)
                self.sc.clrtoeol()

            # Cursor block
            if height == curs_y:
                simple_position = self.cursor_x(node_tuple)
                extra_downset = simple_position // text_width
                extra_inset = simple_position % text_width
                cursor_x = self.inset + indent_width + extra_inset
                cursor_y = self.downset + height + additional_lines + extra_downset
                self.sc.chgat(cursor_y, cursor_x, 1, self.mode.cursor_attr)

            additional_lines += new_additional_lines
        # CLEAR EVERYTHING BELOW
        y_to_delete_from = height + additional_lines + 2
        if y_to_delete_from < rows:
            self.sc.move(y_to_delete_from, 0)
            self.sc.clrtobot()
        # MAKE COLORED BORDER
        self.sc.attrset(self.mode.border_attr)
        self.sc.border()
        self.sc.attrset(0)

        # DRAW TO SCREEN
        self.sc.refresh()
