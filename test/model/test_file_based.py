#!/usr/bin/env python3.6
import unittest
import unittest.mock as mock

from model.file_based import UserFile
from model.model_node import Node
from model.node_store import NodeStore


class Test_UserFile(unittest.TestCase):
    @mock.patch("model.file_based.UserFile._load_data")
    def setUp(self, mocked_load_data):
        self.uf = UserFile()
        mocked_load_data.assert_called_once()
        self.assertEqual(0, len(self.uf.nds))
        test_data = [
            {"id": "0", "nm": "root", "cl": False, "ch": ["1", "2"], "pa": None},
            {"id": "1", "nm": "henlo", "cl": False, "ch": [], "pa": "0"},
            {"id": "2", "nm": "goodbye", "cl": False, "ch": ["3", "4"], "pa": "0"},
            {"id": "3", "nm": "sayonara", "cl": False, "ch": [], "pa": "2"},
            {"id": "4", "nm": "nice", "cl": False, "ch": [], "pa": "2"}
        ]
        nds = NodeStore()
        for node_def in test_data:
            nds.add_node(Node(node_def))
        self.uf.nds = nds
        self.assertEqual(5, len(self.uf.nds))

    def test_current_node(self):
        self.assertEqual(self.uf.current_node().uuid, "1")

    def test_traverse_small(self):
        self.uf._visible = []
        self.uf._traverse_node("2", 0)
        self.assertEqual(len(self.uf._visible), 3)

    def test_traverse_single(self):
        self.uf._visible = []
        self.uf._traverse_node("4", 0)
        self.assertEqual(len(self.uf._visible), 1)

    def test_create_node(self):
        node = self.uf.create_node("parent")
        self.assertIs(node, self.uf.nds.get_node(node.uuid))

    def test_close_open_item(self):
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 4)
        self.uf.cursor_y = 1
        self.uf.collapse_node()
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 2)

    def test_close_open_compound_item(self):
        self.uf.nds.add_node(Node({"id": "5", "nm": "fifth", "pa": "4"}))
        self.uf.nds.get_node("4").children.append("5")
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 5)
        self.uf.cursor_y = 1
        self.uf.collapse_node()
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 2)

    def test_close_closed_item(self):
        self.uf.nds.get_node("2").closed = True
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 2)
        self.uf.cursor_y = 1
        self.uf.collapse_node()
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 2)

    def test_close_leaf_item(self):
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 4)
        self.uf.cursor_y = 0
        self.uf.collapse_node()
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 4)

    def test_open_closed_item(self):
        self.uf.nds.get_node("2").closed = True
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 2)
        self.uf.cursor_y = 1
        self.uf.expand_node()
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 4)

    def test_open_open_item(self):
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 4)
        self.assertFalse(self.uf.nds.get_node("2").closed)
        self.uf.cursor_y = 1
        self.uf.expand_node()
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 4)

    def test_open_compound_closed_open_item(self):
        # cursor is closed, but children are open
        self.uf.nds.add_node(Node({"id": "5", "nm": "fifth", "pa": "4"}))
        self.uf.nds.get_node("4").children.append("5")
        self.uf.nds.get_node("2").closed = True
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 2)
        self.uf.cursor_y = 1
        self.uf.expand_node()
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 5)

    def test_open_compound_closed_closed_item(self):
        # cursor is closed, but children are also closed
        # should only open up the main, not the children
        self.uf.nds.add_node(Node({"id": "5", "nm": "fifth", "pa": "4"}))
        self.uf.nds.get_node("4").children.append("5")
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 5)
        self.uf.nds.get_node("2").closed = True
        self.uf.nds.get_node("4").closed = True
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 2)
        self.uf.cursor_y = 1
        self.uf.expand_node()
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 4)

    def test_open_compound_closed_item(self):
        # cursor is closed, but children are open
        self.uf.nds.add_node(Node({"id": "5", "nm": "fifth", "pa": "4"}))
        self.uf.nds.get_node("4").children.append("5")
        self.uf.nds.get_node("2").closed = True
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 2)
        self.uf.cursor_y = 1
        self.uf.expand_node()
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 5)

    def test_open_leaf_item(self):
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 4)
        self.uf.cursor_y = 0
        self.uf.expand_node()
        self.uf.load_visible()
        self.assertEqual(len(self.uf.visible), 4)

    def test_indent(self):
        pass


if __name__ == "__main__":
    unittest.main()
