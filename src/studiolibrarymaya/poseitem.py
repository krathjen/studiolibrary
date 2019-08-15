# Copyright 2019 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or modify it 
# under the terms of the GNU Lesser General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. This library is distributed in the 
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.

import os
import logging

import studiolibrary

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

from studiolibrarymaya import baseitem
from studiolibrarymaya import baseloadwidget

try:
    import mutils
    import maya.cmds
except ImportError as error:
    print(error)


logger = logging.getLogger(__name__)


def save(path, *args, **kwargs):
    """Convenience function for saving a PoseItem."""
    PoseItem(path).safeSave(*args, **kwargs)


def load(path, *args, **kwargs):
    """Convenience function for loading a PoseItem."""
    PoseItem(path).load(*args, **kwargs)


class PoseLoadWidget(baseloadwidget.BaseLoadWidget):

    def __init__(self, *args, **kwargs):
        """
        Using a custom load widget to support nicer blending.
        """
        super(PoseLoadWidget, self).__init__(*args, **kwargs)

        self.ui.blendFrame = QtWidgets.QFrame(self)

        layout = QtWidgets.QHBoxLayout(self)
        self.ui.blendFrame.setLayout(layout)

        self.ui.blendSlider = QtWidgets.QSlider(self)
        self.ui.blendSlider.setObjectName("blendSlider")
        self.ui.blendSlider.setMinimum(-30)
        self.ui.blendSlider.setMaximum(130)
        self.ui.blendSlider.setOrientation(QtCore.Qt.Horizontal)
        self.ui.blendSlider.sliderMoved.connect(self.sliderMoved)
        self.ui.blendSlider.sliderReleased.connect(self.sliderReleased)

        self.ui.blendEdit = QtWidgets.QLineEdit(self)
        self.ui.blendEdit.setObjectName("blendEdit")
        self.ui.blendEdit.setText("0")
        self.ui.blendEdit.editingFinished.connect(self._blendEditChanged)

        validator = QtGui.QIntValidator(-200, 200, self)
        self.ui.blendEdit.setValidator(validator)

        layout.addWidget(self.ui.blendSlider)
        layout.addWidget(self.ui.blendEdit)

        self.setCustomWidget(self.ui.blendFrame)

        self.item().sliderChanged.connect(self.setSliderValue)

    def selectionChanged(self):
        """Overriding to avoid validating when the selection changes."""
        if not self.item().isBatchModeEnabled():
            super(PoseLoadWidget, self).selectionChanged()

    def _blendEditChanged(self, *args):
        """Triggered when the user changes the blend edit value."""
        blend = int(self.ui.blendEdit.text())
        self.item().loadFromCurrentValues(
            blend=blend,
            batchMode=False,
            showBlendMessage=True,
            clearSelection=False,
        )

    def setSliderValue(self, value):
        """
        Trigger when the item changes blend value.

        :type value: int
        """
        self.ui.blendEdit.blockSignals(True)
        self.ui.blendSlider.setValue(value)
        self.ui.blendEdit.setText(str(int(value)))
        self.ui.blendEdit.blockSignals(False)

    def sliderReleased(self):
        """Triggered when the user releases the slider handle."""
        self.item().loadFromCurrentValues(
            blend=self.ui.blendSlider.value(),
            refresh=False,
            showBlendMessage=True
        )

    def sliderMoved(self, value):
        """
        Triggered when the user moves the slider handle.

        :type value: float
        """
        self.item().setSliderValue(value)

    def accept(self):
        """Triggered when the user clicks the apply button."""
        self.item().loadFromCurrentValues(clearSelection=False)


