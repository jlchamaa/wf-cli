import logging


log = logging.getLogger("wfcli")


class NodeStore:
    # a shallow wrapper for a dictionary.
    # However, NodeStore implements a digest method
    # these objects get stored in History in their entirety
    def __init__(self):
        self.nodes = {}

    def __eq__(self, other_nds):
        try:
            return self.digest == other_nds.digest
        except Exception:
            return False

    def get_node(self, node_id):
        return self.nodes[node_id]

    def add_node(self, node):
        if node.uuid not in self.nodes:
            self.nodes[node.uuid] = node
        else:
            if self.nodes[node.uuid] is node:
                log.info("Node {} was already in the store".format(node.uuid))
            else:
                raise ValueError("Adding node {} that would overwrite".format(node.uuid))

    def __contains__(self, id):
        return id in self.nodes

    def __delitem__(self, id):
        del self.nodes[id]

    def __len__(self):
        return len(self.nodes)

    def items(self):
        return self.nodes.items()

    @property
    def digest(self):
        iterable = [(key, node.digest) for key, node in self.nodes.items()]
        fs = frozenset(iterable)
        res = hash(fs)
        return res

    @property
    def flat_format(self):
        return [node.flat_format for uuid, node in self.nodes.items()]
