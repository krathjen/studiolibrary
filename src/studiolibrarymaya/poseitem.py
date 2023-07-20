# Copyright 2020 by Kurt Rathjen. All Rights Reserved.
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


class PoseLoadWidget(baseloadwidget.BaseLoadWidget):

    @classmethod
    def createFromPath(cls, path, theme=None):

        item = PoseItem(path)
        widget = cls(item)

        if not theme:
            import studiolibrary.widgets
            theme = studiolibrary.widgets.Theme()
            widget.setStyleSheet(theme.styleSheet())

        widget.show()

    def __init__(self, *args, **kwargs):
        super(PoseLoadWidget, self).__init__(*args, **kwargs)

        self._options = None
        self._pose = mutils.Pose.fromPath(self.item().transferPath())

        self.ui.blendFrame = QtWidgets.QFrame(self)

        layout = QtWidgets.QHBoxLayout(self)
        self.ui.blendFrame.setLayout(layout)

        if self.item().libraryWindow():
            self.item().libraryWindow().itemsWidget().itemSliderMoved.connect(self._sliderMoved)
            self.item().libraryWindow().itemsWidget().itemSliderReleased.connect(self._sliderReleased)
            self.item().libraryWindow().itemsWidget().itemDoubleClicked.connect(self._itemDoubleClicked)

        self.ui.blendSlider = QtWidgets.QSlider(self)
        self.ui.blendSlider.setObjectName("blendSlider")
        self.ui.blendSlider.setMinimum(-30)
        self.ui.blendSlider.setMaximum(130)
        self.ui.blendSlider.setOrientation(QtCore.Qt.Horizontal)
        self.ui.blendSlider.sliderMoved.connect(self._sliderMoved)
        self.ui.blendSlider.sliderReleased.connect(self._sliderReleased)

        self.ui.blendEdit = QtWidgets.QLineEdit(self)
        self.ui.blendEdit.setObjectName("blendEdit")
        self.ui.blendEdit.setText("0")
        self.ui.blendEdit.editingFinished.connect(self._blendEditChanged)

        validator = QtGui.QIntValidator(-200, 200, self)
        self.ui.blendEdit.setValidator(validator)

        layout.addWidget(self.ui.blendSlider)
        layout.addWidget(self.ui.blendEdit)

        self.setCustomWidget(self.ui.blendFrame)

    def _itemDoubleClicked(self):
        """Triggered when the user double-clicks a pose."""
        self.accept()

    def _sliderMoved(self, value):
        """Triggered when the user moves the slider handle."""
        self.load(blend=value, batchMode=True)

    def _sliderReleased(self):
        """Triggered when the user releases the slider handle."""
        try:
            self.load(blend=self.ui.blendSlider.value(), refresh=False)
            self._options = {}
        except Exception as error:
            self.item().showErrorDialog("Item Error", str(error))
            raise

    def _blendEditChanged(self, *args):
        """Triggered when the user changes the blend edit value."""
        try:
            self._options = {}
            self.load(blend=int(self.ui.blendEdit.text()), clearSelection=False)
        except Exception as error:
            self.item().showErrorDialog("Item Error", str(error))
            raise

    def loadValidator(self, *args, **kwargs):
        self._options = {}
        return super(PoseLoadWidget, self).loadValidator(*args, **kwargs)

    def accept(self):
        """Triggered when the user clicks the apply button."""
        try:
            self._options = {}
            self.load(clearCache=True,  clearSelection=False)
        except Exception as error:
            self.item().showErrorDialog("Item Error", str(error))
            raise

    def load(
        self,
        blend=100.0,
        refresh=True,
        batchMode=False,
        clearCache=False,
        clearSelection=True,
    ):
        """
        Load the pose item with the current user settings from disc.

        :type blend: float
        :type refresh: bool
        :type batchMode: bool
        :type clearCache: bool
        :type clearSelection: bool
        """
        if batchMode:
            self.formWidget().setValidatorEnabled(False)
        else:
            self.formWidget().setValidatorEnabled(True)

        if not self._options:

            self._options = self.formWidget().values()
            self._options['mirrorTable'] = self.item().mirrorTable()
            self._options['objects'] = maya.cmds.ls(selection=True) or []

            if not self._options["searchAndReplaceEnabled"]:
                self._options["searchAndReplace"] = None

            del self._options["namespaceOption"]
            del self._options["searchAndReplaceEnabled"]

        self.ui.blendEdit.blockSignals(True)
        self.ui.blendSlider.setValue(blend)
        self.ui.blendEdit.setText(str(int(blend)))
        self.ui.blendEdit.blockSignals(False)

        if self.item().libraryWindow():

            self.item().libraryWindow().itemsWidget().blockSignals(True)
            self.item().setSliderValue(blend)
            self.item().libraryWindow().itemsWidget().blockSignals(False)

            if batchMode:
                self.item().libraryWindow().showToastMessage("Blend: {0}%".format(blend))

        try:
            self._pose.load(
                blend=blend,
                refresh=refresh,
                batchMode=batchMode,
                clearCache=clearCache,
                clearSelection=clearSelection,
                **self._options
            )
        finally:
            self.item().setSliderDown(batchMode)


def findMirrorTable(path):
    """
    Get the mirror table object for this item.

    :rtype: mutils.MirrorTable or None
    """
    mirrorTable = None

    mirrorTablePaths = list(studiolibrary.walkup(
            path,
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

        self.setSliderEnabled(True)

    def mirrorTableSearchAndReplace(self):
        """
        Get the values for search and replace from the mirror table.

        :rtype: (str, str)
        """
        mirrorTable = findMirrorTable(self.path())

        return mirrorTable.leftSide(), mirrorTable.rightSide()

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

    def doubleClicked(self):
        """Triggered when the user double-click the item."""
        pass

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
                "name": "additive",
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
                        "enabled": bool(findMirrorTable(self.path())),
                        "callback": self.mirrorTableSearchAndReplace,
                    },
                ]
            },
        ]

        schema.extend(super(PoseItem, self).loadSchema())

        return schema
    
    def mirrorTable(self):
        return findMirrorTable(self.path())

    def loadValidator(self, **values):
        """
        Using the validator to change the state of the mirror option.

        :type values: dict
        :rtype: list[dict]
        """
        # Mirror check box
        mirrorTip = "Cannot find a mirror table!"
        mirrorTable = findMirrorTable(self.path())
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

    def save(self, objects, **kwargs):
        """
        Save all the given object data to the item path on disc.

        :type objects: list[str]
        :type kwargs: dict
        """
        super(PoseItem, self).save(**kwargs)

        # Save the pose to the temp location
        mutils.savePose(
            self.transferPath(),
            objects,
            metadata={"description": kwargs.get("comment", "")}
        )
