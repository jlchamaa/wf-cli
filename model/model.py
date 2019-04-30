#!/usr/bin/env python3
import os
import sys
from lazy import lazy
import requests
import yaml


class UserInfo:
    CONFIG_FILE = "~/.wfclirc"
    URL = {"login": "https://workflowy.com/ajax_login",
           "initialize": "https://workflowy.com/get_initialization_data?client_version=20",
            }

    def __init__(self):
        self.session = requests.Session()
        self.session_id
        self.data = self.get_data()
        self.root = self.data["projectTreeData"]["mainProjectTreeInfo"]["rootProjectChildren"]

    def get_data(self):
        return self.session.post(self.URL["initialize"],
                                 cookies=self.session_cookies).json()

    @lazy
    def session_id(self):
        """ Returns the session id" for the login session.
        Creates a new session if there isn't one, or the
        current is expired """
        rc_path = os.path.expanduser(self.CONFIG_FILE)
        data = None
        if not os.path.exists(rc_path):
            print("{} not found.  Please create the file first!".format(rc_path))
            sys.exit(1)
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
        response = self.session.post(self.URL["login"],
                                   data=payload,
                                   )
        result = response.json()
        if "errors" in result:
            print("Login Error. {}".format(result["errors"]["__all__"]))
            sys.exit(1)
        if result["success"]:
            self.session_cookies = response.cookies
            return (True, result["sid"])
        else:
            return (False, False)
