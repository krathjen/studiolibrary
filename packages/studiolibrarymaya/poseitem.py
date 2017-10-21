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

from studiolibrarymaya import poseitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.pose"
objects = maya.cmds.ls(selection=True) or []

item = poseitem.PoseItem(path)
item.save(objects=objects)

#---------------------------------------------------------------------------
# Loading a pose item
#---------------------------------------------------------------------------

from studiolibrarymaya import poseitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.pose"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

item = poseitem.PoseItem(path)
item.load(objects=objects, namespaces=namespaces, key=True, mirror=False)
"""

import os
import logging

import studioqt

from studioqt import QtCore

import studiolibrary
import studiolibrarymaya

from studiolibrarymaya import baseitem
from studiolibrarymaya import basecreatewidget
from studiolibrarymaya import basepreviewwidget

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


class PoseItem(baseitem.BaseItem):

    _poseItemSignals = PoseItemSignals()
    mirrorChanged = _poseItemSignals.mirrorChanged

    def __init__(self, *args, **kwargs):
        """
        Create a new instance of the pose item from the given path.

        :type path: str
        :type args: list
        :type kwargs: dict
        """
        super(PoseItem, self).__init__(*args, **kwargs)

        self._options = None
        self._isLoading = False
        self._autoKeyFrame = None

        self.setBlendingEnabled(True)
        self.setTransferClass(mutils.Pose)
        self.setTransferBasename("pose.json")

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
        return self.settings().get("mirrorEnabled")

    def setMirrorEnabled(self, value):
        """
        :type value: bool
        """
        self.settings()["mirrorEnabled"] = value
        self.mirrorChanged.emit(bool(value))

    def isKeyEnabled(self):
        """
        :rtype: bool
        """
        return self.settings().get("keyEnabled")

    def setKeyEnabled(self, value):
        """
        :type value: bool
        """
        self.settings()["keyEnabled"] = value

    def keyPressEvent(self, event):
        """
        :type event: QtGui.QEvent
        """
        super(PoseItem, self).keyPressEvent(event)

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
        baseitem.BaseItem.selectionChanged(self)

    def stopBlending(self):
        """
        This method is called from the base class to stop blending.

        :rtype: None
        """
        self._options = None
        baseitem.BaseItem.stopBlending(self)

    def setBlendValue(self, value, load=True):
        """
        This method is called from the base class to set the blend amount.

        :type value: float
        :rtype: None
        """
        super(PoseItem, self).setBlendValue(value)

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
            self.showErrorDialog("Item Error", str(e))
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

        if showBlendMessage:
            self.showToastMessage("Blend: {0}%".format(blend))

        try:
            baseitem.BaseItem.load(
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

    def save(self, objects, path="", iconPath="", **kwargs):
        """
        Save all the given object data to the given path on disc.

        :type objects: list[str]
        :type path: str
        :type iconPath: str
        """
        if path and not path.endswith(".pose"):
            path += ".pose"

        super(PoseItem, self).save(objects, path=path, iconPath=iconPath, **kwargs)


class PoseCreateWidget(basecreatewidget.BaseCreateWidget):

    def __init__(self, item=None, parent=None):
        """"""
        item = item or PoseItem()
        super(PoseCreateWidget, self).__init__(item, parent=parent)


class PosePreviewWidget(basepreviewwidget.BasePreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :rtype: None
        """
        super(PosePreviewWidget, self).__init__(*args, **kwargs)

        self.connect(self.ui.keyCheckBox, QtCore.SIGNAL("clicked()"), self.saveSettings)
        self.connect(self.ui.mirrorCheckBox, QtCore.SIGNAL("clicked()"), self.saveSettings)
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
        super(PosePreviewWidget, self).setItem(item)

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

    def setSettings(self, settings):
        """Set the current state of the widget with a dictionary."""
        key = settings.get("keyEnabled")
        mirror = settings.get("mirrorEnabled")

        self.ui.keyCheckBox.setChecked(key)
        self.ui.mirrorCheckBox.setChecked(mirror)

        super(PosePreviewWidget, self).setSettings(settings)

    def settings(self):
        """
        Return the current state of the widget as a dictionary.

        :rtype: dict
        """
        settings = super(PosePreviewWidget, self).settings()

        key = bool(self.ui.keyCheckBox.isChecked())
        mirror = bool(self.ui.mirrorCheckBox.isChecked())

        settings["keyEnabled"] = key
        settings["mirrorEnabled"] = mirror

        return settings

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


# Register the pose item to the Studio Library
iconPath = studiolibrarymaya.resource().get("icons", "pose.png")

PoseItem.Extensions = [".pose"]
PoseItem.MenuName = "Pose"
PoseItem.MenuIconPath = iconPath
PoseItem.TypeIconPath = iconPath
PoseItem.CreateWidgetClass = PoseCreateWidget
PoseItem.PreviewWidgetClass = PosePreviewWidget

studiolibrary.registerItem(PoseItem)
