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
"""
Example:
    
    from PySide2 import QtGui
    import studiolibrary.widgets
    menu = studiolibrary.widgets.LibrariesMenu()
    point = QtGui.QCursor.pos()
    menu.exec_(point)
"""
from functools import partial

from studiovendor.Qt import QtWidgets

import studiolibrary


class LibrariesMenu(QtWidgets.QMenu):

    def __init__(self, libraryWindow=None):
        super(LibrariesMenu, self).__init__(libraryWindow)

        self.setTitle('Libraries')

        libraries = studiolibrary.readSettings()
        default = studiolibrary.defaultLibrary()

        for name in libraries:

            library = libraries[name]

            path = library.get('path', '')
            kwargs = library.get('kwargs', {})

            enabled = True
            if libraryWindow:
                enabled = name != libraryWindow.name()

            text = name
            if name == default and name.lower() != "default":
                text = name + " (default)"

            action = QtWidgets.QAction(text, self)
            action.setEnabled(enabled)
            callback = partial(self.showLibrary, name, path, **kwargs)
            action.triggered.connect(callback)
            self.addAction(action)

    def showLibrary(self, name, path, **kwargs):
        """
        Show the library window which has given name and path.
        
        :type name: str
        :type path: str 
        :type kwargs: dict 
        """
        studiolibrary.main(name, path, **kwargs)
