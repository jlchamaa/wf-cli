#!/usr/bin/env python3.6
import unittest
from model.model_node import Node
from model.file_based import ModelException
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


class Test_Integrity(unittest.TestCase):
    def setUp(self):
        test_data = [
            {"id": "0", "ch": ["1", "2"], "pa": None},
            {"id": "1", "ch": ["5"], "pa": "0"},
            {"id": "2", "ch": ["3", "4"], "pa": "0"},
            {"id": "3", "ch": ["7"], "pa": "2", "cs": ["6"]},
            {"id": "4", "ch": [], "pa": "2"},
            {"id": "5", "ch": ["6"], "pa": "1"},
            {"id": "6", "ch": ["8"], "pa": "5", "cn": "3"},
            {"id": "7", "ch": [], "pa": "3", "cs": ["8"]},
            {"id": "8", "ch": [], "pa": "6", "cn": "7"},
        ]
        self.ns = NodeStore()
        self.ns.init_from_flat_object(test_data)

    def test_basic_integrity(self):
        self.assertEqual(None, self.ns.integrity_check())

    def test_missing_child(self):
        self.ns.get_node("0")._children.pop()
        with self.assertRaises(ModelException):
            self.ns.integrity_check()

    def test_additional_child(self):
        node_3 = self.ns.get_node("3")
        self.ns.get_node("0")._children.append(node_3)
        with self.assertRaises(ModelException):
            self.ns.integrity_check()

    def test_wrong_parent(self):
        node_3 = self.ns.get_node("3")
        self.ns.get_node("0").parent = node_3
        with self.assertRaises(ModelException):
            self.ns.integrity_check()

    def test_no_parent(self):
        self.ns.get_node("1").parent = None
        with self.assertRaises(ModelException):
            self.ns.integrity_check()

    def test_missing_clone_child(self):
        node_6 = self.ns.get_node("6")
        self.ns.get_node("3").remove_clone(node_6)
        with self.assertRaises(ModelException):
            self.ns.integrity_check()

    def test_missing_clone_daddy(self):
        self.ns.get_node("6").cloning = None
        with self.assertRaises(ModelException):
            self.ns.integrity_check()

    def test_wrong_clone_children(self):
        self.ns.get_node("8").cloning = None
        with self.assertRaises(ModelException):
            self.ns.integrity_check()

    def test_wrong_clone_children_ii(self):
        self.ns.get_node("6")._children = []
        with self.assertRaises(ModelException):
            self.ns.integrity_check()


if __name__ == "__main__":
    unittest.main()
