#!/usr/bin/env python3.6
import unittest
from unittest.mock import Mock, patch
from model.model_node import Node
from model.node_store import NodeStore

class Test_Node_Store(unittest.TestCase):
    def setUp(self):
        self.nodes = [
            Node(pa="0", id="A"),
            Node(pa="0", id="B"),
            Node(pa="0", id="C"),
        ]
        self.ns = NodeStore()
        for node in self.nodes[0:2]:
            self.ns.add_node(node)

    def test_add_node(self):
        # adding is done by the setup for the sake of the other tests.  
        # But here's where we test the basic sanity of that setUp
        self.assertIs(self.ns.nodes["A"], self.nodes[0])
        self.assertIs(self.ns.nodes["B"], self.nodes[1])

    def test_get_node(self):
        self.assertIs(self.ns.get_node("A"), self.nodes[0])
        self.assertIs(self.ns.get_node("B"), self.nodes[1])
        with self.assertRaises(KeyError):
            self.ns.get_node("C")

    def test_contains(self):
        self.assertTrue("A" in self.ns)
        self.assertTrue("B" in self.ns)
        self.assertFalse("C" in self.ns)

    def test_delete(self):
        self.assertTrue("A" in self.ns)
        del self.ns["A"]
        self.assertFalse("A" in self.ns)

    def test_len(self):
        self.assertEqual(len(self.ns), 2)

    # wait until the node digest is stable
    # def test_digest(self):
    #     self.assertEqual(3381629315008440964, self.ns.digest)


if __name__ == "__main__":
    unittest.main()
