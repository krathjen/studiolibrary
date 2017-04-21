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

import mayadockwidgetmixin

__all__ = ["MayaLibraryWidget"]


class MayaLibraryWidget(
    studiolibrary.LibraryWidget,
    mayadockwidgetmixin.MayaDockWidgetMixin
):

    def __init__(self, *args, **kwargs):
        """
        The Maya Library Widget can be used outside of Maya, however it
        is recommended that you use the base library widget for this.
        
        :type args: list
        :type kwargs: dict
        """
        studiolibrary.LibraryWidget.__init__(self, *args,  **kwargs)
        mayadockwidgetmixin.MayaDockWidgetMixin.__init__(self, None)

        self._mayaCloseScriptJob = None

        try:
            self.enableMayaClosedEvent()
        except NameError, e:
            print e

        self.dockingChanged.connect(self.updateWindowTitle)
        self.updateWindowTitle()

    def settings(self):
        """
        Return a dict containing the settings for the widget.
        
        Overriding this method to add support for dock settings.
        
        :rtype: dict 
        """
        settings = studiolibrary.LibraryWidget.settings(self)

        settings["dockWidget"] = self.dockSettings()

        return settings

    def setSettings(self, settings):
        """
        Set the state of the widget with the given settings dict.

        Overriding this method to add support for dock settings.

        :type settings: dict 
        """
        studiolibrary.LibraryWidget.setSettings(self, settings)

        dockSettings = settings.get("dockWidget", {})

        self.setDockSettings(dockSettings)

    def createSettingsMenu(self):
        """
        Create a new instance of the settings menu.
        
        Overriding this method to add support for docking.

        :rtype: studioqt.Menu
        """
        menu = studiolibrary.LibraryWidget.createSettingsMenu(self)

        dockMenu = self.dockMenu()

        menu.insertMenuBefore("debug mode", dockMenu)
        menu.insertSeparatorBefore("debug mode")

        return menu

    def updateWindowTitle(self):
        """
        Update the window title with the version and lock status.

        Overriding this method so that we can remove the version from the
        title when the widget has been docked.

        :rtype: None
        """
        title = "Studio Library - "

        if self.isDocked():
            title += self.library().name()
        else:
            title = "Studio Library Maya - "
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

    # The following methods need to be reimplemented because of how the
    # mixin has been implemented.

    def raise_(self):
        """
        Need to reimplemented because of the mixin.

        :rtype: None
        """
        mayadockwidgetmixin.MayaDockWidgetMixin.raise_(self)

    def showEvent(self, event):
        """
        Need to reimplemented because of the mixin.

        :rtype: None
        """
        studiolibrary.LibraryWidget.showEvent(self, event)

    def setWindowTitle(self, text):
        """
        Need to reimplemented because of the mixin.

        :rtype: None
        """
        mayadockwidgetmixin.MayaDockWidgetMixin.setWindowTitle(self, text)
