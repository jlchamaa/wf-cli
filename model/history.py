import copy
import logging
log = logging.getLogger("wfcli")


class History:
    def __init__(self, seed, history_file=None):
        self.current = copy.deepcopy(seed)
        if history_file is None:
            self._undo_list = []
        else:
            self._load_from_history_file(history_file)
        self._redo_list = []

    def add(self, nds):
        if nds != self.current:
            self._undo_list.append(self.current)
            self.current = copy.deepcopy(nds)
            self._redo_list = []

    def undo(self):
        if len(self._undo_list) > 0:
            self._redo_list.append(self.current)
            self.current = self._undo_list.pop()
            return copy.deepcopy(self.current)
        else:
            print('\a')
            return None

    def redo(self):
        if len(self._redo_list) > 0:
            self._undo_list.append(self.current)
            self.current = self._redo_list.pop()
            return copy.deepcopy(self.current)
        else:
            print('\a')
            return None

    def _load_from_history_file(self, history_file):
        raise NotImplementedError
