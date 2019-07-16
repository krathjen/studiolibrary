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

__all__ = [
    "BaseItem",
]

logger = logging.getLogger(__name__)



class BaseItemSignals(QtCore.QObject):
    """"""
    loadValueChanged = QtCore.Signal(object, object)


class BaseItem(studiolibrary.LibraryItem):
    _baseItemSignals = BaseItemSignals()

    loadValueChanged = _baseItemSignals.loadValueChanged

    """Base class for anim, pose, mirror and sets transfer items."""
    CreateWidgetClass = basesavewidget.BaseSaveWidget
    PreviewWidgetClass = baseloadwidget.BaseLoadWidget

    @classmethod
    def showCreateWidget(cls, libraryWindow, item=None):
        """
        Overriding this method to set the destination location
        for the create widget.

        Triggered when the user clicks the item action in the new item menu.

        :type libraryWindow: studiolibrary.LibraryWindow
        :type item: studiolibrary.LibraryItem or None

        """
        item = item or cls()
        widget = cls.CreateWidgetClass(item=item, parent=libraryWindow)

        path = libraryWindow.selectedFolderPath()

        widget.formWidget().setData("folder", {"visible": False})

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
        studiolibrary.LibraryItem.__init__(self, *args, **kwargs)

        self._currentLoadValues = {}
        self._currentLoadSchema = []
        self._currentSaveSchema = []

        self._transferClass = None
        self._transferObject = None
        self._transferBasename = None

    def emitLoadValueChanged(self, field, value):
        """
        Emit the load value changed to be validated.

        :type field: str
        :type value: object
        """
        self.loadValueChanged.emit(field, value)

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

    def currentLoadValue(self, name):
        """
        Get the current field value for the given name.

        :type name: str
        :rtype: object
        """
        return self._currentLoadValues.get(name)

    def setCurrentLoadValues(self, values):
        self._currentLoadValues = values

    def loadSchema(self):
        """
        Get schema used to load the item.

        :rtype: list[dict]
        """
        ctime = self.ctime()
        if ctime:
            ctime = studiolibrary.timeAgo(ctime)

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
                "value": ctime,
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
                "value": "From selection",
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

    def saveSchema(self):

        return [
            {
                "name": "folder",
                "type": "path",
                "layout": "vertical",
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
                "name": "contains",
                "type": "label",
                "label": {"visible": False}
            },
        ]

    def saveValidator(self, **options):

        self._currentSaveSchema = options

        selection = maya.cmds.ls(selection=True) or []

        if selection:
            count = len(selection)
            plural = "s" if count > 1 else ""

            msg = "{0} object{1} selected for saving"
            msg = msg.format(str(count), plural)
        else:
            msg = "Nothing selected for saving"

        return [
            {
                "name": "contains",
                "value": msg
            },
        ]

    def write(self, path, objects, iconPath="", **options):
        """
        Write all the given object data to the given path on disc.

        :type path: str
        :type objects: list[str]
        :type iconPath: str
        :type options: dict
        """
        # Copy the icon path to the given path
        if iconPath:
            basename = os.path.basename(iconPath)
            shutil.copyfile(iconPath, path + "/" + basename)

    def currentLoadSchema(self):
        """
        Get the current options set by the user.

        :rtype: dict
        """
        return self._currentLoadSchema

    def defaultOptions(self):
        """
        Triggered when the user changes the options.

        :rtype: dict
        """
        options = {}

        for option in self.loadSchema():
            options[option.get('name')] = option.get('default')

        return options

    def setTransferClass(self, classname):
        """
        Set the transfer class used to read and write the data.

        :type classname: mutils.TransferObject
        """
        self._transferClass = classname

    def transferClass(self):
        """
        Return the transfer class used to read and write the data.

        :rtype: mutils.TransferObject
        """
        return self._transferClass

    def transferPath(self):
        """
        Return the disc location to transfer path.

        :rtype: str
        """
        if self.transferBasename():
            return os.path.join(self.path(), self.transferBasename())
        else:
            return self.path()

    def transferBasename(self):
        """
        Return the filename of the transfer path.

        :rtype: str
        """
        return self._transferBasename

    def setTransferBasename(self, transferBasename):
        """
        Set the filename of the transfer path.

        :type: str
        """
        self._transferBasename = transferBasename

    def transferObject(self):
        """
        Return the transfer object used to read and write the data.

        :rtype: mutils.TransferObject
        """
        if not self._transferObject:
            path = self.transferPath()
            self._transferObject = self.transferClass().fromPath(path)
        return self._transferObject

    def contextMenu(self, menu, items=None):
        """
        This method is called when the user right clicks on this item.

        :type menu: QtWidgets.QMenu
        :type items: list[BaseItem]
        :rtype: None
        """
        import setsmenu

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
        Return a new instance of the selection sets menu.

        :type parent: QtWidgets.QWidget
        :type enableSelectContent: bool
        :rtype: QtWidgets.QMenu
        """
        import setsmenu

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

    def mirrorTable(self):
        """
        Return the mirror table object for this item.

        :rtype: mutils.MirrorTable or None
        """
        mirrorTable = None

        mirrorTablePath = self.mirrorTablePath()

        if mirrorTablePath:

            path = os.path.join(mirrorTablePath, "mirrortable.json")

            if path:
                mirrorTable = mutils.MirrorTable.fromPath(path)

        return mirrorTable

    def mirrorTablePath(self):
        """
        Return the mirror table path for this item.

        :rtype: str or None
        """
        path = None
        paths = self.mirrorTablePaths()

        if paths:
            path = paths[0]

        return path

    def mirrorTablePaths(self):
        """
        Return all mirror table paths for this item.

        :rtype: list[str]
        """
        paths = list(studiolibrary.walkup(
                self.path(),
                match=lambda path: path.endswith(".mirror"),
                depth=10,
            )
        )
        return paths

    def namespaces(self):
        """
        Return the namesapces for this item depending on the namespace option.

        :rtype: list[str]
        """
        return self.currentLoadValue("namespaces")

    def namespaceOption(self):
        """
        Return the namespace option for this item.

        :rtype: NamespaceOption
        """
        return self.currentLoadValue("namespaceOption")

    def doubleClicked(self):
        """
        This method is called when the user double clicks the item.

        :rtype: None
        """
        self.loadFromCurrentOptions()

    def loadFromCurrentOptions(self):
        """Load the mirror table using the settings for this item."""
        kwargs = self._currentLoadValues
        objects = maya.cmds.ls(selection=True) or []

        try:
            self.load(
                objects=objects,
                **kwargs
            )
        except Exception as error:
            self.showErrorDialog("Item Error", str(error))
            raise

    def load(self, objects=None, **kwargs):
        """
        Load the data from the transfer object.

        # :type namespaces: list[str] or None
        :type objects: list[str] or None
        :rtype: None
        """
        logger.debug(u'Loading: {0}'.format(self.transferPath()))

        self.transferObject().load(objects=objects, **kwargs)

        logger.debug(u'Loading: {0}'.format(self.transferPath()))
