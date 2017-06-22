# -*- coding: UTF8 -*-
import logging

import studiolibrary

import studioqt

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(funcName)s: %(message)s',
    filemode='w'
)


if __name__ == "__main__":

    with studioqt.app():
        studiolibrary.main(u"Exён Шple")