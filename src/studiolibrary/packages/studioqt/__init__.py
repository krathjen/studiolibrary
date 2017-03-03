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


from studioqt.vendor.Qt import QtGui, QtCore, QtWidgets, QtUiTools

import os

from studioqt.utils import *
from studioqt.icon import Icon
from studioqt.theme import Theme, ThemesMenu
from studioqt.color import Color
from studioqt.pixmap import Pixmap
from studioqt.resource import Resource
from studioqt.stylesheet import StyleSheet
from studioqt.contextmenu import ContextMenu

from studioqt.decorators import showWaitCursor

from studioqt.imagesequence import ImageSequence
from studioqt.imagesequence import ImageSequenceWidget

from studioqt.widgets.hcolorbar import HColorBar
from studioqt.widgets.messagebox import MessageBox
from studioqt.widgets.toastwidget import ToastWidget
from studioqt.widgets.statuswidget import StatusWidget
from studioqt.widgets.menubarwidget import MenuBarWidget

from studioqt.widgets.searchwidget import SearchWidget
from studioqt.widgets.searchwidget import SearchFilter

from studioqt.widgets.combinedwidget.combinedwidget import CombinedWidget
from studioqt.widgets.combinedwidget.combinedwidgetitem import CombinedWidgetItem
from studioqt.widgets.combinedwidget.combinedwidgetitemgroup import CombinedWidgetItemGroup

from studioqt.widgets.folderswidget import FoldersWidget

# Custom qt actions
from studioqt.actions.slideraction import SliderAction
from studioqt.actions.separatoraction import SeparatorAction

PATH = os.path.abspath(__file__)
DIRNAME = os.path.dirname(PATH).replace('\\', '/')
PACKAGES_DIRNAME = DIRNAME + "/packages"
RESOURCE_DIRNAME = DIRNAME + "/resource"

# Studio Qt Config Vars
SHOW_IN_FOLDER_CMD = None


global _resource

_resource = None


def resource():
    """
    :rtype: studioqt.Resource
    """
    global _resource

    if not _resource:
        _resource = Resource(dirname=RESOURCE_DIRNAME)

    return _resource


def icon(*args, **kwargs):
    """
    :type name: str
    :type extension: str
    :rtype: QtWidgets.QIcon
    """
    return resource().icon(*args, **kwargs)


def pixmap(*args, **kwargs):
    """
    :type name: str
    :type extension: str
    :rtype: QtWidgets.QPixmap
    """
    return resource().pixmap(*args, **kwargs)
