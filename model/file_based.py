#!/usr/bin/env python3
import os
import pickle
import sys
from lazy import lazy
import requests
import json
from model.model_node import Node


class UserFile:
    def __init__(self):
        self.data = self._load_data()
        self.nodes = {}
        [self._traverse_node(node) for node in self.data]

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

    def _load_data(self):
        return [
                {"id": "1",
                 "nm": "Name number 1",
                 "ch":
                    [
                     { "id": "2",
                       "nm": "Name number 2",
                       "ch": []
                     },
                     { "id": "3",
                       "nm": "Name number 3",
                       "ch": []
                     },
                     { "id": "4",
                       "nm": "Name number 4",
                       "ch": []
                     }
                    ]
                 },
                {"id": "5",
                 "nm": "Name number 1",
                 "ch":
                    [
                     { "id": "6",
                       "nm": "Name number 2",
                       "ch": []
                     },
                     { "id": "7",
                       "nm": "Name number 3",
                       "ch": []
                     },
                     { "id": "8",
                       "nm": "Name number 4",
                       "ch": []
                     }
                    ]
                 }
                ]
