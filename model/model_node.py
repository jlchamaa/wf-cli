import uuid
import logging
from model.exceptions import ModelException
from collections import namedtuple
log = logging.getLogger("wfcli")

attribute = namedtuple("attribute", ["name", "shorthand", "default", "flatten"])
all_attributes = [
    attribute("_parent", "pa", lambda: None, lambda x: x),
    attribute("_uuid", "id", lambda: str(uuid.uuid4()), lambda x: x),
    attribute("_name", "nm", lambda: "", lambda x: x),
    attribute("_children", "ch", list, lambda x: x),
    attribute("_closed", "cl", lambda: False, lambda x: x),
    attribute("_complete", "cp", lambda: False, lambda x: x),
    attribute("_cloning", "cn", lambda: None, lambda x: x),
    attribute("_clones", "cs", list, lambda x: x),
]


def flatify(attr):
    if attr is None:
        return None
    if isinstance(attr, Node):
        return attr.uuid
    else:
        return [node.uuid for node in attr]


class Node:
    def __init__(self, node_def=None, **kwargs):
        if node_def is None:
            node_def = dict(kwargs)
        if "pa" not in node_def:
            raise KeyError  # gotta have a parent explicitly defined
        for attribute in all_attributes:
            setattr(
                self,
                attribute.name,
                node_def.get(attribute.shorthand, attribute.default()),
            )

    def __repr__(self):
        return self._uuid

    def __str__(self):
        return "\t{}: {}\tParent: {}\tChildren: {}".format(
            self._uuid,
            self._name,
            self._parent.uuid if self._parent is not None else None,
            [c.uuid for c in self._children],
        )

    def normalize(self, node_store):
        if self._parent is not None:
            self._parent = node_store.get_node(self._parent)
        self._children = [node_store.get_node(node_id) for node_id in self._children]
        if self._cloning is not None:
            self._cloning = node_store.get_node(self._cloning)
        self._clones = [node_store.get_node(node_id) for node_id in self._clones]

    """
    ### Mutator methods
    """

    def add_child(self, node, position=None):
        if position is None:
            self._children.append(node)
        else:
            self._children.insert(position, node)

    def remove_child(self, node):
        self._children.remove(node)

    def add_clone(self, node, position=None):
        if position is None:
            self._clones.append(node)
        else:
            self._clones.insert(position, node)

    def remove_clone(self, node):
        self._clones.remove(node)

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
        """
        returning a tuple enforces that nobody is altering our children
        without our consent.
        """
        return tuple(self._children)

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
        """
        returning a tuple enforces that nobody is altering our clones
        without our consent.
        """
        return tuple(self._clones)

    @clones.setter
    def clones(self, x):
        self._clones = x

    """
    ### State Properties
    """

    def is_ancestor(self, node):
        if node is self:
            return True
        if self.parent is None:
            return False
        return self.parent.is_ancestor(node)

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
            "pa": flatify(self._parent),
            "id": self._uuid,
            "nm": self._name,
            "ch": flatify(self._children),
            "cl": self._closed,
            "cp": self._complete,
            "cn": flatify(self._cloning),
            "cs": flatify(self._clones),
        }

    @property
    def digestable_format(self):
        return [
            ("pa", flatify(self._parent)),
            ("id", self._uuid),
            ("nm", self._name),
            ("ch", tuple(flatify(self._children))),
            ("cl", self._closed),
            ("cp", self._complete),
            ("cn", flatify(self._cloning)),
            ("cs", tuple(flatify(self._clones))),
        ]

    @property
    def digest(self):
        return hash(frozenset(self.digestable_format))
