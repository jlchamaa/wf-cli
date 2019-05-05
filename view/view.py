import curses
import os


class View:
    def __init__(self):
        self.log_file = os.path.expanduser("~/.log_from_wfcli")

    def render_homescreen(self):
        self.sc.border()
        self.sc.addstr(2, 2, "This is the homescreen")

    def log_input(self, to_log):
        with open(self.log_file, "a+") as f:
            f.write("{}".format(to_log))


    def send_command(self):
        try:
            self.sc = curses.initscr()
            curses.noecho()
            curses.cbreak()
            try:
                curses.start_color()
            except:
                pass
            self.sc.clear()
            self.sc.nodelay(True)
            self.render_homescreen()
            self.open = True
            while self.open:
                try:
                    keypress = self.sc.getkey()
                except:
                    continue
                self.log_input(keypress)
                if keypress == "q":
                    yield ("quit_app", {})
        finally:
            curses.echo()
            curses.nocbreak()
            curses.endwin()
