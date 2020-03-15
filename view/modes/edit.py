from view.modes import NormalMode


class EditMode(NormalMode):
    @property
    def note(self):
        return "Edit Mode"
