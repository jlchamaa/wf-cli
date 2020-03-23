import logging
from model.file_based import UserFile
from view.view import View


log = logging.getLogger("wfcli")


class ViewModel:
    # SETUP METHODS
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
        for payload in self.v.send_command():
            try:
                if len(payload) == 2:  # payload has a kwargs
                    getattr(self, payload[0])(**payload[1])
                elif len(payload) == 1:  # payload is just a command
                    getattr(self, payload[0])()
                else:
                    raise ValueError("Payload of len {}, {}".format(
                        len(payload),
                        payload,
                    ))
            except AttributeError as ae:
                log.error("Command: {}\nError:{}".format(payload[0], ae))

    def quit_app(self, **kwargs):
        self.v.open = False
        log.error("Closing App Legitimately")

    # PRINTING METHODS
    def render(self, **kwargs):
        log.info("Render")
        self.v.render_content(
            self.visible_nodes,
            self.cursor_y,
        )

    # COMMIT AND SAVE METHODS
    def commit_data(self, **kwargs):
        self.m.commit()

    def save_data(self, **kwargs):
        self.m.save()
        log.info("saved")

    def commit_and_save_data(self, **kwargs):
        self.commit_data()
        self.save_data()

    def undo(self, content={}):
        log.info("Undo")

    # STATE METHODS
    @property
    def visible_nodes(self):
        return self.m.visible

    @property
    def current_node(self, depth=False):
        return self.m.current_node

    @property
    def cursor_x(self):
        return self.v.cursor_x(self.current_node())

    @property
    def cursor_y(self):
        return self.m.cursor_y

    # NAVIGATION METHODS
    def nav_left(self, **kwargs):
        self.v.nav_left(self.current_node(depth=True))
        self.save_data()
        self.render()

    def nav_right(self, **kwargs):
        self.v.nav_right(self.current_node(depth=True))
        self.save_data()
        self.render()

    def nav_up(self, **kwargs):
        self.m.nav_up()
        self.save_data()
        self.render()

    def nav_down(self, **kwargs):
        self.m.nav_down()
        self.save_data()
        self.render()

    def zero(self, **kwargs):
        self.v.zero()
        self.render()

    def dollar_sign(self, **kwargs):
        self.v.dollar_sign()
        self.render()

    # EDIT NODE OBJECTS
    def indent(self, **kwargs):
        self.m.indent()
        self.commit_and_save_data()
        self.render()

    def unindent(self, **kwargs):
        self.m.unindent()
        self.commit_and_save_data()
        self.render()

    def expand_node(self, **kwargs):
        self.m.expand_node()
        self.commit_and_save_data()
        self.render()

    def collapse_node(self, **kwargs):
        self.m.collapse_node()
        self.commit_and_save_data()
        self.render()

    def open_below(self, **kwargs):
        self.edit_mode()
        self.m.open_below()
        self.nav_down()
        self.commit_and_save_data()
        self.render()

    def complete(self, **kwargs):
        self.m.complete()
        self.commit_and_save_data()
        self.render()

    def delete_item(self, **kwargs):
        log.info("Delete Item")
        self.m.delete_item()
        self.commit_and_save_data()
        self.render()

    def print_data(self, **kwargs):
        log.info("Visible nodes\n=====")
        for node, depth in self.visible_nodes:
            log.info(node)
        log.info("All nodes\n=====")
        for key, value in self.m.nodes.items():
            log.info(value)

    # EDIT TEXT
    def add_char(self, char="", **kwargs):
        log.info("I'm adding a '{}' here".format(char))
        self.m.add_char(char, self.cursor_x)
        self.save_data()
        self.nav_right()
        self.render()

    def delete_char(self, num=1, **kwargs):
        log.info("I'm deleting here")
        self.m.delete_char(num, self.cursor_x)
        self.save_data()
        self.nav_left()
        self.render()

    # MODE CHANGING
    def normal_mode(self, **kwargs):
        log.info("Changing mode to normal")
        self.v.change_mode("normal")
        if not self.v.align_cursor(self.current_node()):
            self.nav_left()
        self.commit_and_save_data()
        self.render()

    def edit_mode(self, **kwargs):
        log.info("Changing mode to edit")
        self.v.align_cursor(self.current_node())
        self.v.change_mode("edit")
        self.commit_and_save_data()
        self.render()
