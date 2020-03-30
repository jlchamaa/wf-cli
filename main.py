#!/usr/bin/env python3
import logging
from view_model.view_model import ViewModel
log = logging.getLogger("wfcli")
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("spam.log")
fh.setLevel(logging.DEBUG)
log.addHandler(fh)


def main():
    log.info("Main loop entered")
    vm = ViewModel()
    vm.run()


if __name__ == "__main__":
    main()
