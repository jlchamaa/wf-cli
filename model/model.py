#!/usr/bin/env python3
import os
import pickle
import sys
from lazy import lazy
import requests
import json


class UserInfo:
    CONFIG_FILE = "~/.config/wfcli/.wfclirc"
    COOKIE_FILE = "~/.config/wfcli/.wfclicookies"
    URL = {"login": "https://workflowy.com/ajax_login",
           "initialize": "https://workflowy.com/get_initialization_data?client_version=20",
            }

    def __init__(self):
        self.session = requests.Session()
        self.data = self.get_data()
        self.root = self.data["projectTreeData"]["mainProjectTreeInfo"]["rootProjectChildren"]

    def get_data(self):
        return self.session.post(self.URL["initialize"],
                                 cookies=self.session_cookies).json()

    @lazy
    def session_cookies(self):
        cookie_path = os.path.expanduser(self.COOKIE_FILE)
        if os.path.exists(cookie_path):
            with open(cookie_path, 'rb') as f:
                data = f.read()
                return pickle.loads(data)
        else:
            usr, pw = self.get_credentials
            cookies = self._log_in(usr, pw)
            with open(cookie_path, 'wb') as f:
                f.write(pickle.dumps(cookies))
            return cookies

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
            return response.cookies
        else:
            print("Login Unsuccessful. {}".format(result["errors"]["__all__"]))
            sys.exit(1)

    def get_root_content(self):
        return [(node["nm"],node['id']) for node in self.root]

    @lazy
    def get_credentials(self):
        data = None
        rc_path = os.path.expanduser(self.CONFIG_FILE)
        if not os.path.exists(rc_path):
            print("{} not found.  Please create the file first!".format(rc_path))
            sys.exit(1)
        with open(rc_path, 'r') as f:
            data = f.read()
        try:
            data =json.loads(data)
            return (data["usr"], data["pw"])
        except:
            print("{} malformed! Ensure you have a 'usr' and 'pw' field.".format(rc_path))
            sys.exit(1)
