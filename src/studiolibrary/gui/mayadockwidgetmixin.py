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

import logging

from studioqt import QtCore
from studioqt import QtWidgets

try:
    import maya.cmds
    import maya.OpenMayaUI as omui
    isMaya = True
except ImportError:
    isMaya = False

try:
    from shiboken import wrapInstance
except Exception, msg:
    print msg

try:
    from shiboken2 import wrapInstance
except Exception, msg:
    print msg


__all__ = [
    "MayaDockWidgetMixin",
]

logger = logging.getLogger(__name__)


class MayaDockWidgetMixin(object):

    DEFAULT_DOCK_AREA = "none"
    DEFAULT_DOCK_ALLOWED_AREAS = ["top", "bottom", "left", "right"]

    dockingChanged = QtCore.Signal()

    @staticmethod
    def generateUniqueObjectName(name, attempts=100):
        """
        Generate a unique name for the dock widget.

        :type name: str
        :type attempts: int
        :rtype: str
        """
        for i in range(1, attempts):
            uniqueName = name + str(i)
            controlExists = maya.cmds.control(uniqueName, exists=True)
            if not controlExists:
                return uniqueName

        msg = 'Cannot find unique window name for "{0}"'
        msg = msg.format(name)
        raise ValueError(msg)

    @staticmethod
    def dockAreaStrMap():
        """
        :rtype: dict
        """
        return {
            'none': QtCore.Qt.NoDockWidgetArea,
            'top': QtCore.Qt.TopDockWidgetArea,
            'left': QtCore.Qt.LeftDockWidgetArea,
            'right': QtCore.Qt.RightDockWidgetArea,
            'bottom': QtCore.Qt.BottomDockWidgetArea,
            'all': QtCore.Qt.AllDockWidgetAreas
        }

    @staticmethod
    def dockAreaMap():
        """
        :rtype: dict
        """
        return {
            QtCore.Qt.NoDockWidgetArea: 'none',
            QtCore.Qt.TopDockWidgetArea: 'top',
            QtCore.Qt.LeftDockWidgetArea: 'left',
            QtCore.Qt.RightDockWidgetArea: 'right',
            QtCore.Qt.BottomDockWidgetArea: 'bottom',
            QtCore.Qt.AllDockWidgetAreas: 'all'
        }

    def __init__(self, *args):
        self._dockWidgetName = None
        self._dockLayoutName = None

    def setObjectName(self, name):
        """
        :type name: str
        """
        try:
            name = self.generateUniqueObjectName(name)
        except NameError, msg:
            logger.exception(msg)

        QtWidgets.QWidget.setObjectName(self, name)

    def setupDockSignals(self):
        dockWidget = self.dockWidget()
        dockWidget.topLevelChanged.connect(self._topLevelChanged)
        dockWidget.dockLocationChanged.connect(self._dockLocationChanged)

    def _topLevelChanged(self, value, *args):
        """
        :type value: bool
        """
        self._dockingChanged()

    def _dockLocationChanged(self, dockArea):
        """
        :type dockArea: QtCore.Qt.DockWidgetAreas
        """
        self._dockingChanged()

    def _dockingChanged(self):
        """
        Triggered either when the location changes or floating changes.
        """
        if self.dockWidget():
            self.dockWidget().setMinimumWidth(50)
            self.dockWidget().setMinimumHeight(50)

        msg = "Docking Changed: {0}"
        msg = msg.format(self.dockSettings())
        logger.debug(msg)

        self.dockingChanged.emit()

    def showEvent(self, event):
        """
        :type event: QtWidgets.QShowEvent
        """
        QtWidgets.QWidget.showEvent(self, event)
        self.fixMinimumDockSize()

    def parentX(self):
        """
        :rtype: QtWidgets.QWidget
        """
        return self.parent() or self

    def dockWidget(self):
        """
        :rtype: QtWidgets.QDockWidget
        """
        return self.parent()

    def mayaWindow(self):
        """
        :rtype: QMainWindow
        """
        mainWindowPtr = omui.MQtUtil.mainWindow()
        return wrapInstance(long(mainWindowPtr), QtWidgets.QMainWindow)

    def mapDockAreaToStr(self, dockArea):
        """
        :type dockArea: QtCore.Qt.QDockArea
        :rtype: str
        """
        map = self.dockAreaMap()
        return map[dockArea]

    def mapDockAreaFromStr(self, dockAreaStr):
        """
        :type dockAreaStr: str
        :rtype: QtCore.Qt.QDockArea
        """
        map = self.dockAreaStrMap()
        return map[dockAreaStr]

    def dockArea(self):
        """
        :rtype: QtCore.Qt.DockWidgetAreas
        """
        if self.isFloating():
            dockArea = QtCore.Qt.NoDockWidgetArea
        else:
            dockArea = self.mayaWindow().dockWidgetArea(self.dockWidget())
        return dockArea

    def dockAreaStr(self):
        """
        :rtype: str
        """
        return self.mapDockAreaToStr(self.dockArea())

    def setWindowTitle(self, text):
        """
        :type text: str
        """
        if self.dockWidget():
            self.dockWidget().setWindowTitle(text)
        QtWidgets.QWidget.setWindowTitle(self, text)

    def isDocked(self):
        """
        :rtype: bool
        """
        return not self.isFloating()

    def isFloating(self):
        """
        :rtype: bool
        """
        isFloating = True

        if self.dockWidget():
            isFloating = self.dockWidget().isFloating()

        return isFloating

    def setFloating(self):
        self.setDockArea(dockArea=QtCore.Qt.NoDockWidgetArea)

    def dockTop(self):
        self.setDockArea(dockArea=QtCore.Qt.TopDockWidgetArea)

    def dockLeft(self):
        self.setDockArea(dockArea=QtCore.Qt.LeftDockWidgetArea)

    def dockRight(self):
        self.setDockArea(dockArea=QtCore.Qt.RightDockWidgetArea)

    def dockBottom(self):
        self.setDockArea(dockArea=QtCore.Qt.BottomDockWidgetArea)

    def isDockedTop(self):
        return self.dockArea() == QtCore.Qt.TopDockWidgetArea

    def isDockedLeft(self):
        return self.dockArea() == QtCore.Qt.LeftDockWidgetArea

    def isDockedRight(self):
        return self.dockArea() == QtCore.Qt.RightDockWidgetArea

    def isDockedBottom(self):
        return self.dockArea() == QtCore.Qt.BottomDockWidgetArea

    def dockMenu(self):
        """
        Return a menu for editing the dock settings.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu(self)
        menu.setTitle("Dock")

        action = QtWidgets.QAction("Set Floating", menu)
        action.setEnabled(self.isDocked())
        action.triggered.connect(self.setFloating)
        menu.addAction(action)

        menu.addSeparator()

        action = QtWidgets.QAction("Dock top", menu)
        action.setCheckable(True)
        action.setChecked(self.isDockedTop())
        action.triggered.connect(self.dockTop)
        menu.addAction(action)

        action = QtWidgets.QAction("Dock left", menu)
        action.setCheckable(True)
        action.setChecked(self.isDockedLeft())
        action.triggered.connect(self.dockLeft)
        menu.addAction(action)

        action = QtWidgets.QAction("Dock right", menu)
        action.setCheckable(True)
        action.setChecked(self.isDockedRight())
        action.triggered.connect(self.dockRight)
        menu.addAction(action)

        action = QtWidgets.QAction("Dock bottom", menu)
        action.setCheckable(True)
        action.setChecked(self.isDockedBottom())
        action.triggered.connect(self.dockBottom)
        menu.addAction(action)

        return menu

    def dockSettings(self):
        """
        :rtype: dict
        """
        dockSettings = {}

        if self.dockWidget():
            dockSettings = {
                "area": self.dockAreaStr(),
                "width": self.dockWidth(),
                "height": self.dockHeight()
            }

        return dockSettings

    def setDockSettings(self, settings):
        """
        :type settings: dict
        """
        width = settings.get("width", self.width())
        height = settings.get("height", self.height())
        dockAreaStr = settings.get("area", self.DEFAULT_DOCK_AREA)

        dockArea = self.mapDockAreaFromStr(dockAreaStr)
        self.setDockArea(dockArea=dockArea, width=width, height=height)

    # -----------------------------------------------------------------------
    # Creating and setting the dock widget using cmds.dockControl.
    # Note: cmds.dockControl seems more reliable than the dock widget
    # itself. Eg: It returns the correct width when collapsed
    # -----------------------------------------------------------------------

    def fixMinimumDockSize(self):
        """
        Fix the dock size when docked for Maya 2014 on linux.

        :rtype: None
        """
        dockWidgetPtr = omui.MQtUtil.findControl(self._dockWidgetName)
        dockWidget = wrapInstance(long(dockWidgetPtr), QtWidgets.QWidget)
        dockWidget.setMinimumSize(QtCore.QSize(20, 20))

    def dockWidth(self):
        """
        :rtype: int
        """
        return maya.cmds.dockControl(self._dockWidgetName, q=True, w=True)

    def dockHeight(self):
        """
        :rtype: int
        """
        return maya.cmds.dockControl(self._dockWidgetName, q=True, h=True)

    def raise_(self):
        """
        Raise the window to the top of the screen.
        """
        if self._dockWidgetName:
            maya.cmds.dockControl(
                self._dockWidgetName,
                r=True,
                edit=True,
                visible=True,
            )
        else:
            QtWidgets.QWidget.raise_(self)

    def _createDockLayout(self):
        """
        :rtype: str
        """
        objectName = str(self.objectName())

        self._dockLayoutName = maya.cmds.columnLayout(parent=objectName)
        maya.cmds.layout(self._dockLayoutName, edit=True, visible=False)

        return self._dockLayoutName

    def _createDockWidget(self, dockAreaStr, allowedAreas):
        """
        :type dockAreaStr: str or None
        :type allowedAreas: list[str]
        """
        self._createDockLayout()

        isFloating = False
        objectName = str(self.objectName())

        if dockAreaStr == "none":
            isFloating = True
            dockAreaStr = "left"

        self._dockWidgetName = maya.cmds.dockControl(
            r=True,
            area=dockAreaStr,
            content=objectName,
            floating=isFloating,
            allowedArea=allowedAreas
        )

        self.setupDockSignals()
        self.setWindowTitle(self.windowTitle())

    def setDockArea(
        self,
        dockArea,
        width=None,
        height=None,
        allowedAreas=None
    ):
        """
        :type dockArea: QtCore.Qt.DockWidgetAreas
        :type width: int or None
        :type height: int or None
        :type allowedAreas: list[str] or None
        """
        if isMaya:

            width = width or self.width()
            height = height or self.height()
            dockArea = dockArea or self.DEFAULT_DOCK_AREA
            allowedAreas = allowedAreas or self.DEFAULT_DOCK_ALLOWED_AREAS

            if isinstance(dockArea, basestring):
                dockAreaStr = dockArea
            else:
                dockAreaStr = self.mapDockAreaToStr(dockArea)

            if not self._dockWidgetName:
                self._createDockWidget(
                    dockAreaStr=dockAreaStr,
                    allowedAreas=allowedAreas
                )

            if dockArea == "none":
                maya.cmds.dockControl(
                    self._dockWidgetName,
                    r=True,
                    edit=True,
                    width=width,
                    height=height,
                    visible=True,
                    floating=True
                )
            else:
                maya.cmds.dockControl(
                    self._dockWidgetName,
                    r=True,
                    edit=True,
                    width=width,
                    height=height,
                    visible=True,
                    area=dockAreaStr,
                    floating=False
                )
