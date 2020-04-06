import hashlib
import uuid
import logging


log = logging.getLogger("wfcli")


class Node:
    def __init__(self, node_def=None, **kwargs):
        if node_def is None:
            node_def = dict(kwargs)
        self.parent = node_def["pa"]  # mandatory one here
        self.uuid = node_def.get("id", str(uuid.uuid4()))
        self.name = node_def.get("nm", "")
        self.children = node_def.get("ch", [])
        self.closed = node_def.get("cl", False)
        self.complete = node_def.get("cp", False)

    def __str__(self):
        return "{}: {}\n\tParent: {}\n\tChildren: {}".format(
            self.uuid,
            self.name,
            self.parent,
            self.children,
        )

    @property
    def flat_format(self):
        return {
            "pa": self.parent,
            "id": self.uuid,
            "nm": self.name,
            "ch": self.children,
            "cl": self.closed,
            "cp": self.complete,
        }

    @property
    def digestable_format(self):
        return [
            ("pa", self.parent),
            ("id", self.uuid),
            ("nm", self.name),
            ("ch", tuple(self.children)),
            ("cl", self.closed),
            ("cp", self.complete),
        ]

    @property
    def digest(self):
        return hash(frozenset(self.digestable_format))

    @property
    def is_root(self):
        return self.parent is None

    @property
    def state(self):
        if len(self.children) == 0:
            if self.complete:
                return "complete_item"
            else:
                return "item"
        else:
            if self.complete:
                return "complete_parent"
            else:
                return "closed" if self.closed else "open"
