class Node:
    def __init__(self, node_dict):
        self.from_dictionary(node_dict)

    def from_dictionary(self, node_dict):
        self.uuid = node_dict["id"]
        self.name = node_dict["nm"]
        self.parent = node_dict["pa"]
        self.children = node_dict["ch"]
        self.closed = node_dict["cl"]

    def __str__(self):
        return "{}: {}\n\tParent: {}\n\tChildren: {}".format(
            self.uuid,
            self.name,
            self.parent,
            self.children,
        )

    @property
    def is_root(self):
        return self.parent is None

    @property
    def state(self):
        if len(self.children) == 0:
            return "item"
        else:
            return "closed" if self.closed else "open"
