import uuid
class Node:
    def __init__(self, node_def=None, **kwargs):
        if node_def is None:
            node_def = dict(kwargs)
        self.parent = node_def["pa"]  # mandatory one here
        self.uuid = node_def.get("id", uuid.uuid4())
        self.name = node_def.get("nm", "")
        self.children = node_def.get("ch", [])
        self.closed = node_def.get("cl", False)
        self.complete = node_def.get("cp", False)

        if "parent" not in self.__dict__ or self.parent is False:
            raise ValueError("Parent needs to be set during instantiation")
        if "uuid" not in self.__dict__ or self.parent is False:
            raise ValueError("UUID needs to be set during instantiation")


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
