import copy
import logging
log = logging.getLogger("wfcli")


class History:
    def __init__(self, history_file=None):
        if history_file is None:
            self._undo_list = []
        else:
            self._load_from_history_file(history_file)
        self._redo_list = []

    def add(self, nds):
        log.info("we're in the addition")
        if len(self._undo_list) == 0 or nds.digest != self._undo_list[-1].digest:
            log.info("we've added!")
            self._undo_list.append(copy.deepcopy(nds))
            self._redo_list = []
            log.info(len(self._undo_list))

    def undo(self):
        if len(self._undo_list) > 0:
            popped = self._undo_list.pop()
            self._redo_list.append(popped)
            return copy.deepcopy(popped)
        else:
            print('\a')
            return None

    def redo(self):
        if len(self._redo_list) > 0:
            popped = self._redo_list.pop()
            self._undo_list.append(popped)
            return copy.deepcopy(popped)
        else:
            print('\a')
            return None

    def _load_from_history_file(self, history_file):
        raise NotImplementedError
