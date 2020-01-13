#!/usr/bin/env python3.6
import unittest
from unittest.mock import Mock, patch
from model.model_node import Node


class Test_Node(unittest.TestCase):
    def test_node_def(self):
        node = Node(node_def={"pa": "parent", "id": "id", "nm": "name", "ch": "child", "cl": "closed", "cp": "complete"})
        self.assertEqual(node.parent, "parent")
        self.assertEqual(node.uuid, "id")
        self.assertEqual(node.name, "name")
        self.assertEqual(node.children, "child")
        self.assertEqual(node.closed, "closed")
        self.assertEqual(node.complete, "complete")

    def test_node_def_with_bad_overrides(self):
        node = Node(node_def={"pa": "parent", "id": "id", "nm": "name", "ch": "child", "cl": "closed", "cp": "complete"},
                    pa="parent2",
                    id="id2",
                    nm="name2",
                    ch="child2",
                    cl="closed2",
                    cp="complete2",
        )
        # overrides don't do anything if node_def is defined
        self.assertEqual(node.parent, "parent")
        self.assertEqual(node.uuid, "id")
        self.assertEqual(node.name, "name")
        self.assertEqual(node.children, "child")
        self.assertEqual(node.closed, "closed")
        self.assertEqual(node.complete, "complete")

    def test_node_def_with_good_overrides(self):
        node = Node(pa="parent",
                    id="id",
                    nm="name",
                    ch="child",
                    cl="closed",
                    cp="complete",
        )
        # overrides don't do anything if node_def is defined
        self.assertEqual(node.parent, "parent")
        self.assertEqual(node.uuid, "id")
        self.assertEqual(node.name, "name")
        self.assertEqual(node.children, "child")
        self.assertEqual(node.closed, "closed")
        self.assertEqual(node.complete, "complete")

    def test_node_def_needs_parent(self):
        with self.assertRaises(KeyError):
            node = Node(node_def={"id": "id", "nm": "name", "ch": "child", "cl": "closed", "cp": "complete"})

    def test_node_kwargs_need_parent(self):
        with self.assertRaises(KeyError):
            node = Node(id="id",
                        nm="name",
                        ch="child",
                        cl="closed",
                        cp="complete",
            )

    @patch("model.model_node.uuid.uuid4")
    def test_node_defaults(self, mocked_uuid):
        mocked_uuid.return_value = "fake_uuid"
        node = Node(pa="1")
        self.assertEqual(node.parent, "1")
        self.assertEqual(node.uuid, "fake_uuid")
        self.assertEqual(node.name, "")
        self.assertEqual(node.children, [])
        self.assertEqual(node.closed, False)
        self.assertEqual(node.complete, False)

    def test_state_item(self):
        node = Node(pa="1")
        self.assertEqual(node.state, "item")
        node.closed = True
        self.assertEqual(node.state, "item")

    def test_state_open_closed(self):
        node = Node(pa="1", ch=["0"])
        self.assertEqual(node.state, "open")
        node.closed = True
        self.assertEqual(node.state, "closed")



if __name__ == "__main__":
    unittest.main()
