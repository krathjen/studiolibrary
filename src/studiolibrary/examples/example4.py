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

import studioqt

from studioqt import QtWidgets

if __name__ == "__main__":

    # Use the studiolibrary.app context for creating a QApplication instance
    with studiolibrary.app():

        libraryWindow = studiolibrary.main(name="Example4", path="data")

        text = "Before you get started please choose a folder location " \
               "for storing the data. A network folder is recommended for " \
               "sharing within a studio."

        print studiolibrary.widgets.MessageBox.warning(libraryWindow, "Warning", text)

        button = studiolibrary.widgets.MessageBox.question(
            libraryWindow,
            "Welcome",
            text,
            width=450,
            height=350,
            enableDontShowCheckBox=True
        )

        if button == QtWidgets.QDialogButtonBox.Yes:
            print "Accepted"
        else:
            print "Rejected"

        print studiolibrary.widgets.MessageBox.input(
            libraryWindow,
            "Rename",
            "Rename the selected item?",
            inputText="face.anim",
        )

        print studiolibrary.widgets.MessageBox.critical(libraryWindow, "Error", text)

        dialog = studiolibrary.widgets.createMessageBox(libraryWindow, "Move Item", text)
        dialog.buttonBox().clear()

        dialog.addButton(u'Copy', QtWidgets.QDialogButtonBox.AcceptRole)
        dialog.addButton(u'Move', QtWidgets.QDialogButtonBox.AcceptRole)
        dialog.addButton(u'Cancel', QtWidgets.QDialogButtonBox.RejectRole)

        print dialog.exec_()


