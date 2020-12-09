#!/usr/bin/env python3.6
import unittest
from unittest.mock import patch, Mock, ANY

from model.file_based import UserFile, ModelException
from model.model_node import Node
from model.node_store import NodeStore


class Test_UserFile(unittest.TestCase):
    @patch("model.file_based.UserFile._load_data")
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

    def test_bottom(self):
        self.uf.cursor_y = 0
        self.uf.bottom()
        self.assertEqual(self.uf.cursor_y, 3)

    def test_top(self):
        self.uf.cursor_y = 2
        self.uf.top()
        self.assertEqual(self.uf.cursor_y, 0)

    def test_data_from_fo(self):
        fo = Mock()
        self.assertEqual(len(self.uf.nds), 5)
        fo.read.return_value = '''[{"pa": "4"}]'''
        self.uf.data_from_file_object(fo)
        self.assertEqual(len(self.uf.nds), 6)

    def test_cursor_to_node(self):
        self.assertEqual(self.uf.cursor_y, 0)
        self.uf.set_cursor_to_node("3")
        self.assertEqual(self.uf.cursor_y, 2)

    def test_link_parent_child_particular_position(self):
        self.assertEqual(len(self.uf.visible), 4)
        found_children = self.uf.nds.get_node("0").children
        self.assertEqual(found_children, ["1", "2"])
        self.uf.link_parent_child("0", "2", 0)
        self.assertEqual(len(self.uf.visible), 7)
        found_children = self.uf.nds.get_node("0").children
        self.assertEqual(found_children, ["2", "1", "2"])

    def test_link_parent_child_no_position(self):
        self.assertEqual(len(self.uf.visible), 4)
        found_children = self.uf.nds.get_node("0").children
        self.assertEqual(found_children, ["1", "2"])
        self.uf.link_parent_child("0", "3")
        self.assertEqual(len(self.uf.visible), 5)
        found_children = self.uf.nds.get_node("0").children
        self.assertEqual(found_children, ["1", "2", "3"])

    def test_unlink_relink(self):
        self.uf.unlink_relink("2", "3", "0", 0)
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["3", "1", "2"],
        )

    def test_indent_top_sibling(self):
        self.uf.set_cursor_to_node("1")
        with self.assertRaises(ModelException):
            self.uf.indent()
        # Should not have changed anything
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["1", "2"],
        )

    def test_indent_second_sibling(self):
        self.uf.set_cursor_to_node("2")
        self.uf.indent()
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["1"],
        )
        self.assertEqual(
            self.uf.nds.get_node("1").children,
            ["2"],
        )

    def test_unindent_not_top(self):
        self.uf.set_cursor_to_node("3")
        self.uf.unindent()
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["1", "2", "3"],
        )
        self.assertEqual(
            self.uf.nds.get_node("2").children,
            ["4"],
        )

    def test_unindent_top(self):
        self.uf.set_cursor_to_node("2")
        with self.assertRaises(ModelException):
            self.uf.unindent()
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["1", "2"],
        )
        self.assertEqual(
            self.uf.nds.get_node("2").children,
            ["3", "4"],
        )

    def test_open_below_open(self):
        self.uf.set_cursor_to_node("2")
        self.uf.open_below()
        n2s_children = self.uf.nds.get_node("2").children
        self.assertEqual(len(n2s_children), 3)
        self.assertEqual(n2s_children[1:], ["3", "4"])

    def test_open_below_item(self):
        self.uf.open_below()
        root_children = self.uf.nds.get_node("0").children
        self.assertEqual(len(root_children), 3)
        self.assertEqual(root_children[0], "1")
        self.assertEqual(root_children[2], "2")

    def test_delete_single_item_from_cursor(self):
        self.uf.delete_item()
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["2"],
        )
        self.assertNotIn("1", self.uf.nds)

    def test_delete_single_item_from_id(self):
        self.uf.delete_item("1")
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["2"],
        )
        self.assertNotIn("1", self.uf.nds)

    def test_delete_nested_item_from_cursor(self):
        self.uf.set_cursor_to_node("2")
        self.uf.delete_item()
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["1"],
        )
        self.assertNotIn("2", self.uf.nds)
        self.assertNotIn("3", self.uf.nds)
        self.assertNotIn("4", self.uf.nds)
        self.assertEqual(len(self.uf.nds), 2)  # includes root

    def test_delete_nested_item_from_id(self):
        self.uf.delete_item("2")
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["1"],
        )
        self.assertNotIn("2", self.uf.nds)
        self.assertNotIn("3", self.uf.nds)
        self.assertNotIn("4", self.uf.nds)
        self.assertEqual(len(self.uf.nds), 2)  # includes root

    def test_delete_it_all(self):
        self.uf.delete_item("2")
        self.assertEqual(len(self.uf.nds), 2)  # includes root
        self.uf.delete_item()
        self.assertEqual(len(self.uf.nds), 2)  # includes root+new

    def test_move_down(self):
        self.uf.move_down()
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["2", "1"],
        )
        self.assertEqual(self.uf.cursor_y, 3)
        self.uf.move_down()  # should no-op
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["2", "1"],
        )

    def test_move_up(self):
        self.uf.move_up()  # should no-op
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["1", "2"],
        )
        self.uf.set_cursor_to_node("2")
        self.uf.move_up()
        self.assertEqual(
            self.uf.nds.get_node("0").children,
            ["2", "1"],
        )

    def test_complete(self):
        node_1 = self.uf.nds.get_node("1")
        self.assertEqual(node_1.complete, False)
        self.uf.complete()
        self.assertEqual(node_1.complete, True)
        self.uf.complete()
        self.assertEqual(node_1.complete, False)

    def test_undo(self):
        mock_history = Mock()
        mock_history.undo.return_value = None
        self.uf.history = mock_history
        self.uf.undo()
        self.assertIsNotNone(self.uf.nds)
        mock_history.undo.return_value = "fake_result"
        self.uf.undo()
        self.assertEqual(self.uf.nds, "fake_result")

    def test_redo(self):
        mock_history = Mock()
        mock_history.redo.return_value = None
        self.uf.history = mock_history
        self.uf.redo()
        self.assertIsNotNone(self.uf.nds)
        mock_history.redo.return_value = "fake_result"
        self.uf.redo()
        self.assertEqual(self.uf.nds, "fake_result")

    @patch("model.file_based.UserFile.data_from_file_object")
    @patch("model.file_based.open")
    @patch("model.file_based.UserFile._create_empty_data_file")
    @patch("model.file_based.os.path.exists")
    def test_load_data_exists(self, mock_exists, mock_create_empty, mock_open, mock_data_from_fo):
        mock_exists.return_value = True
        self.uf._load_data()
        mock_create_empty.assert_not_called()
        mock_exists.assert_called_once_with(self.uf.DATA_FILE)
        mock_open.assert_called_once_with(self.uf.DATA_FILE)
        mock_data_from_fo.assert_called_once_with(mock_open.return_value.__enter__.return_value)

    @patch("model.file_based.UserFile.data_from_file_object")
    @patch("model.file_based.open")
    @patch("model.file_based.UserFile._create_empty_data_file")
    @patch("model.file_based.os.path.exists")
    def test_load_data_doesnt_exist(self, mock_exists, mock_create_empty, mock_open, mock_data_from_fo):
        mock_exists.return_value = False
        self.uf._load_data()
        mock_create_empty.assert_called_once_with()
        mock_exists.assert_called_once_with(self.uf.DATA_FILE)
        mock_open.assert_called_once_with(self.uf.DATA_FILE)
        mock_data_from_fo.assert_called_once_with(mock_open.return_value.__enter__.return_value)

    @patch("model.file_based.UserFile._write_data_file")
    def test_create_empty_data_file(self, mock_write_data):
        UserFile._create_empty_data_file()
        mock_write_data.assert_called_once_with([
            {'id': '0', 'pa': None, 'ch': ['1']},
            {'pa': '0', 'id': '1', 'nm': 'Write down your thoughts'},
        ])

    @patch("model.file_based.open")
    @patch("model.file_based.os.makedirs")
    def test_write_data_file(self, mock_makedirs, mock_open):
        self.uf._write_data_file({"hi": "bye"})
        mock_makedirs.assert_called_once_with(ANY, exist_ok=True)


if __name__ == "__main__":
    unittest.main()
