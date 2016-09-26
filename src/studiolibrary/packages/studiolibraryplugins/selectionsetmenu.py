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
import logging
from functools import partial

from studioqt import QtGui
from studioqt import QtWidgets


import studiolibrary
import studiolibraryplugins

from studiolibraryplugins import selectionsetplugin


__all__ = ["SelectionSetMenu"]

logger = logging.getLogger(__name__)


def selectContentAction(record, parent=None):
    """
    :param record: mayabaseplugin.Record
    :param parent: QtWidgets.QMenu
    """
    icon = studiolibraryplugins.resource().icon("arrow")
    action = QtWidgets.QAction(icon, "Select content", parent)
    action.triggered.connect(record.selectContent)
    return action


def show(path, **kwargs):
    """
    :type path: str
    :rtype: QtWidgets.QAction
    """
    menu = SelectionSetMenu.fromPath(path, **kwargs)
    position = QtGui.QCursor().pos()
    action = menu.exec_(position)
    return action


class SelectionSetMenu(QtWidgets.QMenu):

    @classmethod
    def fromPath(cls, path, **kwargs):
        """
        :type path: str
        :type kwargs: dict
        :rtype: QtWidgets.QAction
        """
        record = studiolibrary.BasePath(path)
        return cls(record, enableSelectContent=False, **kwargs)

    def __init__(
            self,
            record,
            parent=None,
            namespaces=None,
            enableSelectContent=True,
    ):
        """
        :type record: mayabaseplugin.Record
        :type parent: QtWidgets.QMenu
        :type namespaces: list[str]
        :type enableSelectContent: bool
        """
        QtWidgets.QMenu.__init__(self, "Selection Sets", parent)

        icon = studiolibraryplugins.resource().icon("selectionSet")
        self.setIcon(icon)

        self._record = record
        self._namespaces = namespaces
        self._enableSelectContent = enableSelectContent
        self.reload()

    def record(self):
        """
        :rtype: mayabaseplugin.Record
        """
        return self._record

    def namespaces(self):
        """
        :rtype: list[str]
        """
        return self._namespaces

    def selectContent(self):
        """
        :rtype: None
        """
        self.record().selectContent(namespaces=self.namespaces())

    def selectionSets(self):
        """
        :rtype: list[studiolibrary.Record]
        """
        path = self.record().path()
        match = lambda path: path.endswith(".set")

        paths = studiolibrary.findPaths(
            path,
            match=match,
            direction=studiolibrary.Direction.Up,
        )

        paths = list(paths)
        records = []

        for path in paths:
            record = selectionsetplugin.Record(path)
            records.append(record)

        return records

    def reload(self):
        """
        :rtype: None
        """
        self.clear()

        if self._enableSelectContent:
            action = selectContentAction(record=self.record(), parent=self)
            self.addAction(action)
            self.addSeparator()

        selectionSets = self.selectionSets()

        if selectionSets:
            for selectionSet in selectionSets:
                dirname = os.path.basename(selectionSet.dirname())
                basename = selectionSet.name().replace(selectionSet.extension(),"")
                nicename = dirname + ": " + basename

                action = QtWidgets.QAction(nicename, self)
                callback = partial(selectionSet.load, namespaces=self.namespaces())
                action.triggered.connect(callback)
                self.addAction(action)
        else:
            action = QtWidgets.QAction("No selection sets found!", self)
            action.setEnabled(False)
            self.addAction(action)
