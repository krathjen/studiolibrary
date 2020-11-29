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
"""
NOTE: Make sure you register this item in the config.
"""

import os
import logging

from studiolibrarymaya import baseitem


logger = logging.getLogger(__name__)


class ExampleItem(baseitem.BaseItem):

    NAME = "Example"
    EXTENSION = ".example"
    ICON_PATH = os.path.join(os.path.dirname(__file__), "icons", "pose.png")

    def loadSchema(self, **kwargs):
        """
        Get the schema used for loading the example item.

        :rtype: list[dict]
        """
        return [
            {
                "name": "option",
                "type": "bool",
                "default": False,
                "persistent": True,
            },
        ]

    def load(self, **kwargs):
        """
        The load method is called with the user values from the load schema.

        :type kwargs: dict
        """
        logger.info("Loading %s %s", self.path(), kwargs)
        raise NotImplementedError("The load method is not implemented!")

    def saveSchema(self, **kwargs):
        """
        Get the schema used for saving the example item.

        :rtype: list[dict]
        """
        return [
            # The 'name' field and the 'folder' field are both required by
            # the BaseItem. How this is handled may change in the future.
            {
                "name": "folder",
                "type": "path",
                "layout": "vertical",
                "visible": False,
            },
            {
                "name": "name",
                "type": "string",
                "layout": "vertical"
            },
            {
                "name": "fileType",
                "type": "enum",
                "layout": "vertical",
                "default": "mayaAscii",
                "items": ["mayaAscii", "mayaBinary"],
                "persistent": True
            },
        ]

    def save(self, **kwargs):
        """
        The save method is called with the user values from the save schema.

        :type kwargs: dict
        """
        logger.info("Saving %s %s", self.path(), kwargs)
        raise NotImplementedError("The save method is not implemented!")
