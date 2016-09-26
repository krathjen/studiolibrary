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
#---------------------------------------------------------------------------
# Saving a mirror table record
#---------------------------------------------------------------------------

from studiolibraryplugins import mirrortableplugin

path = "/AnimLibrary/Characters/Malcolm/malcolm.mirror"
objects = maya.cmds.ls(selection=True) or []
leftSide = "Lf"
rightSide = "Rf"

record = mirrortableplugin.Record(path)
record.save(objects=objects, leftSide=leftSide, rightSide=rightSide)

#---------------------------------------------------------------------------
# Loading a mirror table record
#---------------------------------------------------------------------------

from studiolibraryplugins import mirrortableplugin

path = "/AnimLibrary/Characters/Malcolm/malcolm.mirror"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

record = mirrortableplugin.Record(path)
record.load(objects=objects, namespaces=namespaces, animation=True, time=None)
"""

import os
import logging

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import mutils
import studiolibrary
import studiolibraryplugins

from studiolibraryplugins import mayabaseplugin

try:
    import maya.cmds
except ImportError, msg:
    print msg


logger = logging.getLogger(__name__)

MirrorOption = mutils.MirrorOption


class Plugin(mayabaseplugin.Plugin):

    def __init__(self, library):
        """
        :type library: studiolibrary.Library
        """
        studiolibrary.Plugin.__init__(self, library)

        iconPath = studiolibraryplugins.resource().get("icons", "mirrortable.png")

        self.setName("Mirror Table")
        self.setIconPath(iconPath)
        self.setExtension("mirror")

    def record(self, path=None):
        """
        :type path: str or None
        :rtype: Record
        """
        return Record(path=path, plugin=self)

    def createWidget(self, parent):
        """
        :type parent: QtWidgets.QWidget
        :rtype: MirrorTableCreateWidget
        """
        record = self.record()
        return MirrorTableCreateWidget(parent=parent, record=record)

    def previewWidget(self, parent, record):
        """
        :type parent: QtWidgets.QWidget
        :type record: Record
        :rtype: MirrorTablePreviewWidget
        """
        return MirrorTablePreviewWidget(parent=parent, record=record)


class Record(mayabaseplugin.Record):

    def __init__(self, *args, **kwargs):
        """
        :type args:
        :type kwargs:
        """
        mayabaseplugin.Record.__init__(self, *args, **kwargs)
        self.setTransferBasename("mirrortable.json")
        self.setTransferClass(mutils.MirrorTable)

    def previewWidget(self, parent=None):
        """
        Support for Studio Library 2.0

        :type parent: QtWidgets.QWidget
        :rtype: PosePreviewWidget
        """
        return MirrorTablePreviewWidget(parent=parent, record=self)

    def keyPressEvent(self, event):
        """
        :type event: 
        """
        if event.key() == QtCore.Qt.Key_M:
            pass

    def doubleClicked(self):
        """
        :rtype: None
        """
        self.loadFromSettings()

    def loadFromSettings(self):
        """
        :rtype: None
        """
        mirrorOption = self.settings().get("mirrorOption", MirrorOption.Swap)
        mirrorAnimation = self.settings().get("mirrorAnimation", True)
        namespaces = self.namespaces()
        objects = maya.cmds.ls(selection=True) or []

        try:
            self.load(
                objects=objects,
                option=mirrorOption,
                animation=mirrorAnimation,
                namespaces=namespaces,
            )
        except Exception, msg:
            self.showErrorDialog(msg)
            raise

    @mutils.showWaitCursor
    def load(self, objects=None, namespaces=None, option=None, animation=True, time=None):
        """
        :type objects: list[str]
        :type namespaces: list[str]
        :type option: MirrorOption
        :type animation: bool
        :type time: list[int]
        """
        objects = objects or []
        self.transferObject().load(
            objects=objects,
            namespaces=namespaces,
            option=option,
            animation=animation,
            time=time,
        )

    def save(self, objects, leftSide, rightSide, path=None, iconPath=None):
        """
        :type path: str
        :type objects: list[str]
        :type iconPath: str
        :rtype: None

        """
        logger.info("Saving: %s" % self.transferPath())

        tempDir = mutils.TempDir("Transfer", makedirs=True)
        tempPath = os.path.join(tempDir.path(), self.transferBasename())

        t = self.transferClass().fromObjects(
            objects,
            leftSide=leftSide,
            rightSide=rightSide
        )
        t.save(tempPath)

        studiolibrary.Record.save(self, path=path, contents=[tempPath, iconPath])


class MirrorTablePreviewWidget(mayabaseplugin.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        :type record: Record
        """
        mayabaseplugin.PreviewWidget.__init__(self, *args, **kwargs)

        self.ui.mirrorAnimationCheckBox.stateChanged.connect(self.updateState)
        self.ui.mirrorOptionComboBox.currentIndexChanged.connect(self.updateState)

    def setRecord(self, record):
        """
        :type record: Record
        :rtype: None
        """
        mayabaseplugin.PreviewWidget.setRecord(self, record)

        mt = record.transferObject()
        self.ui.left.setText(mt.leftSide())
        self.ui.right.setText(mt.rightSide())

    def mirrorOption(self):
        """
        :rtype: str
        """
        text = self.ui.mirrorOptionComboBox.currentText()
        return self.ui.mirrorOptionComboBox.findText(text, QtCore.Qt.MatchExactly)

    def mirrorAnimation(self):
        """
        :rtype: bool
        """
        return self.ui.mirrorAnimationCheckBox.isChecked()

    def state(self):
        """
        :rtype: dict
        """
        state = super(MirrorTablePreviewWidget, self).state()

        state["mirrorOption"] = int(self.mirrorOption())
        state["mirrorAnimation"] = bool(self.mirrorAnimation())

        return state

    def setState(self, state):
        """
        :type state: dict
        """
        super(MirrorTablePreviewWidget, self).setState(state)

        mirrorOption = int(state.get("mirrorOption", MirrorOption.Swap))
        mirrorAnimation = bool(state.get("mirrorAnimation", True))

        self.ui.mirrorOptionComboBox.setCurrentIndex(mirrorOption)
        self.ui.mirrorAnimationCheckBox.setChecked(mirrorAnimation)

    def accept(self):
        """
        :rtype: None
        """
        self.record().loadFromSettings()


