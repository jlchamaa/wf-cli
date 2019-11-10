class Node:
    def __init__(self, uuid, name, closed, root=-1):
        self.uuid = uuid
        self.name = name
        self.children = []
        self.closed = closed
        self.root = root  # negatives not root, positives list in order

    def _get_state(self):
        if len(self.children) == 0:
            return "item"
        else:
            return "closed" if self.closed else "open"
