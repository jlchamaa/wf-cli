#from model.wf_account import UserInfo
import logging
import time
from model.file_based import UserFile
from view.view import View
from pudb.remote import set_trace as pst


log = logging.getLogger("wfcli")


class ViewModel:
    def __init__(self):
        self.m = UserFile()
        with View() as self.v:
            self.render()
            # pst(term_size=(300,80))
            self.recieve_commands()

    def recieve_commands(self):
        for command, content in self.v.send_command():
            try:
                getattr(self, command)(content)
            except AttributeError as ae:
                log.error("Command: {}\nError:{}".format(command, ae))
                self.warning("Illegal command {}".format(command))

    def quit_app(self, content=None):
        self.v.open = False 

    def render(self, content={}):
        self.v.render_content(
            self.visible_nodes,
            self.cursor_position,
        )

    def save_data(self, content):
        self.m.save_data()

    @property
    def visible_nodes(self):
        return self.m.load_visible()

    @property
    def cursor_position(self):
        return self.m.cursor_position

    def warning(self, message):
        self.v.print_message(message)

    def indent(self, message):
        message = self.m.indent()
        if message:
            self.warning(message)
        self.render()

    def unindent(self, message):
        message = self.m.unindent()
        if message:
            self.warning(message)
        self.render()

    def nav_left(self, content):
        self.m.nav_left()
        self.render()

    def nav_right(self, content):
        self.m.nav_right()
        self.render()

    def nav_up(self, content):
        self.m.nav_up()
        self.render()

    def nav_down(self, content):
        self.m.nav_down()
        self.render()

    def print_data(self, content):
        log.info("Visible nodes\n=====")
        for node, depth in self.visible_nodes:
            log.info(node)
        log.info("All nodes\n=====")
        for key,value  in self.m.nodes.items():
            log.info(value)

    def open_below(self, content):
        edit_mode = True
        self.v.change_mode("edit")
        new_node = self.m.open_below()
        while edit_mode:
            self.render()
            key_combo = self.v.get_keypress()
            if len(key_combo) > 1:
                edit_mode = False
            else:
                if key_combo[0] == 27:
                    edit_mode = False
                else:
                    new_node.name += chr(key_combo[0])
        self.v.change_mode("normal")
        self.render()
