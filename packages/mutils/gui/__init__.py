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

try:
    import maya.OpenMayaUI as omui
except ImportError, e:
    print e

from studioqt import QtCore
from studioqt import QtWidgets


try:
    from shiboken2 import wrapInstance
except ImportError:
    try:
        from shiboken import wrapInstance
    except ImportError, e:
        print e


from .framerangemenu import FrameRangeMenu
from .framerangemenu import showFrameRangeMenu
from .modelpanelwidget import ModelPanelWidget
from .thumbnailcapturedialog import *


def mayaWindow():
    """
    Return the Maya main window as a QMainWindow object.
    
    :rtype: QMainWindow
    """
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindowPtr), QtWidgets.QMainWindow)


def makeMayaStandaloneWindow(w):
    """
    Make a standalone window, though parented under Maya's mainWindow.

    The parenting under Maya's mainWindow is done so that the QWidget will 
    not auto-destroy itself when the instance variable goes out of scope.
    """
    # Parent under the main Maya window
    w.setParent(mayaWindow())

    # Make this widget appear as a standalone window
    w.setWindowFlags(QtCore.Qt.Window)
    w.raise_()
    w.show()
