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
        self._load_data()

    def _traverse_node(self, node, parent=0):
        this_node = Node(node['id'], node['nm'], parent)
        if 'ch' in node:
            for child in node['ch']:
                self._traverse_node(child, node['id'])
                this_node.children.append(child['id'])
        self.nodes[node['id']] = this_node

    def get_children(self, parent_id):
        parent_node = self.nodes[parent_id]
        return [self.nodes[node_id] for node_id in parent_node.children]
        
    def get_root_content(self):
        return [(node["nm"],node['id']) for node in self.data]

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
            self._traverse_node(node)

    def save_data(self):
        pass
