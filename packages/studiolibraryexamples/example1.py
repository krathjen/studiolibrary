"""
Run this file or the following code to show this example.

import studiolibrary
from studiolibraryexamples import example1
reload(example1)
example1.main()
"""
import os

import studiolibrary

# studioqt supports both pyside (Qt4) and pyside2 (Qt5)
from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets


# At the moment all paths need to have forward slashes
dirname = os.path.dirname(__file__).replace("\\", "/")


class ImageItem(studiolibrary.LibraryItem):

    """An item to display image files in the Studio Library."""

    def load(self):
        """ Trigged when the user double clicks or clicks the load button."""
        print "Loaded", self.path()

    def doubleClicked(self):
        """Overriding this method to load any data on double click."""
        self.load()

    def thumbnailPath(self):
        """
        Return the thumbnail path to be displayed for the item.

        :rtype: str
        """
        return self.path()

    def previewWidget(self, libraryWidget):
        """
        Return the widget to be shown when the user clicks on the item.

        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: ImagePreviewWidget
        """
        return ImagePreviewWidget(self)


class ImagePreviewWidget(QtWidgets.QWidget):

    """The widget to be shown when the user clicks on an image item."""

    def __init__(self, item, *args):
        """
        :type item: ImageItem
        :type args: list
        """
        QtWidgets.QWidget.__init__(self, *args)

        self._item = item
        self._pixmap = QtGui.QPixmap(item.thumbnailPath())

        self._image = QtWidgets.QLabel(self)
        self._image.setAlignment(QtCore.Qt.AlignHCenter)

        self._loadButton = QtWidgets.QPushButton("Load")
        self._loadButton.setFixedHeight(40)
        self._loadButton.clicked.connect(self.load)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._image)
        layout.addStretch(1)
        layout.addWidget(self._loadButton)

        self.setLayout(layout)

    def load(self):
        """Triggered when the user clicks the load button."""
        self._item.load()

    def resizeEvent(self, event):
        """
        Overriding to adjust the image size when the widget changes size.

        :type event: QtCore.QSizeEvent
        """
        width = self.width() / 1.2
        transformMode = QtCore.Qt.SmoothTransformation
        pixmap = self._pixmap.scaledToWidth(width, transformMode)
        self._image.setPixmap(pixmap)


def main():
    """The main entry point for this example."""

    # Register the item class to the extension and ignore all jpgs that
    # contain the string "thumbnail."
    studiolibrary.registerItem(ImageItem, ".jpg", ignore="thumbnail.")
    studiolibrary.registerItem(ImageItem, ".png")
    studiolibrary.registerItem(ImageItem, ".gif")

    # Show the library with the given name and path
    studiolibrary.main(name="Example", path=dirname + "/data")


if __name__ == "__main__":

    import studioqt

    # The app context is used to check if a QApplication instance is running.
    with studioqt.app():
        main()