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
        self._load_data()

    def _traverse_node(self, node, depth):
        current_node = self.nodes[node]
        state = current_node._get_state()
        self.visible.append(current_node.uuid)
        if not current_node.closed:
            for child in current_node.children:
                self._traverse_node(child, depth+1)

    def get_children(self, parent_id):
        parent_node = self.nodes[parent_id]
        return [self.nodes[node_id] for node_id in parent_node.children]
        
    def load_visible(self):
        self.visible = []
        for node in self.root_content:
            if node is not None:
                self._traverse_node(node, 0)
        return self.visible


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
            self.data = json.load(f)
            for node in self.data:
                self.nodes[node["id"]] = Node(node["id"], node["nm"], node["cl"], node["rt"])
                if node["rt"] >= 0:
                    self.root_content[node["rt"]] = node["id"]

    def save_data(self):
        pass