class PoseItem(baseitem.BaseItem):

    NAME = "Pose"
    EXTENSION = ".pose"
    ICON_PATH = os.path.join(os.path.dirname(__file__), "icons", "pose.png")
    LOAD_WIDGET_CLASS = PoseLoadWidget
    TRANSFER_CLASS = mutils.Pose
    TRANSFER_BASENAME = "pose.json"

    def __init__(self, *args, **kwargs):
        """
        Create a new instance of the pose item from the given path.

        :type path: str
        :type args: list
        :type kwargs: dict
        """
        super(PoseItem, self).__init__(*args, **kwargs)

        self._options = None
        self._batchMode = False

        self.setSliderEnabled(True)

    def isBatchModeEnabled(self):
        """
        Check if the pose is currently blending.

        :rtype: bool
        """
        return self._batchMode

    def mirrorTable(self):
        """
        Get the mirror table object for this item.

        :rtype: mutils.MirrorTable or None
        """
        mirrorTable = None

        mirrorTablePaths = list(studiolibrary.walkup(
                self.path(),
                match=lambda path: path.endswith(".mirror"),
                depth=10,
            )
        )

        if mirrorTablePaths:
            mirrorTablePath = mirrorTablePaths[0]

            path = os.path.join(mirrorTablePath, "mirrortable.json")

            if path:
                mirrorTable = mutils.MirrorTable.fromPath(path)

        return mirrorTable

    def mirrorTableSearchAndReplace(self):
        """
        Get the values for search and replace from the mirror table.

        :rtype: (str, str)
        """
        return self.mirrorTable().leftSide(), self.mirrorTable().rightSide()

    def switchSearchAndReplace(self):
        """
        Switch the values of the search and replace field.

        :rtype: (str, str)
        """
        values = self.currentLoadValue("searchAndReplace")
        return values[1], values[0]

    def clearSearchAndReplace(self):
        """
        Clear the search and replace field.

        :rtype: (str, str)
        """
        return '', ''

    def keyPressEvent(self, event):
        """
        Called when a key press event for the item is triggered.

        :type event: QtGui.QEvent
        """
        super(PoseItem, self).keyPressEvent(event)

        if not event.isAutoRepeat():
            if event.key() == QtCore.Qt.Key_M:

                # Toggle the value of the mirror option
                mirror = self.currentLoadValue("mirror")
                self.emitLoadValueChanged("mirror", not mirror)

                blend = self.sliderValue()

                if self.isSliderDown():
                    self.loadFromCurrentValues(
                        blend=blend,
                        batchMode=True,
                        showBlendMessage=True
                    )
                else:
                    self.loadFromCurrentValues(
                        blend=blend,
                        refresh=True,
                        batchMode=False,
                    )

    def mouseReleaseEvent(self, event):
        """
        Triggered when the mouse button is released on this item.

        :type event: QtCore.QMouseEvent
        """
        if self.isSliderDown():
            self.loadFromCurrentValues(blend=self.sliderValue(), refresh=False)

    def doubleClicked(self):
        """Triggered when the user double clicks the item."""
        self.loadFromCurrentValues(clearSelection=False)

    def selectionChanged(self):
        """Triggered when the item is selected or deselected."""
        self._transferObject = None
        super(PoseItem, self).selectionChanged()

    def setSliderDown(self, down):
        """This method is called from the base class to stop blending."""
        if not down:
            self._options = None
        super(PoseItem, self).setSliderDown(down)

    def setSliderValue(self, value, load=True):
        """
        This method is called from the base class to set the blend amount.

        :type value: float
        :type load: bool
        """
        super(PoseItem, self).setSliderValue(value)

        if load:
            self.loadFromCurrentValues(
                blend=value,
                batchMode=True,
                showBlendMessage=True
            )

    def loadSchema(self):
        """
        Get schema used to load the pose item.

        :rtype: list[dict]
        """
        schema = [
            {
                "name": "optionsGroup",
                "title": "Options",
                "type": "group",
                "order": 2,
            },
            {
                "name": "key",
                "type": "bool",
                "inline": True,
                "default": False,
                "persistent": True,
            },
            {
                "name": "mirror",
                "type": "bool",
                "inline": True,
                "default": False,
                "persistent": True,
            },
            {
                "name": "searchAndReplaceEnabled",
                "title": "Search and Replace",
                "type": "bool",
                "inline": True,
                "default": False,
                "persistent": True,
            },
            {
                "name": "searchAndReplace",
                "title": "",
                "type": "stringDouble",
                "default": ("", ""),
                "placeholder": ("search", "replace"),
                "persistent": True,
                "actions": [
                    {
                        "name": "Switch",
                        "callback": self.switchSearchAndReplace,
                    },
                    {
                        "name": "Clear",
                        "callback": self.clearSearchAndReplace,
                    },
                    {
                        "name": "From Mirror Table",
                        "enabled": bool(self.mirrorTable()),
                        "callback": self.mirrorTableSearchAndReplace,
                    },
                ]
            },
        ]

        schema.extend(super(PoseItem, self).loadSchema())

        return schema

    def loadValidator(self, **values):
        """
        Using the validator to change the state of the mirror option.

        :type values: dict
        :rtype: list[dict]
        """
        # Ignore the validator while blending
        if self.isBatchModeEnabled():
            return None

        # Mirror check box
        mirrorTip = "Cannot find a mirror table!"
        mirrorTable = self.mirrorTable()
        if mirrorTable:
            mirrorTip = "Using mirror table: %s" % mirrorTable.path()

        fields = [
            {
                "name": "mirror",
                "toolTip": mirrorTip,
                "enabled": mirrorTable is not None,
            },
            {
                "name": "searchAndReplace",
                "visible": values.get("searchAndReplaceEnabled")
            },
        ]

        fields.extend(super(PoseItem, self).loadValidator(**values))

        return fields

    def loadFromCurrentValues(
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
            self._options["key"] = self.currentLoadValue("key")
            # self._options['namespaces'] = self.currentLoadValue("namespaces")
            self._options['mirrorTable'] = self.mirrorTable()
            self._options['objects'] = maya.cmds.ls(selection=True) or []

        searchAndReplace = None
        if self.currentLoadValue("searchAndReplaceEnabled"):
            searchAndReplace = self.currentLoadValue("searchAndReplace")

        try:
            self.load(
                blend=blend,
                refresh=refresh,
                batchMode=batchMode,
                clearSelection=clearSelection,
                showBlendMessage=showBlendMessage,
                searchAndReplace=searchAndReplace,
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
        searchAndReplace=None,
    ):
        """
        Load the pose item to the given objects or namespaces.
        
        :type objects: list[str]
        :type blend: float
        :type key: bool
        :type namespaces: list[str] or None
        :type refresh: bool
        :type attrs: list[str] or None
        :type mirror: bool or None
        :type batchMode: bool
        :type showBlendMessage: bool
        :type clearSelection: bool
        :type mirrorTable: mutils.MirrorTable
        :type searchAndReplace: (str, str) or None
        """
        logger.debug(u'Loading: {0}'.format(self.path()))

        self._batchMode = batchMode

        # The mirror option can change during blending, so we always get
        # the value instead of caching it. This might make blending slower.
        if mirror is None:
            mirror = self.currentLoadValue("mirror")

        if namespaces is None:
            namespaces = self.currentLoadValue("namespaces")

        self.setSliderValue(blend, load=False)

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
                searchAndReplace=searchAndReplace
            )

        except Exception:
            self.setSliderDown(False)
            raise

        finally:
            if not batchMode:
                self.setSliderDown(False)

        logger.debug(u'Loaded: {0}'.format(self.path()))

    def save(self, objects, *args, **kwargs):
        """
        Save all the given object data to the item path on disc.

        :type objects: list[str]
        :type args: list
        :type kwargs: dict
        """
        super(PoseItem, self).save(objects, *args, **kwargs)

        # Save the pose to the temp location
        mutils.savePose(
            self.path() + "/pose.json",
            objects,
            metadata={"description": kwargs.get("comment", "")}
        )
