class NodeStore:
    # a shallow wrapper for a dictionary.
    # However, NodeStore implements a digest method
    # these objects get stored in History in their entirety
    def __init__(self):
        self.nodes = {}

    def get_node(self, node_id):
        return self.nodes[node_id]

    def add_node(self, node):
        self.nodes[node.uuid] = node

    def __contains__(self, item):
        return item in self.nodes
    
    def __delitem__(self, item):
        del self.nodes[item]

    def digest(self):
        return "123"
