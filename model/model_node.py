class Node:
    def __init__(self, uuid, name, parent=0):
        self.uuid = uuid
        self.name = name
        self.parent = parent
        self.children = []
