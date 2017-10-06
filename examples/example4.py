# An example for showing the message box dialog.

import studiolibrary

import studioqt

from studioqt import QtWidgets

if __name__ == "__main__":

    # Use the studiolibrary.app context for creating a QApplication instance
    with studiolibrary.app():

        libraryWidget = studiolibrary.main(name="Example4", path="data")

        text = "Before you get started please choose a folder location " \
               "for storing the data. A network folder is recommended for " \
               "sharing within a studio."

        print studioqt.MessageBox.warning(libraryWidget, "Warning", text)

        button = studioqt.MessageBox.question(
            libraryWidget,
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

        print studioqt.MessageBox.input(
            libraryWidget,
            "Rename",
            "Rename the selected item?",
            inputText="face.anim",
        )

        print studioqt.MessageBox.critical(libraryWidget, "Error", text)

        dialog = studioqt.createMessageBox(libraryWidget, "Move Item", text)
        dialog.buttonBox().clear()

        dialog.addButton(u'Copy', QtWidgets.QDialogButtonBox.AcceptRole)
        dialog.addButton(u'Move', QtWidgets.QDialogButtonBox.AcceptRole)
        dialog.addButton(u'Cancel', QtWidgets.QDialogButtonBox.RejectRole)

        print dialog.exec_()


