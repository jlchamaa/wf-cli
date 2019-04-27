import unittest
from mock import Mock, patch
from tempfile import NamedTemporaryFile
from model import model

class Test_Model(unittest.TestCase):
    def setUp(self):
        pass

    @patch("model.model.UserInfo._log_in")
    def test_session_id_successful_login(self, mocked_log_in):
        mocked_log_in.return_value = (True , "FAKE_SID")
        temp  = NamedTemporaryFile()
        my_userInfo = model.UserInfo()
        with open(temp.name, "w+") as f:
            f.write("---\nfake_user\nfake_password")
        my_userInfo.CONFIG_FILE = temp.name
        self.assertEqual("FAKE_SID", my_userInfo.session_id)
        print(dir(mocked_log_in))
        mocked_log_in.assert_called_once_with(usr="fake_user", pw="fake_password")

    @patch("model.model.UserInfo._log_in")
    def test_session_id_failed_login(self, mocked_log_in):
        mocked_log_in.return_value = (False , "FAKE_SID")
        temp  = NamedTemporaryFile()
        my_userInfo = model.UserInfo()
        with open(temp.name, "w+") as f:
            f.write("---\nfake_user\nfake_password")
        my_userInfo.CONFIG_FILE = temp.name
        with self.assertRaises(ValueError):
            my_userInfo.session_id
        mocked_log_in.assert_called_once_with(usr="fake_user", pw="fake_password")

    def test_log_in_success(self):
        UI = model.UserInfo()
        UI.session = Mock()
        UI.URL["login"] = "fake_url"
        UI.session.post.return_value.json.return_value = {"success": True, "sid": "fake_sid"}
        res1, res2 = UI._log_in("fake_user", "fake_pw")
        self.assertTrue(res1)
        self.assertEqual(res2, "fake_sid")

    def test_log_in_failure(self):
        UI = model.UserInfo()
        UI.session = Mock()
        UI.URL["login"] = "fake_url"
        UI.session.post.return_value.json.return_value = {"success": False, "sid": "fake_sid"}
        res1, res2 = UI._log_in("fake_user", "fake_pw")
        self.assertFalse(res1)
        self.assertFalse(res2)
