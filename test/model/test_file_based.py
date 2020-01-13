#!/usr/bin/env python3.6
import unittest
import unittest.mock as mock

from model.file_based import UserFile
from model.model_node import Node
from model.history import History
from model.node_store import NodeStore


class Test_UserFile(unittest.TestCase):
    @mock.patch("model.file_based.UserFile._load_data")
    def setUp(self, mocked_load_data):
        self.uf = UserFile()
        mocked_load_data.assert_called_once()
        self.assertEqual(0, len(self.uf.nds))
        test_data = [
            {"id": "0","nm": "root","cl": False,"ch": ["1","2"],"pa": None},
            {"id": "1","nm": "henlo","cl": False,"ch": [],"pa": "0"},
            {"id": "2","nm": "goodbye","cl": False,"ch": ["3", "4"],"pa": "0"},
            {"id": "3","nm": "sayonara","cl": False,"ch": [],"pa": "2"},
            {"id": "4","nm": "nice","cl": False,"ch": [],"pa": "2"}
        ]
        nds = NodeStore()
        for node_def in test_data:
            nds.add_node(Node(node_def))
        self.uf.nds = nds
        self.assertEqual(5, len(self.uf.nds))

    def test_current_node(self):
        self.assertEqual(self.uf.current_node.uuid, "1")


if __name__ == "__main__":
    unittest.main()
