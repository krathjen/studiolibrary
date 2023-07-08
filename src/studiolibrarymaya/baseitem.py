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
import shutil
import logging

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore

import studiolibrary

from studiolibrarymaya import basesavewidget
from studiolibrarymaya import baseloadwidget

try:
    import mutils
    import mutils.gui
    import maya.cmds
except ImportError as error:
    print(error)


logger = logging.getLogger(__name__)


class BaseItemSignals(QtCore.QObject):
    """"""
    loadValueChanged = QtCore.Signal(object, object)


class BaseItem(studiolibrary.LibraryItem):

    _baseItemSignals = BaseItemSignals()

    loadValueChanged = _baseItemSignals.loadValueChanged

    """Base class for anim, pose, mirror and sets transfer items."""
    SAVE_WIDGET_CLASS = basesavewidget.BaseSaveWidget
    LOAD_WIDGET_CLASS = baseloadwidget.BaseLoadWidget

    TRANSFER_CLASS = None
    TRANSFER_BASENAME = ""

    def createLoadWidget(self, parent=None):
        widget = self.LOAD_WIDGET_CLASS(item=self, parent=parent)
        return widget

    @classmethod
    def createSaveWidget(cls, parent=None, item=None):
        item = item or cls()
        widget = cls.SAVE_WIDGET_CLASS(item=item, parent=parent)
        return widget

    @classmethod
    def showSaveWidget(cls, libraryWindow=None, item=None):
        """
        Overriding this method to set the destination location
        for the save widget.

        Triggered when the user clicks the item action in the new item menu.

        :type libraryWindow: studiolibrary.LibraryWindow
        :type item: studiolibrary.LibraryItem or None
        """
        item = item or cls()
        widget = cls.SAVE_WIDGET_CLASS(item=item, parent=libraryWindow)

        if libraryWindow:
            path = libraryWindow.selectedFolderPath()

            widget.setFolderPath(path)
            widget.setLibraryWindow(libraryWindow)

            libraryWindow.setCreateWidget(widget)
            libraryWindow.folderSelectionChanged.connect(widget.setFolderPath)

    def __init__(self, *args, **kwargs):
        """
        Initialise a new instance for the given path.

        :type path: str
        :type args: list
        :type kwargs: dict
        """
        self._transferObject = None
        self._currentLoadValues = {}

        studiolibrary.LibraryItem.__init__(self, *args, **kwargs)

    def emitLoadValueChanged(self, field, value):
        """
        Emit the load value changed to be validated.

        :type field: str
        :type value: object
        """
        self.loadValueChanged.emit(field, value)

    def namespaces(self):
        """
        Return the namesapces for this item depending on the namespace option.

        :rtype: list[str] or None
        """
        return self.currentLoadValue("namespaces")

    def namespaceOption(self):
        """
        Return the namespace option for this item.

        :rtype: NamespaceOption or None
        """
        return self.currentLoadValue("namespaceOption")

    def doubleClicked(self):
        """
        This method is called when the user double clicks the item.

        :rtype: None
        """
        self.loadFromCurrentValues()

    def transferPath(self):
        """
        Return the disc location to transfer path.

        :rtype: str
        """
        if self.TRANSFER_BASENAME:
            return os.path.join(self.path(), self.TRANSFER_BASENAME)
        else:
            return self.path()

    def transferObject(self):
        """
        Return the transfer object used to read and write the data.

        :rtype: mutils.TransferObject
        """
        if not self._transferObject:
            path = self.transferPath()
            self._transferObject = self.TRANSFER_CLASS.fromPath(path)
        return self._transferObject

    def currentLoadValue(self, name):
        """
        Get the current field value for the given name.

        :type name: str
        :rtype: object
        """
        return self._currentLoadValues.get(name)

    def setCurrentLoadValues(self, values):
        """
        Set the current field values for the the item.

        :type values: dict
        """
        self._currentLoadValues = values

    def loadFromCurrentValues(self):
        """Load the mirror table using the settings for this item."""
        kwargs = self._currentLoadValues
        objects = maya.cmds.ls(selection=True) or []

        try:
            self.load(objects=objects, **kwargs)
        except Exception as error:
            self.showErrorDialog("Item Error", str(error))
            raise

    def contextMenu(self, menu, items=None):
        """
        This method is called when the user right clicks on this item.

        :type menu: QtWidgets.QMenu
        :type items: list[BaseItem]
        :rtype: None
        """
        from studiolibrarymaya import setsmenu

        action = setsmenu.selectContentAction(self, parent=menu)
        menu.addAction(action)
        menu.addSeparator()

        subMenu = self.createSelectionSetsMenu(menu, enableSelectContent=False)
        menu.addMenu(subMenu)
        menu.addSeparator()

        studiolibrary.LibraryItem.contextMenu(self, menu, items=items)

    def showSelectionSetsMenu(self, **kwargs):
        """
        Show the selection sets menu for this item at the cursor position.

        :rtype: QtWidgets.QAction
        """
        menu = self.createSelectionSetsMenu(**kwargs)
        position = QtGui.QCursor().pos()
        action = menu.exec_(position)
        return action

    def createSelectionSetsMenu(self, parent=None, enableSelectContent=True):
        """
        Get a new instance of the selection sets menu.

        :type parent: QtWidgets.QWidget
        :type enableSelectContent: bool
        :rtype: QtWidgets.QMenu
        """
        from . import setsmenu

        parent = parent or self.libraryWindow()

        namespaces = self.namespaces()

        menu = setsmenu.SetsMenu(
            item=self,
            parent=parent,
            namespaces=namespaces,
            enableSelectContent=enableSelectContent,
        )

        return menu

    def selectContent(self, namespaces=None, **kwargs):
        """
        Select the contents of this item in the Maya scene.

        :type namespaces: list[str]
        """
        namespaces = namespaces or self.namespaces()

        kwargs = kwargs or mutils.selectionModifiers()

        msg = "Select content: Item.selectContent(namespacea={0}, kwargs={1})"
        msg = msg.format(namespaces, kwargs)
        logger.debug(msg)

        try:
            self.transferObject().select(namespaces=namespaces, **kwargs)
        except Exception as error:
            self.showErrorDialog("Item Error", str(error))
            raise

    def loadSchema(self):
        """
        Get schema used to load the item.

        :rtype: list[dict]
        """
        modified = self.itemData().get("modified")
        if modified:
            modified = studiolibrary.timeAgo(modified)

        count = self.transferObject().objectCount()
        plural = "s" if count > 1 else ""
        contains = str(count) + " Object" + plural

        return [
            {
                "name": "infoGroup",
                "title": "Info",
                "type": "group",
                "order": 1,
            },
            {
                "name": "name",
                "value": self.name(),
            },
            {
                "name": "owner",
                "value": self.transferObject().owner(),
            },
            {
                "name": "created",
                "value": modified,
            },
            {
                "name": "contains",
                "value": contains,
            },
            {
                "name": "comment",
                "value": self.transferObject().description() or "No comment",
            },
            {
                "name": "namespaceGroup",
                "title": "Namespace",
                "type": "group",
                "order": 10,
            },
            {
                "name": "namespaceOption",
                "title": "",
                "type": "radio",
                "value": "From file",
                "items": ["From file", "From selection", "Use custom"],
                "persistent": True,
                "persistentKey": "BaseItem",
            },
            {
                "name": "namespaces",
                "title": "",
                "type": "tags",
                "value": [],
                "items": mutils.namespace.getAll(),
                "persistent": True,
                "label": {"visible": False},
                "persistentKey": "BaseItem",
            },
        ]

    def loadValidator(self, **values):
        """
        Called when the load fields change.

        :type values: dict
        """
        namespaces = values.get("namespaces")
        namespaceOption = values.get("namespaceOption")

        if namespaceOption == "From file":
            namespaces = self.transferObject().namespaces()
        elif namespaceOption == "From selection":
            namespaces = mutils.namespace.getFromSelection()

        fieldChanged = values.get("fieldChanged")
        if fieldChanged == "namespaces":
            values["namespaceOption"] = "Use custom"
        else:
            values["namespaces"] = namespaces

        self._currentLoadValues = values

        return [
            {
                "name": "namespaces",
                "value": values.get("namespaces"),
            },
            {
                "name": "namespaceOption",
                "value": values.get("namespaceOption"),
            },
        ]

    def load(self, **kwargs):
        """
        Load the data from the transfer object.

        :rtype: None
        """
        logger.debug(u'Loading: {0}'.format(self.transferPath()))

        self.transferObject().load(**kwargs)

        logger.debug(u'Loading: {0}'.format(self.transferPath()))

    def saveSchema(self):
        """
        The base save schema.

        :rtype: list[dict]
        """
        return [
            {
                "name": "folder",
                "type": "path",
                "layout": "vertical",
                "visible": False,
            },
            {
                "name": "name",
                "type": "string",
                "layout": "vertical",
            },
            {
                "name": "comment",
                "type": "text",
                "layout": "vertical"
            },
            {
                "name": "objects",
                "type": "objects",
                "label": {"visible": False}
            },
        ]

    def saveValidator(self, **kwargs):
        """
        The save validator is called when an input field has changed.

        :type kwargs: dict
        :rtype: list[dict]
        """
        fields = []

        if not kwargs.get("folder"):
            fields.append({
                "name": "folder",
                "error": "No folder selected. Please select a destination folder.",
            })

        if not kwargs.get("name"):
            fields.append({
                "name": "name",
                "error": "No name specified. Please set a name before saving.",
            })

        selection = maya.cmds.ls(selection=True) or []
        msg = ""
        if not selection:
            msg = "No objects selected. Please select at least one object."

        fields.append({
                "name": "objects",
                "value": selection,
                "error": msg,
            },
        )

        return fields

    def save(self, thumbnail="", **kwargs):
        """
        Save all the given object data to the item path on disc.

        :type thumbnail: str
        :type kwargs: dict
        """
        # Copy the icon path to the given path
        if thumbnail:
            basename = os.path.basename(thumbnail)
            shutil.copyfile(thumbnail, self.path() + "/" + basename)
