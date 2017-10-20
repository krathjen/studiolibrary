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

import os
import logging

from studioqt import QtGui

import studioqt
import studiolibrary
import studiolibrarymaya

try:
    import mutils
    import mutils.gui
    import maya.cmds
except ImportError, e:
    print e


__all__ = [
    "BaseItem",
]

logger = logging.getLogger(__name__)


class NamespaceOption:
    FromFile = "file"
    FromCustom = "custom"
    FromSelection = "selection"


class BaseItem(studiolibrary.LibraryItem):

    """Base class for anim, pose, mirror and sets transfer items."""

    @classmethod
    def showCreateWidget(cls, libraryWidget):
        """
        Overriding this method to set the destination location
        for the create widget.

        Triggered when the user clicks the item action in the new item menu.

        :type libraryWidget: studiolibrary.LibraryWidget
        """
        widget = cls.CreateWidgetClass()

        path = libraryWidget.selectedFolderPath()

        if path:
            widget.folderFrame().hide()
        else:
            path = libraryWidget.path()

        widget.setFolderPath(path)
        widget.setLibraryWidget(libraryWidget)

        libraryWidget.setCreateWidget(widget)
        libraryWidget.folderSelectionChanged.connect(widget.setFolderPath)

    def __init__(self, *args, **kwargs):
        """
        Initialise a new instance for the given path.

        :type path: str
        :type args: list
        :type kwargs: dict
        """
        studiolibrary.LibraryItem.__init__(self, *args, **kwargs)

        self._namespaces = []
        self._namespaceOption = NamespaceOption.FromSelection

        self._transferClass = None
        self._transferObject = None
        self._transferBasename = None

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

    def thumbnailPath(self):
        """
        Return the thumbnail location on disc to be displayed for the item.

        :rtype: str
        """
        return self.path() + "/thumbnail.jpg"

    def settings(self):
        """
        Return a settings object for saving data to the users local disc.

        :rtype: studiolibrary.Settings
        """
        return studiolibrarymaya.settings()

    def owner(self):
        """
        Return the user who created this item.

        :rtype: str or None
        """
        return self.transferObject().metadata().get("user", "")

    def description(self):
        """
        Return the user description for this item.

        :rtype: str
        """
        return self.transferObject().metadata().get("description", "")

    def objectCount(self):
        """
        Return the number of controls this item contains.

        :rtype: int
        """
        return self.transferObject().count()

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

        parent = parent or self.libraryWidget()

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
        except Exception, e:
            self.showErrorDialog("Item Error", str(e))
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
        paths = list(studiolibrary.findPaths(
                self.path(),
                match=lambda path: path.endswith(".mirror"),
                direction=studiolibrary.Direction.Up,
                depth=10,
            )
        )
        return paths

    def namespaces(self):
        """
        Return the namesapces for this item depending on the namespace option.

        :rtype: list[str]
        """
        namespaces = []
        namespaceOption = self.namespaceOption()

        # # When creating a new item we can only get the namespaces from
        # # selection because the file (transferObject) doesn't exist yet.
        if not self.exists():
            namespaces = self.namespacesFromSelection()

        # If the file (transferObject) exists then we can use the namespace
        # option to determined which namespaces to return.
        if namespaceOption == NamespaceOption.FromFile:
            namespaces = self.namespacesFromFile()

        elif namespaceOption == NamespaceOption.FromCustom:
            namespaces = self.namespacesFromCustom()

        elif namespaceOption == NamespaceOption.FromSelection:
            namespaces = self.namespacesFromSelection()

        return namespaces

    def setNamespaceOption(self, namespaceOption):
        """
        Set the namespace option for this item.

        :type namespaceOption: NamespaceOption
        :rtype: None
        """
        self.settings()["namespaceOption"] = namespaceOption

    def namespaceOption(self):
        """
        Return the namespace option for this item.

        :rtype: NamespaceOption
        """
        namespaceOption = self.settings().get(
                "namespaceOption",
                NamespaceOption.FromSelection
        )
        return namespaceOption

    def namespacesFromCustom(self):
        """
        Return the namespace the user has set.

        :rtype: list[str]
        """
        return self.settings().get("namespaces", [])

    def setCustomNamespaces(self, namespaces):
        """
        Set the users custom namespace.

        :type namespaces: list[str]
        :rtype: None
        """
        self.settings()["namespaces"] = namespaces

    def namespacesFromFile(self):
        """
        Return the namespaces from the transfer data.

        :rtype: list[str]
        """
        return self.transferObject().namespaces()

    @staticmethod
    def namespacesFromSelection():
        """
        Return the current namespaces from the selected objects in Maya.

        :rtype: list[str]
        """
        namespaces = [""]

        try:
            namespaces = mutils.namespace.getFromSelection() or namespaces
        except NameError, e:
            # Catch any errors when running this command outside of Maya
            logger.exception(e)

        return namespaces

    def doubleClicked(self):
        """
        This method is called when the user double clicks the item.

        :rtype: None
        """
        self.load()

    def load(self, objects=None, namespaces=None, **kwargs):
        """
        Load the data from the transfer object.

        :type namespaces: list[str] or None
        :type objects: list[str] or None
        :rtype: None
        """
        logger.debug(u'Loading: {0}'.format(self.transferPath()))

        self.transferObject().load(objects=objects, namespaces=namespaces, **kwargs)

        logger.debug(u'Loading: {0}'.format(self.transferPath()))

    def save(
            self,
            objects,
            path="",
            iconPath="",
            contents=None,
            description="",
            **kwargs
    ):
        """
        Save the data to the transfer path on disc.

        :type objects: list[str]
        :type path: str
        :type iconPath: str
        :type contents: list[str] or None
        :type description: str

        :rtype: None
        """
        logger.info(u'Saving: {0}'.format(path))

        tempDir = mutils.TempDir("Transfer", clean=True)
        tempPath = tempDir.path() + "/" + self.transferBasename()

        t = self.transferClass().fromObjects(objects)
        t.setMetadata("description", description)
        t.save(tempPath, **kwargs)

        contents = contents or list()
        if iconPath:
            contents.append(iconPath)
        contents.append(tempPath)

        studiolibrary.LibraryItem.save(self, path=path, contents=contents)

        logger.info(u'Saved: {0}'.format(path))
