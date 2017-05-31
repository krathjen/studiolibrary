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

    def _folderRenamed(oldPath, newPath):
        print "Renamed:", oldPath, ">>>", newPath

    with studioqt.app():
        library = studiolibrary.main("Default", lockFolder="Malcolm")

        widget = library.libraryWidget()
        widget.folderRenamed.connect(_folderRenamed)
