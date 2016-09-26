"""
"""
import logging

import studiolibrary

import studioqt

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(funcName)s: %(message)s',
    filemode='w'
)

logger = logging.getLogger("test_library")


if __name__ == "__main__":

    from studiolibraryplugins import lockplugin

    # plugins = [lockplugin.Plugin()]

    with studioqt.app():
        path = "C:/Users/Hovel/Dropbox/libraries"
        studiolibrary.main("HEYHEY", path=path, lockFolder="Malcolm")
        # studiolibrary.main("HEYHEY", show=True)