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

import studiolibrary

from studioqt import QtCore

import mutils

__all__ = ["MayaLibraryWidget"]


class MayaLibraryWidget(studiolibrary.LibraryWidget):

    def __init__(self, *args, **kwargs):
        studiolibrary.LibraryWidget.__init__(self, *args,  **kwargs)

        self._mayaCloseScriptJob = None

        try:
            self.enableMayaClosedEvent()
        except NameError, e:
            print e

        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)

    def updateWindowTitle(self):
        """
        Update the window title with the version and lock status.
        
        Overriding this method so that we can remove the version from the 
        title when the widget has been docked.

        :rtype: None
        """
        title = "Studio Library Maya - "

        if self.isDocked():
            title += self.library().name()
        else:
            title += studiolibrary.version() + " - " + self.library().name()

        if self.isLocked():
            title += " (Locked)"

        self.setWindowTitle(title)

    def enableMayaClosedEvent(self):
        """
        Create a Maya script job to trigger on the event "quitApplication".

        :rtype: None
        """
        if not self._mayaCloseScriptJob:
            event = ['quitApplication', self.mayaClosedEvent]
            self._mayaCloseScriptJob = mutils.ScriptJob(event=event)

    def mayaClosedEvent(self):
        """
        This method is triggered when the user closes Maya.

        :rtype: None
        """
        self.saveSettings()
