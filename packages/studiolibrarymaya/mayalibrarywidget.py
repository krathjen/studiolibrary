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

import uuid
import logging

import studiolibrary

import maya.cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


logger = logging.getLogger(__name__)


class MayaLibraryWidget(MayaQWidgetDockableMixin, studiolibrary.LibraryWidget):

    def setObjectName(self, name):
        """
        Overriding to ensure the widget has a unique name for Maya.
        
        :type name: str
        :rtype: None 
        """
        name = '{0}_{1}'.format(name, uuid.uuid4())

        studiolibrary.LibraryWidget.setObjectName(self, name)

    def tabWidget(self):
        """
        Return the tab widget for the library widget.

        :rtype: QtWidgets.QTabWidget or None
        """
        return self.parent().parent().parent()

    def workspaceControlName(self):
        """
        Return the workspaceControl name for the widget.
        
        :rtype: str or None
        """
        parent = self.parent()
        if parent:
            return parent.objectName()
        else:
            return None

    def isDocked(self):
        """
        Convenience method to return if the widget is docked.
        
        :rtype: bool 
        """
        return not self.isFloating()

    def isFloating(self):
        """
        Return True if the the widget is a floating window.
        
        :rtype: bool 
        """
        name = self.workspaceControlName()
        if name:
            try:
                return maya.cmds.workspaceControl(name, q=True, floating=True)
            except AttributeError:
                msg = 'The "maya.cmds.workspaceControl" ' \
                      'command is not supported!'

                logger.warning(msg)

        return True

    def window(self):
        """
        Overriding this method to return itself when docked.
        
        This is used for saving the correct window position and size settings.
        
        :rtype: QWidgets.QWidget
        """
        if self.isDocked():
            return self
        else:
            return studiolibrary.LibraryWidget.window(self)

    def show(self):
        """
        Show the library widget as a dockable window.

        :rtype: None
        """
        MayaQWidgetDockableMixin.show(self, dockable=True)
        self.raise_()
        self.fixBorder()

    def resizeEvent(self, event):
        """
        Override method to remove the border when the window size has changed.
        
        :type event: QtCore.QEvent 
        :rtype: None 
        """
        if event.isAccepted():
            self.fixBorder()

    def floatingChanged(self, isFloating):
        """        
        Override method to remove the grey border when the parent has changed.

        Only supported/triggered in Maya 2018 

        :rtype: None
        """
        self.fixBorder()

    def fixBorder(self):
        """
        Remove the grey border around the tab widget.

        :rtype: None
        """
        if self.tabWidget():
            self.tabWidget().setStyleSheet("border:0px;")
