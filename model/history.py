import copy
import hashlib
from collections import namedtuple


Entry = namedtuple("Entry", "nodes cursor_position nodes_hash")

class History:
    def __init__(self, history_file=None):
        if history_file is None:
            self._undo_list = []
        else:
            self._load_from_history_file(history_file)


    def add(self, nodes, cursor_position):
        pass
        # entry = self._create_entry(nodes, cursor_position)

    def _create_entry(self, nodes, cursor_position):
        nodes_copy = copy.deepcopy(nodes)
        digest = hashlib.sha1(nodes_copy)



    def _load_from_history_file(self, history_file):
        raise NotImplementedError
