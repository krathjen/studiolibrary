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

"""
#---------------------------------------------------------------------------
# Saving a pose item
#---------------------------------------------------------------------------

from studiolibraryitems import poseitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.pose"
objects = maya.cmds.ls(selection=True) or []

item = poseitem.PoseItem(path)
item.save(objects=objects)

#---------------------------------------------------------------------------
# Loading a pose item
#---------------------------------------------------------------------------

from studiolibraryitems import poseitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.pose"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

item = poseitem.PoseItem(path)
item.load(objects=objects, namespaces=namespaces, key=True, mirror=False)
"""

import os
import logging
from functools import partial

# studioqt supports both pyside (Qt4) and pyside2 (Qt5)
import studioqt
from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studiolibrary
import studiolibraryitems

from studiolibraryitems import transferitem

try:
    import mutils
    import maya.cmds
except ImportError, e:
    print e


__all__ = [
    "PoseItem",
    "PoseCreateWidget",
    "PosePreviewWidget"
]


logger = logging.getLogger(__name__)


class PoseItemSignals(QtCore.QObject):
    """"""
    mirrorChanged = QtCore.Signal(bool)


class PoseItem(transferitem.TransferItem):

    _poseItemSignals = PoseItemSignals()
    mirrorChanged = _poseItemSignals.mirrorChanged

    @classmethod
    def typeIconPath(cls):
        """
        Return the type icon path on disc.

        :rtype: path
        """
        return studiolibraryitems.resource().get("icons", "pose.png")

    @classmethod
    def createAction(cls, menu, libraryWidget):
        """
        Return the action to be displayed when the user clicks the "plus" icon.

        :type menu: QtWidgets.QMenu
        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: QtCore.QAction
        """
        icon = QtGui.QIcon(cls.typeIconPath())
        callback = partial(cls.showCreateWidget, libraryWidget)

        action = QtWidgets.QAction(icon, "Pose", menu)
        action.triggered.connect(callback)

        return action

    @staticmethod
    def showCreateWidget(libraryWidget):
        """
        Show the widget for creating a new pose item.

        :type libraryWidget: studiolibrary.LibraryWidget
        """
        widget = PoseCreateWidget()
        widget.folderFrame().hide()
        widget.setFolderPath(libraryWidget.selectedFolderPath())

        libraryWidget.setCreateWidget(widget)
        libraryWidget.folderSelectionChanged.connect(widget.setFolderPath)

    def __init__(self, *args, **kwargs):
        """
        Create a new instance of the pose item from the given path.

        :type path: str
        :type args: list
        :type kwargs: dict
        """
        transferitem.TransferItem.__init__(self, *args, **kwargs)

        self._options = None
        self._isLoading = False
        self._autoKeyFrame = None

        self.setBlendingEnabled(True)
        self.setTransferClass(mutils.Pose)
        self.setTransferBasename("pose.dict")

        if not os.path.exists(self.transferPath()):
            self.setTransferBasename("pose.json")

    def previewWidget(self, libraryWidget):
        """
        Return the widget to be shown when the user clicks on the item.

        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: PosePreviewWidget
        """
        return PosePreviewWidget(item=self)

    def isLoading(self):
        """
        :rtype: bool
        """
        return self._isLoading

    def toggleMirror(self):
        """
        :rtype: None
        """
        mirror = self.isMirrorEnabled()
        mirror = False if mirror else True
        self.setMirrorEnabled(mirror)

    def isMirrorEnabled(self):
        """
        :rtype: bool
        """
        return self.settings().get("mirrorEnabled", False)

    def setMirrorEnabled(self, value):
        """
        :type value: bool
        """
        self.settings().set("mirrorEnabled", value)
        self.mirrorChanged.emit(bool(value))

    def isKeyEnabled(self):
        """
        :rtype: bool
        """
        return self.settings().get("keyEnabled", False)

    def setKeyEnabled(self, value):
        """
        :type value: bool
        """
        self.settings().set("keyEnabled", value)

    def keyPressEvent(self, event):
        """
        :type event: QtGui.QEvent
        """
        transferitem.TransferItem.keyPressEvent(self, event)

        if not event.isAutoRepeat():
            if event.key() == QtCore.Qt.Key_M:

                self.toggleMirror()

                blend = self.blendValue()
                mirror = self.isMirrorEnabled()

                if self.isBlending():
                    self.loadFromSettings(
                        blend=blend,
                        mirror=mirror,
                        batchMode=True,
                        showBlendMessage=True
                    )
                else:
                    self.loadFromSettings(
                        blend=blend,
                        refresh=True,
                        mirror=mirror,
                        batchMode=False,
                    )

    def mouseReleaseEvent(self, event):
        """
        Triggered when the mouse button is released on this item.

        :type event: QtCore.QMouseEvent
        """
        if self.isBlending():
            self.loadFromSettings(blend=self.blendValue(), refresh=False)

    def doubleClicked(self):
        """
        Triggered when the user double clicks the item.

        :rtype: None
        """
        self.loadFromSettings(clearSelection=False)

    def selectionChanged(self):
        """
        Triggered when the item is selected or deselected.

        :rtype: None
        """
        self._transferObject = None
        transferitem.TransferItem.selectionChanged(self)

    def stopBlending(self):
        """
        This method is called from the base class to stop blending.

        :rtype: None
        """
        self._options = None
        transferitem.TransferItem.stopBlending(self)

    def setBlendValue(self, value, load=True):
        """
        This method is called from the base class to set the blend amount.

        :type value: float
        :rtype: None
        """
        transferitem.TransferItem.setBlendValue(self, value)

        if load:
            self.loadFromSettings(
                blend=value,
                batchMode=True,
                showBlendMessage=True
            )

    def loadFromSettings(
        self,
        blend=100.0,
        mirror=None,
        refresh=True,
        batchMode=False,
        clearSelection=True,
        showBlendMessage=False,
    ):
        """
        Load this item with the current user settings from disc.

        :type blend: float
        :type refresh: bool
        :type batchMode: bool
        :type clearSelection: bool
        :type showBlendMessage: bool
        """
        if self._options is None:
            self._options = dict()
            self._options["key"] = self.isKeyEnabled()
            self._options['mirror'] = self.isMirrorEnabled()
            self._options['namespaces'] = self.namespaces()
            self._options['mirrorTable'] = self.mirrorTable()
            self._options['objects'] = maya.cmds.ls(selection=True) or []

        if mirror is not None:
            self._options['mirror'] = mirror

        try:
            self.load(
                blend=blend,
                refresh=refresh,
                batchMode=batchMode,
                clearSelection=clearSelection,
                showBlendMessage=showBlendMessage,
                **self._options
            )
        except Exception, e:
            studioqt.MessageBox.critical(None, "Item Error", str(e))
            raise

    def load(
        self,
        objects=None,
        namespaces=None,
        blend=100.0,
        key=None,
        attrs=None,
        mirror=None,
        refresh=True,
        batchMode=False,
        mirrorTable=None,
        clearSelection=False,
        showBlendMessage=False,
    ):
        """
        :type objects: list[str]
        :type blend: float
        :type key: bool | None
        :type namespaces: list[str] | None
        :type refresh: bool | None
        :type mirror: bool | None
        :type batchMode: bool
        :type showBlendMessage: bool
        :type mirrorTable: mutils.MirrorTable
        """
        logger.info(u'Loading: {0}'.format(self.path()))

        mirror = mirror or self.isMirrorEnabled()

        # Update the blend value in case this method is called
        # without blending.
        self.setBlendValue(blend, load=False)

        if showBlendMessage and self.libraryWidget():
            self.libraryWidget().setToast("Blend: {0}%".format(blend))

        try:
            transferitem.TransferItem.load(
                self,
                objects=objects,
                namespaces=namespaces,
                key=key,
                blend=blend,
                attrs=attrs,
                mirror=mirror,
                refresh=refresh,
                batchMode=batchMode,
                mirrorTable=mirrorTable,
                clearSelection=clearSelection,
            )
        except Exception:
            self.stopBlending()
            raise

        finally:
            if not batchMode:
                self.stopBlending()

        logger.info(u'Loaded: {0}'.format(self.path()))

    def save(self, objects, path=None, iconPath=None):
        """
        Save all the given object data to the given path on disc.

        :type path: path
        :type objects: list
        :type iconPath: str
        """
        if path and not path.endswith(".pose"):
            path += ".pose"

        transferitem.TransferItem.save(self, objects, path=path, iconPath=iconPath)


