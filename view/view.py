import curses
class View:
    def __init__(self):
        curses.wrapper(self.main)

    def main(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.clear()
        self.render_homescreen()
        self.open = True

    def render_homescreen(self):
        self.stdscr.addstr(2, 2, "This is the homescreen")

    def send_command(self):
        while self.open:
            keypress = self.stdscr.getkey()
            if keypress == "q":
                yield ("quit_app", {})
