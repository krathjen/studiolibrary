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
"""
To test this demo please run this file.

NOTE: You don't need to be in Maya to run this demo.
"""

import logging

from studioqt import QtWidgets

import studioqt
import studiolibrary


__all__ = ["Plugin"]

logger = logging.getLogger(__name__)


class Plugin(studiolibrary.Plugin):
    """
    A studio library plugin must have a "Plugin" class as the main entry point.
    """

    def __init__(self, library):
        """
        :type library: studiolibrary.Library
        """
        studiolibrary.Plugin.__init__(self, library)

        self.setName("Demo")
        self.setExtension("demo")
        self.setIconPath(self.dirname() + "/resource/images/demo.png")

        # Use the settings object on the plugin class for
        # custom plugin options.
        # eg: "paste option", "current time",
        settings = self.settings()
        settings.setdefault("customPluginOption", True)

    def record(self, path=None):
        """
        :type path: str or None
        :rtype: Record
        """
        return Record(path=path, plugin=self)

    def createWidget(self, parent):
        """
        :type parent: QtWidgets.QWidget
        :rtype: CreateWidget
        """
        record = self.record()
        return CreateWidget(parent=parent, record=record)

    def previewWidget(self, parent, record):
        """
        :type parent: QtWidgets.QWidget
        :type record: Record
        :rtype: CreateWidget
        """
        return PreviewWidget(parent=parent, record=record)


class Record(studiolibrary.Record):

    def __init__(self, *args, **kwargs):
        studiolibrary.Record.__init__(self, *args, **kwargs)

    def doubleClicked(self):
        """
        Override this method to load the record on double click.
        """
        self.load()

    def save(self, path, contents=None):
        """
        Save is called from the create widget.
        """
        logger.info("Saving a new record!!")
        self.metaFile().data().setdefault("customRecordOption", "Hello World")
        studiolibrary.Record.save(self, path=path, contents=contents)

    def load(self):
        """
        Load is called from the preview widget
        """
        path = self.path()

        recordOption = self.metaFile().data().get("customRecordOption")
        pluginOption = self.plugin().settings().get("customPluginOption")

        logger.info('----------------')
        logger.info('Loading record "{0}"'.format(path))
        logger.info('Record Option: {0}'.format(recordOption))
        logger.info('Plugin Option: {0}'.format(pluginOption))
        logger.info('Record: {0}'.format(self))
        logger.info('Loaded record!')
        logger.info('----------------')


class CreateWidget(QtWidgets.QWidget):

    def __init__(self, record, parent):
        """
        :type record: Record
        :type parent: QtWidgets.QWidget
        """
        QtWidgets.QWidget.__init__(self, parent)

        # If you're using studioqt.loadUi(self) then the ui file must have the
        # following naming convention /resource/ui/PreviewWidget.ui
        studioqt.loadUi(self)

        self._record = record

        self.ui.acceptButton.clicked.connect(self.accept)

    def record(self):
        """
        :rtype: Record
        """
        return self._record

    def plugin(self):
        """
        :rtype: Plugin
        """
        return self.record().plugin()

    def libraryWidget(self):
        """
        :rtype: studiolibrary.LibraryWidget
        """
        return self.plugin().libraryWidget()

    def description(self):
        """
        :rtype: str
        """
        return str(self.ui.description.toPlainText())

    def showEvent(self, event):
        """
        :type: QtCore.QEvent
        """
        QtWidgets.QWidget.showEvent(self, event)
        self.ui.name.setFocus()

    def accept(self):
        """
        :rtype: None
        """
        try:
            folder = self.libraryWidget().selectedFolder()

            if not folder:
                msg = "No folder selected. Please select a destination folder."
                raise Exception(msg)

            path = folder.path() + "/" + str(self.ui.name.text())

            r = self.record()
            r.setDescription(self.description())
            r.save(path=path)

        except Exception, msg:
            logger.exception(msg)
            self.libraryWidget().criticalDialog(str(msg))


class PreviewWidget(QtWidgets.QWidget):

    def __init__(self, record, parent=None):
        """
        :type record: Record
        :type parent: studiolibrary.LibraryWidget
        """
        QtWidgets.QWidget.__init__(self, parent)

        # If you're using studioqt.loadUi(self) then the ui file must have the
        # following naming convention /resource/ui/PreviewWidget.ui
        studioqt.loadUi(self)

        self._record = record

        name = self.record().name()
        description = self.record().description()
        optionChecked = self.settings().get("customPluginOption")

        self.ui.name.setText(name)
        self.ui.description.setPlainText(description)
        self.ui.optionCheckBox.setChecked(optionChecked)

        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.optionCheckBox.stateChanged.connect(self.optionChanged)

    def record(self):
        """
        :rtype: Record
        """
        return self._record

    def settings(self):
        """
        :rtype: studiolibrary.Settings
        """
        return self.record().plugin().settings()

    def optionChanged(self, value):
        """
        :type value: int
        """
        self.settings().set("customPluginOption", value)
        self.settings().save()

    def accept(self):
        """
        :rtype: None
        """
        self.record().load()

        msg = (
            "You have successfully tested the demo plugin!\n"
            "Record Object:\n{0}"
        )

        msg = msg.format(self.record().metaFile().data())
        QtWidgets.QMessageBox.information(self.parent(), "YAY!", msg)


def test():
    """
    :rtype: None
    """
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Plugin Path:", __file__)

    studiolibrary.main(name="Demo", plugins=[__file__])


if __name__ == "__main__":
    test()
