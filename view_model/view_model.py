from model.model import UserInfo
from view.view import View
from pdb import set_trace

class ViewModel:
    def __init__(self):
        self.m = UserInfo()
        self.v = View()

    def recieve_commands(self):
        for command, content in self.v.send_command():
            try:
                getattr(self, command)(content)
            except AttributeError:
                self.warning("Illegal command {}".format(command))

    def quit_app(self, content=None):
        self.v.open = False 
