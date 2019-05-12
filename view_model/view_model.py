from model.model import UserInfo
from view.view import View
from pdb import set_trace

class ViewModel:
    def __init__(self):
        self.m = UserInfo()
        self.v = View()

    def recieve_commands(self):
        for command, content in self.v.send_command():
            #from pudb.remote import set_trace
            #set_trace(term_size=(150, 70))
            try:
                getattr(self, command)(content)
            except AttributeError:
                self.warning("Illegal command {}".format(command))

    def quit_app(self, content=None):
        self.v.open = False 

    def load_root_content(self, content={}):
        user_content = self.m.get_root_content()
        self.v.display_root_content(user_content)

    def warning(self, message):
        self.v.print_message(message)

    def nav_right(self, content):
        self.v.nav_right()
