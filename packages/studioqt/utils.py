# Copyright 2017 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.

import ctypes
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
    "fadeIn",
    "fadeOut",
    "loadUi",
    "saveJson",
    "readJson",
    "showInFolder",
    "isAltModifier",
    "isControlModifier",
    "currentScreenGeometry",
    "InvokeRepeatingThread",
]

logger = logging.getLogger(__name__)


class InvokeRepeatingThread(QtCore.QThread):
    """
    A convenience class for invoking a method to the given repeat rate.
    """

    triggered = QtCore.Signal()

    def __init__(self, repeatRate, *args):
        QtCore.QThread.__init__(self, *args)

        self._repeatRate = repeatRate

    def run(self):
        """
        The starting point for the thread.
        
        :rtype: None 
        """
        while True:
            QtCore.QThread.sleep(self._repeatRate)
            self.triggered.emit()


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


def uiPath(cls):
    """
    Return the ui path for the given widget class.
    
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


def isModifier():
    """
    Return True if either the alt key or control key is down.
    
    :rtype: bool 
    """
    return isAltModifier() or isControlModifier()


def isAltModifier():
    """
    Return True if the alt key is down.

    :rtype: bool
    """
    modifiers = QtWidgets.QApplication.keyboardModifiers()
    return modifiers == QtCore.Qt.AltModifier


def isControlModifier():
    """
    Return True if the control key is down.
    
    :rtype: bool
    """
    modifiers = QtWidgets.QApplication.keyboardModifiers()
    return modifiers == QtCore.Qt.ControlModifier


def fadeIn(widget, duration=200, onFinished=None):
    """
    Fade in the given widget using the opacity effect.

    :type widget: QtWidget.QWidgets
    :type duration: int 
    :type onFinished: func
    :rtype: QtCore.QPropertyAnimation 
    """
    effect = QtWidgets.QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QtCore.QPropertyAnimation(effect, "opacity")
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
    animation.start()

    if onFinished:
        animation.finished.connect(onFinished)

    return animation


def fadeOut(widget, duration=200, onFinished=None):
    """
    Fade out the given widget using the opacity effect.
    
    :type widget: QtWidget.QWidgets
    :type duration: int
    :type onFinished: func
    :rtype: QtCore.QPropertyAnimation 
    """
    effect = QtWidgets.QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QtCore.QPropertyAnimation(effect, "opacity")
    animation.setDuration(duration)
    animation.setStartValue(1.0)
    animation.setEndValue(0.0)
    animation.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
    animation.start()

    if onFinished:
        animation.finished.connect(onFinished)

    return animation


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

    :type path: unicode
    :rtype: None
    """
    cmd = os.system
    args = []

    if studioqt.SHOW_IN_FOLDER_CMD:
        args = [unicode(studioqt.SHOW_IN_FOLDER_CMD)]

    elif isLinux():
        args = [u'konqueror "{path}"&']

    elif isWindows():
        # os.system() nither subprocess.call() can't pass command with non ascii symbols,
        # use ShellExecuteW directly
        args = [None, u'open', u'explorer.exe', u'/n,/select, "{path}"', None, 1]
        cmd = ctypes.windll.shell32.ShellExecuteW

    elif isMac():
        args = [u'open -R "{path}"']

    # Normalize the pathname for windows
    path = os.path.normpath(path)

    for i, a in enumerate(args):
        if isinstance(a, basestring) and '{path}' in a:
            args[i] = a.format(path=path)

    logger.info("Call: '%s' with arguments: %s", cmd.__name__, args)
    cmd(*args)


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
    path = os.path.abspath(path)
    path = path.replace("\\", "/")

    with open(path, "r") as f:
        data = f.read()

    relPath = os.path.dirname(path)
    relPath2 = os.path.dirname(relPath)
    relPath3 = os.path.dirname(relPath2)

    data = data.replace('\".../', '"' + relPath3 + '/')
    data = data.replace('\"../', '"' + relPath2 + '/')
    data = data.replace('\"./', '"' + relPath + '/')

    if data:
        data = json.loads(data)

    return data
