#from model.wf_account import UserInfo
from model.file_based import UserFile
from view.view import View
from pdb import set_trace

class ViewModel:
    def __init__(self):
        self.m = UserFile()
        with View() as self.v:
            self.render()
            self.recieve_commands()

    def recieve_commands(self):
        for command, content in self.v.send_command():
            try:
                getattr(self, command)(content)
            except AttributeError:
                self.warning("Illegal command {}".format(command))

    def quit_app(self, content=None):
        self.v.open = False 

    def render(self, content={}):
        self.v.render_content(self.m.load_visible())

    def save_data(self, content):
        self.m.save_data()

    def warning(self, message):
        self.v.print_message(message)

    def nav_left(self, content):
        self.v.nav_left()

    def nav_right(self, content):
        id_selected = self.v.view_status["id_selected"]
        children = self.m.get_children(id_selected)
        self.v.nav_right(children)

    def nav_up(self, content):
        self.v.nav_up()

    def nav_down(self, content):
        self.v.nav_down()
