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

import os
import mutils

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studiolibrary
import studiolibraryplugins

from studiolibraryplugins import mayabaseplugin


class Plugin(mayabaseplugin.Plugin):

    def __init__(self, library):
        """
        :type library: studiolibrary.Library
        """
        mayabaseplugin.Plugin.__init__(self, library)

        iconPath = studiolibraryplugins.resource().get("icons", "selectionSet.png")

        self.setName("Selection Set")
        self.setIconPath(iconPath)
        self.setExtension("set")

    def record(self, path=None):
        """
        :type path: str or None
        :rtype: Record
        """
        return Record(path=path, plugin=self)

    def createWidget(self, parent):
        """
        :type parent: QtWidgets.QWidget
        :rtype: SelectionSetCreateWidget
        """
        record = self.record()
        return SelectionSetCreateWidget(parent=parent, record=record)

    def previewWidget(self, parent, record):
        """
        :type parent: QtWidgets.QWidget
        :type record: Record
        :rtype: SelectionSetPreviewWidget
        """
        return SelectionSetPreviewWidget(parent=parent, record=record)


class Record(mayabaseplugin.Record):

    def __init__(self, *args, **kwargs):
        """
        :rtype: None
        """
        mayabaseplugin.Record.__init__(self, *args, **kwargs)
        self.setTransferBasename("set.json")
        self.setTransferClass(mutils.SelectionSet)

        self.setTransferBasename("set.list")
        if not os.path.exists(self.transferPath()):
            self.setTransferBasename("set.json")

    def previewWidget(self, parent=None):
        """
        Support for Studio Library 2.0

        :type parent: QtWidgets.QWidget
        :rtype: PosePreviewWidget
        """
        return SelectionSetPreviewWidget(parent=parent, record=self)

    def doubleClicked(self):
        """
        :rtype: None
        """
        self.loadFromSettings()

    def loadFromSettings(self):
        """
        :rtype: None
        """
        namespaces = self.namespaces()
        self.load(namespaces=namespaces)

    def load(self, namespaces=None):
        """
        :type namespaces: list[str] | None
        """
        self.selectContent(namespaces=namespaces)


class SelectionSetPreviewWidget(mayabaseplugin.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        :type record: Record
        """
        mayabaseplugin.PreviewWidget.__init__(self, *args, **kwargs)

    def accept(self):
        """
        :rtype: None
        """
        self.record().loadFromSettings()


class SelectionSetCreateWidget(mayabaseplugin.CreateWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        :type record: Record
        """
        mayabaseplugin.CreateWidget.__init__(self, *args, **kwargs)
