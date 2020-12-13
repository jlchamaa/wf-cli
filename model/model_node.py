import uuid
import logging
from model.exceptions import ModelException


log = logging.getLogger("wfcli")


class Node:
    def __init__(self, node_def=None, **kwargs):
        if node_def is None:
            node_def = dict(kwargs)
        self._parent = node_def["pa"]  # mandatory one here
        self._uuid = node_def.get("id", str(uuid.uuid4()))
        self._name = node_def.get("nm", "")
        self._children = node_def.get("ch", [])
        self._closed = node_def.get("cl", False)
        self._complete = node_def.get("cp", False)
        self._cloning = node_def.get("cn", None)
        self._clones = node_def.get("cs", [])

    def __str__(self):
        return "{}: {}\n\tParent: {}\n\tChildren: {}".format(
            self._uuid,
            self._name,
            self._parent,
            self._children,
        )

    def flatify(self, attr):
        if attr is None:
            return None
        if isinstance(attr, Node):
            return attr.uuid
        else:
            return [node.uuid for node in attr]

    def normalize(self, node_store):
        if self._parent is not None:
            self._parent = node_store.get_node(self._parent)
        self._children = [node_store.get_node(node_id) for node_id in self._children]
        if self._cloning is not None:
            self._cloning = node_store.get_node(self._cloning)
        self._clones = [node_store.get_node(node_id) for node_id in self._clones]

    """
    ### Accessor properties
    """

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, x):
        self._parent = x

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, x):
        raise ModelException("Illegal to change the UUID of a node")

    @property
    def name(self):
        if self.is_clone:
            return self.cloning.name
        return self._name

    @name.setter
    def name(self, x):
        if self.is_clone:
            self.cloning.name = x
        self._name = x

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, x):
        self._children = x

    @property
    def closed(self):
        return self._closed

    @closed.setter
    def closed(self, x):
        self._closed = x

    @property
    def complete(self):
        return self._complete

    @complete.setter
    def complete(self, x):
        self._complete = x

    @property
    def cloning(self):
        return self._cloning

    @cloning.setter
    def cloning(self, x):
        self._cloning = x

    @property
    def clones(self):
        return self._clones

    @clones.setter
    def clones(self, x):
        self._clones = x

    """
    ### State Properties
    """

    @property
    def is_clone(self):
        return self._cloning is not None

    @property
    def is_root(self):
        return self._parent is None

    @property
    def state(self):
        if len(self._children) == 0:
            if self._complete:
                return "complete_item"
            else:
                return "item"
        else:
            if self._complete:
                return "complete_parent"
            else:
                return "closed" if self._closed else "open"

    @property
    def flat_format(self):
        return {
            "pa": self.flatify(self._parent),
            "id": self._uuid,
            "nm": self._name,
            "ch": self.flatify(self._children),
            "cl": self._closed,
            "cp": self._complete,
            "cn": self.flatify(self._cloning),
            "cs": self.flatify(self._clones),
        }

    @property
    def digestable_format(self):
        return [
            ("pa", self.flatify(self._parent)),
            ("id", self._uuid),
            ("nm", self._name),
            ("ch", tuple(self.flatify(self._children))),
            ("cl", self._closed),
            ("cp", self._complete),
            ("cn", self.flatify(self._cloning)),
            ("cs", tuple(self.flatify(self._clones))),
        ]

    @property
    def digest(self):
        return hash(frozenset(self.digestable_format))
