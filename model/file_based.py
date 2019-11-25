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

    def __init__(self):
        self.nodes = {}
        self.root_content = [None] * 50
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
        for node in self.root_content:
            if node is not None:
                self._traverse_node(node, 0)
        return self.visible

    def data_from_file_object(self, fo):
        data = json.load(fo)
        for node_dict in data:
            node = Node(node_dict)
            self.nodes[node.uuid] = node
            if node.is_root:
                self.root_content[node.parent] = node.uuid

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
        if self.nodes[child].is_root:
            # parent is root, just remove from list
            self.root_content.remove(child)
        else:
            #parent is a node, more work/verification is needed
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
        if self.cursor_position > 0:
            # we have a neighbor above us
            current_node, current_depth = self.visible[self.cursor_position]
            neighbor_node, neighbor_depth = self.visible[self.cursor_position - 1]
            if neighbor_depth == current_depth -1:  # above neighbor should be parent
                assert current_node.uuid in neighbor_node.children
                return "Cannot Indent"
            if neighbor_depth == current_depth:  # above neighbor should be peer
                self.unlink_relink(current_node.parent, current_node.uuid, neighbor_node.uuid) 
                return "Can Indent"
        else:
            #nobody above to compare with. Error
            return "cursor 0"

    def unindent(self):
        pass