class MirrorTableCreateWidget(mayabaseplugin.CreateWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        :type record: Record
        """
        mayabaseplugin.CreateWidget.__init__(self, *args, **kwargs)

    def leftText(self):
        """
        :rtype: str
        """
        return str(self.ui.left.text()).strip()

    def rightText(self):
        """
        :rtype: str
        """
        return str(self.ui.right.text()).strip()

    def selectionChanged(self):
        """
        :rtype: None
        """
        objects = maya.cmds.ls(selection=True) or []

        if not self.ui.left.text():
            self.ui.left.setText(mutils.MirrorTable.findLeftSide(objects))

        if not self.ui.right.text():
            self.ui.right.setText(mutils.MirrorTable.findRightSide(objects))

        leftSide = str(self.ui.left.text())
        rightSide = str(self.ui.right.text())

        mt = mutils.MirrorTable.fromObjects(
                [],
                leftSide=leftSide,
                rightSide=rightSide
        )

        self.ui.leftCount.setText(str(mt.leftCount(objects)))
        self.ui.rightCount.setText(str(mt.rightCount(objects)))

        mayabaseplugin.CreateWidget.selectionChanged(self)

    def save(self, objects, path, iconPath, description):
        """
        :type objects: list[str]
        :type path: str
        :type iconPath: str
        :type description: str
        :rtype: None
        """
        iconPath = self.iconPath()
        leftSide = self.leftText()
        rightSide = self.rightText()

        r = self.record()
        r.setDescription(description)

        self.record().save(
            path=path,
            objects=objects,
            iconPath=iconPath,
            leftSide=leftSide,
            rightSide=rightSide,
        )
