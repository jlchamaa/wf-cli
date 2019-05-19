from view.keypress import key_mapping
import curses
import os


class Node:
    def __init__(self, node_id, name, depth=0):
        self.node_id = node_id
        self.name = name
        self.depth = depth
        self.closed = True


class View:
    def __init__(self):
        self.log_file = os.path.expanduser("~/.log_from_wfcli")
        self.cursor_index = 0
        self.displayed = []

    def send_command(self):
        try:
            self.sc = curses.initscr()
            curses.noecho()
            curses.cbreak()
            try:
                curses.start_color()
            except:
                pass
            self.sc.nodelay(True)
            self.render_homescreen()
            self.open = True
            while self.open:
                keypress = self.sc.getch()
                if keypress < 0:
                    continue
                else:
                    if keypress in key_mapping:
                        result = key_mapping[keypress]
                        yield (result, self.view_status)
                    self.log_input(keypress)
        finally:
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    @property
    def view_status(self):
        try:
            id_under_cursor = self.displayed[self.cursor_index].node_id
            return {"id_selected": id_under_cursor}
        except IndexError:
            return {"id_selected": None}

    def print_message(self, message):
        self.sc.addstr(1, 1, message)

    def render_homescreen(self):
        self.sc.clear()
        self.sc.border()
        self.print_message("This is WorkFlowy-CLI")
        for height, line in enumerate(self.displayed):
            indicator = "-" if line.closed else "v"
            message = "{} {}".format(indicator, line.name)
            attribute = curses.A_REVERSE if height == self.cursor_index else curses.A_NORMAL
            self.sc.addstr(height + 2,
                           (line.depth + 1) * 2,
                           message,
                           attribute)
        self.sc.refresh()

    def log_input(self, to_log):
        with open(self.log_file, "a+") as f:
            f.write("{}".format(to_log))

    def display_root_content(self, content):
        for node in content:
            new_node = Node(node[1], node[0], 0)
            self.displayed.append(new_node)
        self.render_homescreen()

    def nav_left(self):
        pass

    def nav_right(self):
        pass

    def nav_up(self):
        if self.cursor_index > 0:
            self.cursor_index -= 1
            self.render_homescreen()

    def nav_down(self):
        if self.cursor_index < len(self.displayed) - 1:
            self.cursor_index += 1
            self.render_homescreen()
