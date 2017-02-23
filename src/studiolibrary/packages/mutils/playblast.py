# Copyright 2017 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.

import os
import shutil
import logging

import mutils

try:
    import maya.cmds
except Exception:
    import traceback
    traceback.print_exc()


__all__ = [
    "playblast",
]

logger = logging.getLogger(__name__)


class PlayblastError(Exception):
    """Base class for exceptions in this module."""
    pass


def playblast(filename, modelPanel, startFrame, endFrame, width, height, step=1):
    """
    :type path: str
    :type modelPanel: str
    :type start: int
    :type end: int
    :type width: int
    :type height: int
    :type step: list[int]
    :rtype: str
    """
    logger.info("Playblasting '%s'" % filename)

    if startFrame == endFrame and os.path.exists(filename):
        os.remove(filename)

    frame = [i for i in range(startFrame, endFrame + 1, step)]

    modelPanel = modelPanel or mutils.currentModelPanel()
    if maya.cmds.modelPanel(modelPanel, query=True, exists=True):
        maya.cmds.setFocus(modelPanel)

    name, compression = os.path.splitext(filename)
    filename = filename.replace(compression, "")
    compression = compression.replace(".", "")
    offScreen = mutils.isLinux()

    path = maya.cmds.playblast(
        format="image",
        viewer=False,
        percent=100,
        quality=100,
        frame=frame,
        width=width,
        height=height,
        filename=filename,
        endTime=endFrame,
        startTime=startFrame,
        offScreen=offScreen,
        forceOverwrite=True,
        showOrnaments=False,
        compression=compression,
    )

    if not path:
        raise PlayblastError("Playblast was canceled")

    src = path.replace("####", str(int(0)).rjust(4, "0"))

    if startFrame == endFrame:
        dst = src.replace(".0000.", ".")
        logger.info("Renaming '%s' => '%s" % (src, dst))
        os.rename(src, dst)
        src = dst

    logger.info("Playblasted '%s'" % src)
    return src
