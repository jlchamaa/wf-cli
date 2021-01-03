import logging
from model.model_node import Node


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

    def init_from_flat_object(self, flat_obj):
        for node_def in flat_obj:
            node = Node(node_def=node_def)
            self.add_node(node)
        for node_id, node_data in self.items():
            node_data.normalize(self)

    def integrity_check(self):
        for node_id, node in self.items():
            # check my parent
            if node.parent is not None:
                if node not in node.parent.children:
                    log.error("{} fails. Not present in its parent's children".format(node.uuid))
                    return False

            # check my children
            for child in node.children:
                if child.parent is not node:
                    log.error("{} fails. Child {} doesn't have as parent".format(node.uuid, child.uuid))
                    return False

            # check my basic cloning
            if node.cloning is not None:
                if node not in node.cloning.clones:
                    log.error("{} fails. Not present in its cloning's clones".format(node.uuid))
                    return False

            # and the reverse
            for clone in node.clones:
                if clone.cloning is not node:
                    log.error("{} fails. Clone {} doesn't have node as clone daddy".format(node.uuid, clone.uuid))
                    return False

            # clone nesting
            if node.cloning is not None:
                children_of_what_i_clone = [n.uuid for n in node.cloning.children]
                what_my_children_clone = [n.cloning.uuid for n in node.children if n.cloning is not None]
                if children_of_what_i_clone != what_my_children_clone:
                    log.error("{} fails. Children don't match up".format(node.uuid))
        return True
