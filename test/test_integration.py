#!/usr/bin/env python3.6
import unittest
from unittest.mock import Mock, patch
from model.model_node import Node


class Test_All(unittest.TestCase):
    def test_reality(self):
        self.assertEqual(1, 1)


if __name__ == "__main__":
    unittest.main()
