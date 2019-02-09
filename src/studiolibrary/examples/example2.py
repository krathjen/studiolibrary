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

import studiolibrary


class CustomLibraryWidget(studiolibrary.LibraryWidget):

    def createSettingsMenu(self):
        """Reimplementing this method to add a custom action."""
        menu = super(CustomLibraryWidget, self).createSettingsMenu()

        menu.addSeparator()

        action = menu.addAction("Custom Action")
        action.triggered.connect(self.customActionClicked)

        return menu

    def customActionClicked(self):
        """Triggered when the custom action has been clicked."""
        print "Hello World"


if __name__ == "__main__":

    # Use the studiolibrary.app context for creating a QApplication instance
    with studiolibrary.app():

        w = CustomLibraryWidget.instance(name="Example2", path="data")
