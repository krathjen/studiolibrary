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

import logging

from studioqt import QtCore

import studiolibrary
import studiolibrarymaya

from studiolibrarymaya import baseitem
from studiolibrarymaya import basecreatewidget
from studiolibrarymaya import basepreviewwidget

try:
    import mutils
    import maya.cmds
except ImportError as error:
    print(error)


__all__ = [
    "PoseItem",
    "PoseCreateWidget",
    "PosePreviewWidget"
]


logger = logging.getLogger(__name__)


class PoseItemSignals(QtCore.QObject):
    """Signals need to be attached to a QObject"""
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

        self.setBlendingEnabled(True)
        self.setTransferClass(mutils.Pose)
        self.setTransferBasename("pose.json")

    def isLoading(self):
        """
        Return True if the item is loading.
        
        :rtype: bool
        """
        return self._isLoading

    def toggleMirror(self):
        """
        Toggle the mirror setting.
        
        :rtype: None
        """
        mirror = self.isMirrorEnabled()
        mirror = False if mirror else True
        self.setMirrorEnabled(mirror)

    def isMirrorEnabled(self):
        """
        Return True if the mirror setting is enabled.
        
        :rtype: bool
        """
        return self.settings().get("mirrorEnabled")

    def setMirrorEnabled(self, value):
        """
        Set the user mirror setting.
        
        :type value: bool
        """
        logger.info("Set mirror enabled: %s", value)
        self.settings()["mirrorEnabled"] = value
        self.mirrorChanged.emit(bool(value))

    def isKeyEnabled(self):
        """
        Return True if the pose should be keyed after loading.
        
        :rtype: bool
        """
        return self.settings().get("keyEnabled")

    def setKeyEnabled(self, value):
        """
        if enabled, key the objects after the pose item has been loaded.
        
        :type value: bool
        """
        logger.info("Set key enabled: %s", value)
        self.settings()["keyEnabled"] = value

    def keyPressEvent(self, event):
        """
        Called when a key press event for the item is triggered.
        
        :type event: QtGui.QEvent
        """
        super(PoseItem, self).keyPressEvent(event)

        if not event.isAutoRepeat():
            if event.key() == QtCore.Qt.Key_M:

                self.toggleMirror()

                blend = self.blendValue()

                if self.isBlending():
                    self.loadFromSettings(
                        blend=blend,
                        batchMode=True,
                        showBlendMessage=True
                    )
                else:
                    self.loadFromSettings(
                        blend=blend,
                        refresh=True,
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
        :type load: bool
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
        refresh=True,
        batchMode=False,
        clearSelection=True,
        showBlendMessage=False,
    ):
        """
        Load the pose item with the current user settings from disc.

        :type blend: float
        :type refresh: bool
        :type batchMode: bool
        :type clearSelection: bool
        :type showBlendMessage: bool
        """
        if self._options is None:
            self._options = dict()
            self._options["key"] = self.isKeyEnabled()
            self._options['namespaces'] = self.namespaces()
            self._options['mirrorTable'] = self.mirrorTable()
            self._options['objects'] = maya.cmds.ls(selection=True) or []

        try:
            self.load(
                blend=blend,
                refresh=refresh,
                batchMode=batchMode,
                clearSelection=clearSelection,
                showBlendMessage=showBlendMessage,
                **self._options
            )
        except Exception as error:
            self.showErrorDialog("Item Error", str(error))
            raise

    def load(
        self,
        objects=None,
        namespaces=None,
        blend=100.0,
        key=False,
        attrs=None,
        mirror=None,
        refresh=True,
        batchMode=False,
        mirrorTable=None,
        clearSelection=False,
        showBlendMessage=False,
    ):
        """
        Load the pose item to the given objects or namespaces.
        
        :type objects: list[str]
        :type blend: float
        :type key: bool
        :type namespaces: list[str] | None
        :type refresh: bool
        :type mirror: bool or None
        :type batchMode: bool
        :type showBlendMessage: bool
        :type clearSelection: bool
        :type mirrorTable: mutils.MirrorTable
        """
        logger.debug(u'Loading: {0}'.format(self.path()))

        # The mirror option can change during blending, so we always get
        # the value instead of caching it. This might make blending slower.
        if mirror is None:
            mirror = self.isMirrorEnabled()

        self.setBlendValue(blend, load=False)

        if showBlendMessage:
            self.showToastMessage("Blend: {0}%".format(blend))

        try:
            self.transferObject().load(
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

        logger.debug(u'Loaded: {0}'.format(self.path()))

    def save(self, objects, path="", iconPath="", metadata=None, **kwargs):
        """
        Save all the given object data to the given path on disc.

        :type objects: list[str]
        :type path: str
        :type iconPath: str
        :type metadata: None or dict
        """
        if path and not path.endswith(".pose"):
            path += ".pose"

        logger.info(u'Saving: {0}'.format(path))

        # Remove and create a new temp directory
        tempPath = mutils.createTempPath() + "/" + self.transferBasename()

        # Save the pose to the temp location
        mutils.savePose(
            tempPath,
            objects,
            metadata=metadata
        )

        # Move the mirror table to the given path using the base class
        contents = [tempPath, iconPath]
        super(PoseItem, self).save(path, contents=contents, **kwargs)

        logger.info(u'Saved: {0}'.format(path))


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

        self.ui.keyCheckBox.clicked.connect(self.saveSettings)
        self.ui.mirrorCheckBox.clicked.connect(self.saveSettings)
        self.ui.blendSlider.sliderMoved.connect(self.sliderMoved)
        self.ui.blendSlider.sliderReleased.connect(self.sliderReleased)

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
PoseItem.MenuOrder = 4
PoseItem.MenuIconPath = iconPath
PoseItem.TypeIconPath = iconPath
PoseItem.CreateWidgetClass = PoseCreateWidget
PoseItem.PreviewWidgetClass = PosePreviewWidget

studiolibrary.registerItem(PoseItem)
