import logging


log = logging.getLogger("wfcli")


class NodeStore:
    # a shallow wrapper for a dictionary.
    # However, NodeStore implements a digest method
    # these objects get stored in History in their entirety
    def __init__(self):
        self.nodes = {}

    def __eq__(self, other_nds):
        return self.digest == other_nds.digest

    def get_node(self, node_id):
        return self.nodes[node_id]

    def add_node(self, node):
        self.nodes[node.uuid] = node

    def __contains__(self, id):
        return id in self.nodes

    def __delitem__(self, id):
        del self.nodes[id]

    def __len__(self):
        return len(self.nodes)

    @property
    def digest(self):
        iterable = [(key, node.digest) for key, node in self.nodes.items()]
        fs = frozenset(iterable)
        res = hash(fs)
        return res

    @property
    def flat_format(self):
        return [node.flat_format for uuid, node in self.nodes.items()]
