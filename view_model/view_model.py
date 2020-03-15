import logging
from model.file_based import UserFile
from view.view import View


log = logging.getLogger("wfcli")


class ViewModel:
    def __init__(self):
        self.m = UserFile()
        try:
            with View() as self.v:
                self.render()
                self.recieve_commands()
        except BaseException as be:
            log.error("Exception {} raised.  Shut down".format(be))
            raise be

    def recieve_commands(self):
        for command, content in self.v.send_command():
            try:
                getattr(self, command)(content=content)
            except AttributeError as ae:
                log.error("Command: {}\nError:{}".format(command, ae))
                self.warning("Illegal command {}".format(command))

    def quit_app(self, content=None):
        self.v.open = False
        log.error("Closing App Legitimately")

    def render(self, content={}):
        self.v.render_content(
            self.visible_nodes,
            self.cursor_position,
        )

    def commit_data(self, content={}):
        self.m.commit()

    def save_data(self, content={}):
        self.m.save()
        log.info("saved")

    def commit_and_save_data(self, content={}):
        self.commit_data()
        self.save_data()

    @property
    def visible_nodes(self):
        return self.m.load_visible()

    @property
    def cursor_position(self):
        return self.m.cursor_position

    def warning(self, message):
        self.v.print_message(message)

    def indent(self, content={}):
        log.info("Indent invoked in ViewModel")
        self.m.indent()
        self.commit_and_save_data()
        self.render()
        log.info("Indent completed in ViewModel")

    def unindent(self, content={}):
        log.info("Unindent invoked in ViewModel")
        self.m.unindent()
        self.commit_and_save_data()
        self.render()
        log.info("Unindent completed in ViewModel")

    def nav_left(self, content={}):
        log.info("Nav_left invoked in ViewModel")
        self.m.nav_left()
        self.commit_and_save_data()
        self.render()
        log.info("Nav_left completed in ViewModel")

    def nav_right(self, content={}):
        log.info("Nav_right invoked in ViewModel")
        self.m.nav_right()
        self.commit_and_save_data()
        self.render()
        log.info("Nav_right completed in ViewModel")

    def nav_up(self, content={}):
        self.m.nav_up()
        self.save_data()
        self.render()

    def nav_down(self, content={}):
        self.m.nav_down()
        self.save_data()
        self.render()

    def print_data(self, content={}):
        log.info("Visible nodes\n=====")
        for node, depth in self.visible_nodes:
            log.info(node)
        log.info("All nodes\n=====")
        for key, value in self.m.nodes.items():
            log.info(value)

    def open_below(self, content={}):
        self.v.change_mode("edit")
        self.m.open_below()
        self.save_data()
        self.render()

    def complete(self, content={}):
        self.m.complete()
        self.commit_and_save_data()
        self.render()

    def delete_item(self, content={}):
        self.m.delete_item()
        self.commit_and_save_data()
        self.render()

    def add_char(self, content={"chr": ' '}):
        log.info("I'm adding a '{}' here".format(content["chr"]))
        self.render()

    def delete_char(self, content={"num": 1}):
        log.info("I'm deleting here")
        self.render()

    def undo(self, content={}):
        pass

    def change_view_mode(self, content={"mode": "normal"}):
        self.v.change_mode(content["mode"])
        log.info("Chnaging mode to {}".format(content["mode"]))
        self.render()
