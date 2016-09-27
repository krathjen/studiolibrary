# -*- coding: UTF8 -*-
import logging

import studiolibrary

import studioqt

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(funcName)s: %(message)s',
    filemode='w'
)

logger = logging.getLogger("test_library")


from studioqt import QtWidgets

if __name__ == "__main__":

    with studioqt.app():
        path = "C:/Users/Hovel/Dropbox/libraries"
        library = studiolibrary.main("Hello", path=path, lockFolder="Malcolm")