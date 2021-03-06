#!/usr/bin/env python3
import json
import logging
import os
from model.model_node import Node
from model.history import History
from model.node_store import NodeStore

log = logging.getLogger("wfcli")


class ModelException(Exception):
    pass


class UserFile:
    DATA_FILE = os.path.expanduser("~/.cache/.wfclidata")
    root_node_id = "0"

    # SETUP METHODS
    def __init__(self):
        self.nds = NodeStore()
        self.cursor_y = 0
        self._load_data()
        self._update = True
        self.history = History(seed=self.nds)

    # Decorator for funtions that need to force an update to our tree
    def update_visible_after(func):
        def do_update(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self._update = True
            return result
        return do_update

    def update_visible_now(self):
        self._update = True

    def set_cursor_to_node(self, node_id):
        self.update_visible_now()
        for i, v in enumerate(self.visible):
            if v[0].uuid == node_id:
                self.cursor_y = i

    def current_node(self, depth=False):
        node_pair = self.visible[self.cursor_y]
        if depth:
            return node_pair
        else:
            return node_pair[0]

    # FILE METHODS
    def data_from_file_object(self, fo):
        data = json.load(fo)
        for node_def in data:
            node = Node(node_def=node_def)
            self.nds.add_node(node)

    @classmethod
    def _write_data_file(cls, data_obj):
        os.makedirs(os.path.dirname(cls.DATA_FILE), exist_ok=True)
        with open(cls.DATA_FILE, "x+") as f:
            json.dump(data_obj, f, indent=2)

    @classmethod
    def _create_empty_data_file(cls):
        empty_data = [
            {"id": cls.root_node_id, "pa": None, "ch": ["1"]},
            {"pa": cls.root_node_id, "id": "1", "nm": "Write down your thoughts"},
        ]
        cls._write_data_file(empty_data)

    def _load_data(self):
        if not os.path.exists(self.DATA_FILE):
            self._create_empty_data_file()

        with open(self.DATA_FILE) as f:
            self.data_from_file_object(f)

    def save(self):
        with open(self.DATA_FILE, "w") as f:
            json.dump(self.nds.flat_format, f, indent=2)

    def commit(self):
        self.history.add(self.nds)

    # TREE TRAVERSAL
    @property
    def visible(self):
        if self._update:
            self._update = False
            return self.load_visible()
        else:
            return self._visible

    def load_visible(self):
        """
        returns a list of tuples like this ( node, depth,)
        """
        self._visible = []
        for node in self.nds.get_node(self.root_node_id).children:
            if node is not None:
                self._traverse_node(node, 0)
        return self._visible

    def _traverse_node(self, node, depth):
        current_node = self.nds.get_node(node)
        self._visible.append((current_node, depth))
        if not current_node.closed:
            for child in current_node.children:
                self._traverse_node(child, depth + 1)

    # NAVIGATION METHODS
    def nav_up(self):
        if self.cursor_y > 0:
            self.cursor_y -= 1

    def nav_down(self):
        if self.cursor_y < len(self.visible) - 1:
            self.cursor_y += 1

    def bottom(self):
        self.cursor_y = len(self.visible) - 1

    def top(self):
        self.cursor_y = 0

    # LINKING METHODS
    @update_visible_after
    def link_parent_child(self, parent, child, position=-1):
        self.nds.get_node(child).parent = parent
        if position >= 0:
            self.nds.get_node(parent).children.insert(position, child)
        else:
            self.nds.get_node(parent).children.append(child)

    @update_visible_after
    def unlink_relink(self, old_parent, child, new_parent, position):
        def unlink_parent_child(self, parent, child):
            assert child in self.nds
            assert parent in self.nds
            assert self.nds.get_node(child).parent == parent
            assert child in self.nds.get_node(parent).children
            self.nds.get_node(parent).children.remove(child)
            self.nds.get_node(child).parent = None
        unlink_parent_child(self, old_parent, child)
        self.link_parent_child(new_parent, child, position)

    # MANIPULATE NODES
    @update_visible_after
    def indent(self):
        current_node = self.current_node()
        parent_node = current_node.parent
        parents_child_list = self.nds.get_node(parent_node).children
        current_node_index = parents_child_list.index(current_node.uuid)
        if current_node_index == 0:
            raise ModelException("Indent of top child")
        else:
            new_parent = parents_child_list[current_node_index - 1]
            self.unlink_relink(parent_node, current_node.uuid, new_parent, -1)
            self.nds.get_node(new_parent).closed = False
            log.info("Nailed it")

    @update_visible_after
    def unindent(self):
        current_node = self.current_node()
        parent_id = current_node.parent
        if parent_id == self.root_node_id:
            raise ModelException("top level, can't unindent")
        else:
            super_parent_node = self.nds.get_node(self.nds.get_node(parent_id).parent)
            pos_in_parent_list = super_parent_node.children.index(parent_id)
            self.unlink_relink(
                parent_id,
                current_node.uuid,
                super_parent_node.uuid,
                pos_in_parent_list + 1,
            )
            log.info("nailed it")

    @update_visible_after
    def open_above(self):
        current_node = self.current_node()
        parent_node = self.nds.get_node(current_node.parent)
        new_node = self.create_node(parent_node.uuid)
        pos_in_parent_list = parent_node.children.index(current_node.uuid)
        self.link_parent_child(
            parent_node.uuid,
            new_node.uuid,
            pos_in_parent_list,
        )

    @update_visible_after
    def open_below(self):
        current_node = self.current_node()
        if current_node.state == "open":
            new_node = self.create_node(current_node.uuid)
            self.link_parent_child(
                current_node.uuid,
                new_node.uuid,
                0,
            )
        else:  # new node is sibling of current node
            parent_node = self.nds.get_node(current_node.parent)
            new_node = self.create_node(parent_node.uuid)
            pos_in_parent_list = parent_node.children.index(current_node.uuid)
            self.link_parent_child(
                parent_node.uuid,
                new_node.uuid,
                pos_in_parent_list + 1,
            )

    @update_visible_after
    def delete_item(self, node_id=None):
        current_node = self.current_node() if node_id is None else self.nds.get_node(node_id)
        for child_id in current_node.children[:]:
            self.delete_item(node_id=child_id)
        parent_id = current_node.parent
        self.nds.get_node(parent_id).children.remove(current_node.uuid)
        del self.nds[current_node.uuid]
        if node_id is None:  # this is our top-level delete
            self.cursor_y = max(0, self.cursor_y - 1)
            if len(self.nds.get_node(self.root_node_id).children) == 0:
                new_node = self.create_node(
                    self.root_node_id,
                    nm="Ooops, you deleted the last item on the list",
                )
                self.link_parent_child(
                    self.root_node_id,
                    new_node.uuid,
                    0,
                )

    @update_visible_after
    def move_down(self):
        current_node = self.current_node()
        parent_id = current_node.parent
        parents_child_list = self.nds.get_node(parent_id).children
        current_node_index = parents_child_list.index(current_node.uuid)
        if current_node_index < len(parents_child_list) - 1:
            # swap with the one behind
            parents_child_list[current_node_index] = parents_child_list[current_node_index + 1]
            parents_child_list[current_node_index + 1] = current_node.uuid
            self.set_cursor_to_node(current_node.uuid)

    @update_visible_after
    def move_up(self):
        current_node = self.current_node()
        parent_id = current_node.parent
        parents_child_list = self.nds.get_node(parent_id).children
        current_node_index = parents_child_list.index(current_node.uuid)
        if current_node_index > 0:
            # swap with the one behind
            parents_child_list[current_node_index] = parents_child_list[current_node_index - 1]
            parents_child_list[current_node_index - 1] = current_node.uuid
            self.set_cursor_to_node(current_node.uuid)

    @update_visible_after
    def complete(self):
        current_node = self.current_node()
        current_node.complete = not current_node.complete

    @update_visible_after
    def create_node(self, parent, **kwargs):
        node = Node(pa=parent, **kwargs)
        self.nds.add_node(node)
        return node

    @update_visible_after
    def collapse_node(self):
        self.visible[self.cursor_y][0].closed = True

    @update_visible_after
    def expand_node(self):
        self.visible[self.cursor_y][0].closed = False

    @update_visible_after
    def undo(self):
        ret = self.history.undo()
        if ret is not None:
            self.nds = ret

    @update_visible_after
    def redo(self):
        ret = self.history.redo()
        if ret is not None:
            self.nds = ret

    # EDIT TEXT
    @update_visible_after
    def add_char(self, char, cursor_x):
        current_node = self.current_node()
        name = current_node.name[0:cursor_x] + char + current_node.name[cursor_x:]
        current_node.name = name

    @update_visible_after
    def delete_char(self, num, cursor_x):
        current_node = self.current_node()
        if cursor_x > 0:
            name = current_node.name[0:cursor_x - num] + current_node.name[cursor_x:]
            current_node.name = name
