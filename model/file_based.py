#!/usr/bin/env python3
import os
import pickle
import sys
from lazy import lazy
import requests
import json
from model.model_node import Node


class UserFile:
    DATA_FILE = os.path.expanduser("~/.cache/.wfclidata")
    root_node_id = "0"

    def __init__(self):
        self.nodes = {}
        self.cursor_position = 0
        self._load_data()

    def _traverse_node(self, node, depth):
        current_node = self.nodes[node]
        self.visible.append((current_node, depth))
        if not current_node.closed:
            for child in current_node.children:
                self._traverse_node(child, depth+1)

    def get_children(self, parent_id):
        parent_node = self.nodes[parent_id]
        return [self.nodes[node_id] for node_id in parent_node.children]
        
    def load_visible(self):
        """
        returns a list of tuples like this ( name, depth, state)
        """
        self.visible = []
        for node in self.nodes[self.root_node_id].children:
            if node is not None:
                self._traverse_node(node, 0)
        return self.visible

    def data_from_file_object(self, fo):
        data = json.load(fo)
        for node_dict in data:
            node = Node(node_dict)
            self.nodes[node.uuid] = node

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

    def save_data(self):
        pass

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
        assert child in self.nodes
        assert parent in self.nodes
        assert self.nodes[child].parent == parent
        assert child in self.nodes[parent].children
        self.nodes[parent].children.remove(child)
        self.nodes[child].parent = None

    def link_parent_child(self, parent, child):
        self.nodes[child].parent = parent
        self.nodes[parent].children.append(child)

    def unlink_relink(self, old_parent, child, new_parent):
        self.unlink_parent_child(old_parent, child)
        self.link_parent_child(new_parent, child)

    def indent(self):
        current_node, current_depth = self.visible[self.cursor_position]
        parent_node = current_node.parent
        parents_child_list = self.nodes[parent_node].children
        current_node_index = parents_child_list.index(current_node.uuid)
        if current_node_index == 0:
            return "top child"
        else:
            new_parent = parents_child_list[current_node_index - 1]
            self.unlink_relink(parent_node, current_node.uuid, new_parent)
            return "Nailed it"

    def unindent(self):
        current_node, current_depth = self.visible[self.cursor_position]
        parent_id = current_node.parent
        if parent_id == self.root_node_id:
            return "top level, no unindent"
        else:
            super_parent_id = self.nodes[parent_id].parent
            self.unlink_relink(parent_id, current_node.uuid, super_parent_id)