class PoseCreateWidget(transferitem.CreateWidget):

    def __init__(self, item=None, parent=None):
        """"""
        item = item or PoseItem()
        transferitem.CreateWidget.__init__(self, item, parent=parent)


class PosePreviewWidget(transferitem.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :rtype: None
        """
        transferitem.PreviewWidget.__init__(self, *args, **kwargs)

        self.connect(self.ui.keyCheckBox, QtCore.SIGNAL("clicked()"), self.updateState)
        self.connect(self.ui.mirrorCheckBox, QtCore.SIGNAL("clicked()"), self.updateState)
        self.connect(self.ui.blendSlider, QtCore.SIGNAL("sliderMoved(int)"), self.sliderMoved)
        self.connect(self.ui.blendSlider, QtCore.SIGNAL("sliderReleased()"), self.sliderReleased)

        self.item().blendChanged.connect(self.updateSlider)
        self.item().mirrorChanged.connect(self.updateMirror)

    def setItem(self, item):
        """
        Set the current pose item for the preview widget.

        :type item: PoseItem
        :rtype: None
        """
        transferitem.PreviewWidget.setItem(self, item)

        # Mirror check box
        mirrorTip = "Cannot find a mirror table!"
        mirrorTable = item.mirrorTable()
        if mirrorTable:
            mirrorTip = "Using mirror table: %s" % mirrorTable.path()

        self.ui.mirrorCheckBox.setToolTip(mirrorTip)
        self.ui.mirrorCheckBox.setEnabled(mirrorTable is not None)

    def updateMirror(self, mirror):
        """
        Triggered when the user changes the mirror option for the item.

        :type mirror: bool
        """
        if mirror:
            self.ui.mirrorCheckBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.mirrorCheckBox.setCheckState(QtCore.Qt.Unchecked)

    def setState(self, state):
        """Set the current state of the widget with a dictionary."""
        key = state.get("keyEnabled", False)
        mirror = state.get("mirrorEnabled", False)

        self.ui.keyCheckBox.setChecked(key)
        self.ui.mirrorCheckBox.setChecked(mirror)

        super(PosePreviewWidget, self).setState(state)

    def state(self):
        """
        Return the current state of the widget as a dictionary.

        :rtype: dict
        """
        state = super(PosePreviewWidget, self).state()

        key = bool(self.ui.keyCheckBox.isChecked())
        mirror = bool(self.ui.mirrorCheckBox.isChecked())

        state["keyEnabled"] = key
        state["mirrorEnabled"] = mirror

        return state

    def updateSlider(self, value):
        """
        Trigger when the item changes blend value.

        :type value: int
        """
        self.ui.blendSlider.setValue(value)

    def sliderReleased(self):
        """Triggered when the user releases the slider handle."""
        blend = self.ui.blendSlider.value()
        self.item().loadFromSettings(
            blend=blend,
            refresh=False,
            showBlendMessage=True
        )

    def sliderMoved(self, value):
        """
        Triggered when the user moves the slider handle.

        :type value: float
        """
        self.item().loadFromSettings(
            blend=value,
            batchMode=True,
            showBlendMessage=True
        )

    def accept(self):
        """Triggered when the user clicks the apply button."""
        self.item().loadFromSettings(clearSelection=False)


studiolibrary.register(PoseItem, ".pose")
