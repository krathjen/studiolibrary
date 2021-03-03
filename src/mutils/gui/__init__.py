# Copyright 2020 by Kurt Rathjen. All Rights Reserved.
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

from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

try:
    import maya.OpenMayaUI as omui
except ImportError as error:
    print(error)

try:
    from shiboken2 import wrapInstance
except ImportError:
    try:
        from shiboken import wrapInstance
    except ImportError as error:
        print(error)

from .framerangemenu import FrameRangeMenu
from .framerangemenu import showFrameRangeMenu
from .modelpanelwidget import ModelPanelWidget
from .thumbnailcapturedialog import *
from .thumbnailcapturemenu import ThumbnailCaptureMenu


def mayaWindow():
    """
    Return the Maya main window as a QMainWindow object.
    
    :rtype: QMainWindow
    """
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mainWindowPtr), QtWidgets.QMainWindow)


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
