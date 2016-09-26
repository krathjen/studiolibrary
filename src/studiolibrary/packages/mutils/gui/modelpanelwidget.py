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

import mutils
import mutils.gui

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

try:
    import maya.cmds
    import maya.OpenMayaUI as mui
    isMaya = True
except ImportError:
    isMaya = False


__all__ = ["ModelPanelWidget"]


class ModelPanelWidget(QtWidgets.QWidget):

    _count = 0

    @staticmethod
    def findUniqueName(name):
        ModelPanelWidget._count += 1
        return name + str(ModelPanelWidget._count)

    def __init__(self, parent, name="capturedModelPanel", **kwargs):
        super(ModelPanelWidget, self).__init__(parent, **kwargs)

        name = self.findUniqueName(name)
        self.setObjectName(name + "Widget")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setObjectName(name + "Layout")
        self.setLayout(layout)

        maya.cmds.setParent(layout.objectName())
        self._modelPanel = maya.cmds.modelPanel(name, label="ModelPanel")
        self.setModelPanelOptions()

    def setModelPanelOptions(self):

        modelPanel = self.name()

        maya.cmds.modelEditor(modelPanel, edit=True, allObjects=False)
        maya.cmds.modelEditor(modelPanel, edit=True, grid=False)
        maya.cmds.modelEditor(modelPanel, edit=True, dynamics=False)
        maya.cmds.modelEditor(modelPanel, edit=True, activeOnly=False)
        maya.cmds.modelEditor(modelPanel, edit=True, manipulators=False)
        maya.cmds.modelEditor(modelPanel, edit=True, headsUpDisplay=False)
        maya.cmds.modelEditor(modelPanel, edit=True, selectionHiliteDisplay=False)

        maya.cmds.modelEditor(modelPanel, edit=True, polymeshes=True)
        maya.cmds.modelEditor(modelPanel, edit=True, nurbsSurfaces=True)
        maya.cmds.modelEditor(modelPanel, edit=True, subdivSurfaces=True)
        maya.cmds.modelEditor(modelPanel, edit=True, displayTextures=True)
        maya.cmds.modelEditor(modelPanel, edit=True, displayAppearance="smoothShaded")

        currentModelPanel = mutils.currentModelPanel()

        if currentModelPanel:
            camera = maya.cmds.modelEditor(currentModelPanel, query=True, camera=True)
            displayLights = maya.cmds.modelEditor(currentModelPanel, query=True, displayLights=True)
            displayTextures = maya.cmds.modelEditor(currentModelPanel, query=True, displayTextures=True)

            maya.cmds.modelEditor(modelPanel, edit=True, camera=camera)
            maya.cmds.modelEditor(modelPanel, edit=True, displayLights=displayLights)
            maya.cmds.modelEditor(modelPanel, edit=True, displayTextures=displayTextures)

    def name(self):
        return self._modelPanel

    def modelPanel(self):
        ptr = mui.MQtUtil.findControl(self._modelPanel)
        return mutils.gui.wrapInstance(long(ptr), QtWidgets.QWidget)

    def barLayout(self):
        name = maya.cmds.modelPanel(self._modelPanel, query=True, barLayout=True)
        ptr = mui.MQtUtil.findControl(name)
        return mutils.gui.wrapInstance(long(ptr), QtCore.QObject)

    def hideBarLayout(self):
        self.barLayout().hide()

    def hideMenuBar(self):
        maya.cmds.modelPanel(self._modelPanel, edit=True, menuBarVisible=False)

    def setCamera(self, name):
        maya.cmds.modelPanel(self._modelPanel, edit=True, cam=name)


if __name__ == "__main__":
    widget = ModelPanelWidget(None, "modelPanel")
    widget.show()
