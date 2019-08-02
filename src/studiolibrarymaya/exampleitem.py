# Copyright 2019 by Kurt Rathjen. All Rights Reserved.
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

    Name = "Example"
    Extension = ".example"
    IconPath = os.path.join(os.path.dirname(__file__), "icons", "pose.png")

    def loadSchema(self, **kwargs):
        """
        Get the schema used to load the item.

        :rtype: list[dict]
        """
        schema = [
            {
                "name": "myOption",
                "type": "bool",
                "default": False,
                "persistent": True,
            },
        ]

        return schema

    def load(self, **kwargs):
        """
        Load the item data from disc.

        :type kwargs: dict
        """
        logger.info("Load %s %s", self.path(), kwargs)
        raise NotImplementedError("Load is not implemented!\n" + str(kwargs))

    def saveSchema(self, **kwargs):
        """
        Get the schema used for saving the item.

        :rtype: list[dict]
        """
        return [
            # The name field and the folder field are both required by
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
        Save the item data to disc.

        :type kwargs: dict
        """
        logger.info("Save %s %s", self.path(), kwargs)
        raise NotImplementedError("Saving is not implemented!\n" + str(kwargs))
