#!/usr/bin/env python3
import os
from lazy import lazy
import requests
import yaml

class Document:
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.children = []
        self.content = ""


class UserInfo:
    CONFIG_FILE = "~/.wfclirc"
    URL = {"login": "https://workflowy.com/ajax_login",
            }

    def __init__(self):
        self.root = Document("blue")
        self.session = requests.Session()

    @lazy
    def session_id(self):
        """ Returns the session id" for the login session.
        Creates a new session if there isn't one, or the
        current is expired """

        rc_path = os.path.expanduser(self.CONFIG_FILE)
        data = None
        with open(rc_path, 'r') as f:
            data = f.read()
        yaml_data = yaml.safe_load(data).split(' ')
        if len(yaml_data) != 2:
            raise ValueError("Malformed YAML. {} elements in YAML return".format(len(yaml_data)))
        success, sid = self._log_in(usr=yaml_data[0], pw=yaml_data[1])
        if success:
            return sid
        else:
            raise ValueError("Was not able to log in!")

    def _log_in(self, usr, pw):
        payload = {"username": usr, "password": pw}
        result = self.session.post(self.URL["login"],
                                   data=payload,
                                   )
        if result.json()["success"]:
            self.session_cookies = result.cookies
            return (True, result.json()["sid"])
        else:
            return (False, False)
