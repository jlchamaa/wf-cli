#!/usr/bin/env python3
import logging
from view_model.view_model import ViewModel
log = logging.getLogger("wfcli")
log.setLevel(logging.DEBUG)
log.addHandler(logging.FileHandler("spam.log"))

def main():
    log.info("Main loop entered")
    vm = ViewModel()

if __name__ == "__main__":
    main()
