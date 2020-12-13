import unittest
import unittest.mock as mock

from view.view import View
from view_model.view_model import ViewModel


class Test_LateralCursor(unittest.TestCase):
    @mock.patch("model.file_based.UserFile._load_data")
    def setUp(self, mocked_load_data):
        self.vm = ViewModel()
        self.vm.render = mock.MagicMock()
        mocked_load_data.assert_called_once()
        test_data = [
            {"id": "0", "nm": "root", "cl": False, "ch": ["1", "2"], "pa": None},
            {"id": "1", "nm": "henlo", "cl": False, "ch": [], "pa": "0"},
            {"id": "2", "nm": "goodbye", "cl": False, "ch": [], "pa": "0"},
        ]
        self.vm.m.data_from_flat_object(test_data)
        self.assertEqual(3, len(self.vm.m.nds))
        self.vm.v = View()
        self.lc = self.vm.v.lc  # purely an alias

    def test_initial_position(self):
        self.assertEqual(self.lc.in_line(self.vm.visible_nodes[0]), 0)

    def test_nav_down_stay_0(self):
        nodes = self.vm.visible_nodes
        self.assertEqual(self.lc.in_line(nodes[0]), 0)
        self.vm.nav_down()
        self.assertEqual(self.lc.in_line(nodes[1]), 0)

    def test_nav_down_stay_EOL(self):
        nodes = self.vm.visible_nodes
        self.vm.dollar_sign()
        self.assertEqual(self.lc.in_line(nodes[0]), 4)
        self.vm.nav_down()
        self.assertEqual(self.lc.in_line(nodes[1]), 6)

    def test_cursor_stays_out_even_when_moved_to_smaller_line(self):
        nodes = self.vm.visible_nodes
        self.vm.dollar_sign()
        self.vm.nav_down()
        self.assertEqual(self.lc.in_line(nodes[1]), 6)
        self.vm.nav_left()
        self.assertEqual(self.lc.in_line(nodes[1]), 5)
        self.vm.nav_up()
        self.assertEqual(self.lc.in_line(nodes[0]), 4)
        self.vm.nav_down()
        self.assertEqual(self.lc.in_line(nodes[1]), 5)

    def test_cursor_can_extend_1_in_edit_mode(self):
        nodes = self.vm.visible_nodes
        self.vm.dollar_sign()
        self.assertEqual(self.lc.in_line(nodes[0]), 4)
        self.vm.nav_right()
        self.assertEqual(self.lc.in_line(nodes[0]), 4)
        self.vm.edit_mode()
        self.vm.nav_right()
        self.assertEqual(self.lc.in_line(nodes[0]), 5)
        self.vm.nav_right()
        self.assertEqual(self.lc.in_line(nodes[0]), 5)

    def test_edit_doesnt_shift_cursor(self):
        nodes = self.vm.visible_nodes
        self.assertEqual(self.lc.in_line(nodes[0]), 0)
        self.vm.edit_mode()
        self.assertEqual(self.lc.in_line(nodes[0]), 0)

    @mock.patch("view_model.view_model.ViewModel.save_data")
    def test_normal_does_shift_cursor(self, mock_save_data):
        nodes = self.vm.visible_nodes
        self.vm.nav_right()
        self.assertEqual(self.lc.in_line(nodes[0]), 1)
        self.vm.edit_mode()
        self.assertEqual(self.lc.in_line(nodes[0]), 1)
        self.vm.normal_mode()
        self.assertEqual(self.lc.in_line(nodes[0]), 0)
        mock_save_data.assert_called_once_with()

    @mock.patch("view_model.view_model.ViewModel.save_data")
    def test_normal_does_shift_cursor_but_not_past_zero(self, mock_save_data):
        nodes = self.vm.visible_nodes
        self.assertEqual(self.lc.in_line(nodes[0]), 0)
        self.vm.edit_mode()
        self.assertEqual(self.lc.in_line(nodes[0]), 0)
        self.vm.normal_mode()
        self.assertEqual(self.lc.in_line(nodes[0]), 0)
        mock_save_data.assert_called_once_with()

    @mock.patch("view_model.view_model.ViewModel.save_data")
    def test_newline_content(self, mock_save_data):
        self.vm.open_below()
        self.vm.add_char(char="a")
        self.vm.add_char(char="b")
        self.vm.add_char(char="c")
        nodes = self.vm.visible_nodes
        self.assertEqual(self.lc.in_line(nodes[1]), 3)
        self.vm.normal_mode()
        self.assertEqual(self.lc.in_line(nodes[1]), 2)
        mock_save_data.assert_called_once_with()

    @mock.patch("view_model.view_model.ViewModel.save_data")
    def test_newline_content_with_backspace(self, mock_save_data):
        self.vm.open_below()
        self.vm.add_char(char="a")
        self.vm.add_char(char="b")
        self.vm.delete_char()
        self.vm.add_char(char="b")
        self.vm.add_char(char="c")
        nodes = self.vm.visible_nodes
        self.assertEqual(self.lc.in_line(nodes[1]), 3)
        self.vm.normal_mode()
        self.assertEqual(self.lc.in_line(nodes[1]), 2)
        mock_save_data.assert_called_once_with()
