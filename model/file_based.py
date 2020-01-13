#!/usr/bin/env python3
import json
import os
import sys
from model.model_node import Node
from model.history import History
from model.node_store import NodeStore


class UserFile:
    DATA_FILE = os.path.expanduser("~/.cache/.wfclidata")
    root_node_id = "0"

    def __init__(self):
        self.nds = NodeStore()
        self.history = History()
        self.cursor_position = 0
        self._load_data()

    @property
    def current_node(self):
        return self.load_visible()[self.cursor_position][0]

    def _traverse_node(self, node, depth):
        current_node = self.nds.get_node(node)
        self.visible.append((current_node, depth))
        if not current_node.closed:
            for child in current_node.children:
                self._traverse_node(child, depth+1)

    def get_children(self, parent_id):
        parent_node = self.nds.get_node(parent_id)
        return [self.nds.get_node(node_id) for node_id in parent_node.children]
        
    def load_visible(self):
        """
        returns a list of tuples like this ( name, depth, state)
        """
        self.visible = []
        for node in self.nds.get_node(self.root_node_id).children:
            if node is not None:
                self._traverse_node(node, 0)
        return self.visible

    def data_from_file_object(self, fo):
        data = json.load(fo)
        for node_def in data:
            node = Node(node_def=node_def)
            self.nds.add_node(node)

    @classmethod
    def _data_file_exists(cls):
        return os.path.exists(cls.DATA_FILE)

    @classmethod
    def _create_empty_data_file(cls):
        os.makedirs(os.path.dirname(cls.DATA_FILE), exist_ok=True)
        with open(cls.DATA_FILE, "x+") as f:
            json.dump([], f)

    def _load_data(self):
        if not self._data_file_exists():
            self._create_empty_data_file()

        with open(self.DATA_FILE) as f:
            self.data_from_file_object(f)

    def save(self):
        pass

    def commit(self):
        self.history.add(self.nds, self.cursor_position)

    def create_node(self, parent, **kwargs):
        node = Node(pa=parent, **kwargs)
        self.nds.add_node(node)
        return node

    def nav_left(self):
        self.visible[self.cursor_position][0].closed = True

    def nav_right(self):
        self.visible[self.cursor_position][0].closed = False

    def nav_up(self):
        if self.cursor_position > 0:
            self.cursor_position -= 1

    def nav_down(self):
        if self.cursor_position < len(self.visible) - 1:
            self.cursor_position += 1

    def unlink_parent_child(self, parent, child):
        assert child in self.nds
        assert parent in self.nds
        assert self.nds.get_node(child).parent == parent
        assert child in self.nds.get_node(parent).children
        self.nds.get_node(parent).children.remove(child)
        self.nds.get_node(child).parent = None

    def link_parent_child(self, parent, child, position=None):
        self.nds.get_node(child).parent = parent
        if position is not None:
            self.nds.get_node(parent).children.insert(position, child)
        else:
            self.nds.get_node(parent).children.append(child)

    def unlink_relink(self, old_parent, child, new_parent, position=None):
        self.unlink_parent_child(old_parent, child)
        self.link_parent_child(new_parent, child, position)

    def indent(self):
        current_node = self.current_node
        parent_node = current_node.parent
        parents_child_list = self.nds.get_node(parent_node).children
        current_node_index = parents_child_list.index(current_node.uuid)
        if current_node_index == 0:
            return "top child"
        else:
            new_parent = parents_child_list[current_node_index - 1]
            self.unlink_relink(parent_node, current_node.uuid, new_parent)
            return "Nailed it"

    def unindent(self):
        current_node = self.current_node
        parent_id = current_node.parent
        if parent_id == self.root_node_id:
            return "top level, no unindent"
        else:
            super_parent_node = self.nds.get_node(self.nds.get_node(parent_id).parent)
            pos_in_parent_list = super_parent_node.children.index(parent_id)
            self.unlink_relink(
                parent_id,
                current_node.uuid,
                super_parent_node.uuid,
                position=pos_in_parent_list+1,
            )
            return "nailed it"

    def open_below(self):
        current_node = self.current_node
        self.cursor_position += 1

        if current_node.state == "open":
            new_node = self.create_node(current_node.uuid)
            self.link_parent_child(
                current_node.uuid,
                new_node.uuid,
                position=0,
            )
            return new_node

        else:  # new node is sibling of current node
            parent_node = self.nds.get_node(current_node.parent)
            new_node = self.create_node(parent_node.uuid)
            pos_in_parent_list = parent_node.children.index(current_node.uuid)
            self.link_parent_child(
                parent_node.uuid,
                new_node.uuid,
                position=pos_in_parent_list+1,
            )
            return new_node

    def complete(self):
        current_node = self.current_node
        current_node.complete = not current_node.complete

    def delete_item(self, node_id=None):
        current_node = self.current_node if node_id is None else self.nds.get_node(node_id)
        for child_id in current_node.children[:]:
            self.delete_item(node_id=child_id)
        parent_id = current_node.parent
        self.nds.get_node(parent_id).children.remove(current_node.uuid)
        del self.nds[current_node.uuid]
        if node_id is None:  # this is our top-level delete
            self.cursor_position = max(0, self.cursor_position-1)
            if len(self.nds.get_node(self.root_node_id).children) == 0:
                new_node = self.create_node(
                    self.root_node_id,
                    nm="Ooops, you deleted the last item on the list",
                )
                self.link_parent_child(
                    self.root_node_id,
                    new_node.uuid,
                    position=0,
                )
