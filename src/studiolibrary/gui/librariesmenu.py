# Copyright 2016 by Kurt Rathjen. All Rights Reserved.
#
# Permission to use, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Kurt Rathjen
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# KURT RATHJEN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# KURT RATHJEN BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import sys
import logging

from studioqt import QtGui
from studioqt import QtWidgets

import studioqt
import studiolibrary


__all__ = ["LibrariesMenu"]

logger = logging.getLogger(__name__)


class LibrariesMenu(QtWidgets.QMenu):

    def __init__(self, *args):
        """
        """
        QtWidgets.QMenu.__init__(self, *args)
        self.setTitle("Libraries")
        self.reload()

    def reload(self):
        self.clear()

        for library in studiolibrary.libraries():
            action = LibraryAction(self, library)
            self.addAction(action)
            action.setStatusTip('Load library "%s" "%s"' % (library.name(), library.path()))
            action.triggered.connect(library.show)


class LibraryAction(QtWidgets.QWidgetAction):

    STYLE_SHEET = """
#actionIcon {
    background-color: ACCENT_COLOR;
}

#actionWidget {
    background-color: BACKGROUND_COLOR;
}

#actionLabel, #actionLabel, #actionOption {
    background-color: BACKGROUND_COLOR;
    color: rgb(255, 255, 255);
}
#actionLabel:hover, #actionLabel:hover, #actionOption:hover {
    background-color: ACCENT_COLOR;
    color: rgb(255, 255, 255);
}
"""

    def __init__(self, parent, library):
        """
        :type parent: QtWidgets.QMenu
        :type library: studiolibrary.Library
        """
        QtWidgets.QWidgetAction.__init__(self, parent)
        self._library = library
        self.setText(self.library().name())

    def library(self):
        """
        :rtype: studiolibrary.Librarya
        """
        return self._library

    def deleteLibrary(self):
        """
        :rtype: None
        """
        self.parent().close()
        self.library().showDeleteDialog()

    def createWidget(self, parent):
        """
        :type parent: QtWidgets.QMenu
        """
        height = 25
        spacing = 1

        options = self.library().theme().options()

        styleSheet = studioqt.StyleSheet.fromText(
            LibraryAction.STYLE_SHEET,
            options=options
        )

        actionWidget = QtWidgets.QFrame(parent)
        actionWidget.setObjectName("actionWidget")
        actionWidget.setStyleSheet(styleSheet.data())

        actionLabel = QtWidgets.QLabel(self.library().name(), actionWidget)
        actionLabel.setObjectName('actionLabel')
        actionLabel.setFixedHeight(height)

        iconColor = QtGui.QColor(255, 255, 255, 220)
        icon = studiolibrary.resource().icon("delete", color=iconColor)
        actionOption = QtWidgets.QPushButton("", actionWidget)
        actionOption.setObjectName('actionOption')
        actionOption.setIcon(icon)
        actionOption.setFixedHeight(height + spacing)
        actionOption.setFixedWidth(height)
        actionOption.clicked.connect(self.deleteLibrary)

        actionIcon = QtWidgets.QLabel("", actionWidget)
        actionIcon.setObjectName('actionIcon')
        actionIcon.setFixedWidth(10)
        actionIcon.setFixedHeight(height)

        actionLayout = QtWidgets.QHBoxLayout(actionWidget)
        actionLayout.setSpacing(0)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.addWidget(actionIcon, stretch=1)
        actionLayout.addWidget(actionLabel, stretch=1)
        actionLayout.addWidget(actionOption, stretch=1)

        return actionWidget


class Example(QtWidgets.QMainWindow):

    def __init__(self):
        super(Example, self).__init__()

        menubar = self.menuBar()
        menu = LibrariesMenu("Libraries", menubar)
        menubar.addMenu(menu)

        self.statusBar()
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Menubar')
        self.show()


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(funcName)s: %(message)s',
                        filemode='w')

    app = QtWidgets.QApplication(sys.argv)
    e = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
