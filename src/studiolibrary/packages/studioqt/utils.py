# Copyright 2016 by Kurt Rathjen. All Rights Reserved.
#
# Permission to use, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Kurt Rathjen
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# KURT RATHJEN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# KURT RATHJEN BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import sys
import json
import inspect
import logging
import platform
import contextlib

import studioqt

from studioqt import QtCore
from studioqt import QtUiTools
from studioqt import QtWidgets


__all__ = [
    "app",
    "loadUi",
    "saveJson",
    "readJson",
    "showInFolder",
    "isAltModifier",
    "isControlModifier",
    "currentScreenGeometry",
]

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def app():
    """
    
    .. code-block:: python
        import studioqt

        with studioqt():
            widget = QWidget(None)
            widget.show()

    :rtype: None
    """
    app_ = None

    isAppRunning = bool(QtWidgets.QApplication.instance())
    if not isAppRunning:
        app_ = QtWidgets.QApplication(sys.argv)

    yield None

    if not isAppRunning:
        sys.exit(app_.exec_())


def currentScreenGeometry():
    """
    Return the geometry of the screen with the current cursor.

    :rtype: QtCore.QRect
    """
    pos = QtWidgets.QApplication.desktop().cursor().pos()
    screen = QtWidgets.QApplication.desktop().screenNumber(pos)
    return QtWidgets.QApplication.desktop().screenGeometry(screen)


def system():
    """
    :rtype: str
    """
    return platform.system().lower()


def isMac():
    """
    :rtype: bool
    """
    return system().startswith("mac") or system().startswith("os") \
        or system().startswith("darwin")


def isWindows():
    """
    :rtype: bool
    """
    return system().startswith("win")


def isLinux():
    """
    :rtype: bool
    """
    return system().startswith("lin")


def showInFolder(path):
    """
    Show the given path in the system file explorer.
    
    :type path: str
    :rtype: None
    """
    if studioqt.SHOW_IN_FOLDER_CMD:
        cmd = studioqt.SHOW_IN_FOLDER_CMD

    elif isLinux():
        cmd = 'konqueror "{path}"&'

    elif isWindows():
        cmd = 'start explorer /select, "{path}"'

    elif isMac():
        cmd = 'open -R "{path}"'

    # Normalize the pathname for windows
    path = os.path.normpath(path)
    cmd = cmd.format(path=path)

    logger.info(cmd)
    os.system(cmd)


def saveJson(path, data):
    """
    Write a python dict to a json file.

    :type path: str
    :type data: dict
    :rtype: None
    """
    dirname = os.path.dirname(path)

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(path, "w") as f:
        data = json.dumps(data, indent=4)
        f.write(data)


def readJson(path):
    """
    Read a json file to a python dict.

    :type path: str
    :rtype: dict
    """
    data = {}

    if os.path.exists(path):
        with open(path, "r") as f:
            data_ = f.read()
            if data_:
                data = json.loads(data_)

    return data


def uiPath(cls):
    """
    :type cls: type
    :rtype: str
    """
    name = cls.__name__
    path = inspect.getfile(cls)
    dirname = os.path.dirname(path)

    path = dirname + "/resource/ui/" + name + ".ui"
    return path


def loadUi(widget, path=None):
    """
    .. code-block:: python
        import studioqt

        class Widget(QtWidgets.QWidget):
            def __init__(self)
                super(Widget, self).__init__()
                studioqt.loadUi(self)

        with studioqt.app():
            widget = Widget()
            widget.show()

    :type widget: QWidget or QDialog
    :type path: str
    :rtype: None
    """
    if not path:
        path = uiPath(widget.__class__)

    loadUiPySide(widget, path)


def loadUiPySide(widget, path=None):
    """
    :type widget: QtWidgets.QWidget
    :type path: str
    :rtype: None
    """
    loader = QtUiTools.QUiLoader()
    loader.setWorkingDirectory(os.path.dirname(path))

    f = QtCore.QFile(path)
    f.open(QtCore.QFile.ReadOnly)
    widget.ui = loader.load(path, widget)
    f.close()

    layout = QtWidgets.QVBoxLayout()
    layout.setObjectName("uiLayout")
    layout.addWidget(widget.ui)
    widget.setLayout(layout)
    layout.setContentsMargins(0, 0, 0, 0)

    widget.setMinimumWidth(widget.ui.minimumWidth())
    widget.setMinimumHeight(widget.ui.minimumHeight())
    widget.setMaximumWidth(widget.ui.maximumWidth())
    widget.setMaximumHeight(widget.ui.maximumHeight())


def mayaWindow():
    """
    :rtype: QtCore.QObject
    """
    instance = None
    try:
        import maya.OpenMayaUI as mui
        import sip

        ptr = mui.MQtUtil.mainWindow()
        instance = sip.wrapinstance(long(ptr), QtCore.QObject)

    except Exception:
        logger.debug("Warning: Cannot find a maya window.")
        pass

    return instance


def isModifier():
    return isAltModifier() or isControlModifier()


def isAltModifier():
    """

    :rtype: bool
    """
    modifiers = QtWidgets.QApplication.keyboardModifiers()
    return modifiers == QtCore.Qt.AltModifier


def isControlModifier():
    """
    :rtype: bool
    """
    modifiers = QtWidgets.QApplication.keyboardModifiers()
    return modifiers == QtCore.Qt.ControlModifier
