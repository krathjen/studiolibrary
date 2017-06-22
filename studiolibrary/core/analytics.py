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

import urllib2
import getpass
import platform
import threading


__all__ = ["Analytics"]


class Analytics:

    ENABLED = True
    DEFAULT_ID = None

    def __init__(self, tid, name="PacakgeName", version="1.0.0"):
        """
        :type name: str
        :type version: str
        """
        self._tid = tid
        self._name = name
        self._enabled = Analytics.ENABLED
        self._version = version

    def setId(self, tid):
        """
        :type tid: str
        """
        self._tid = tid

    def setEnabled(self, enable):
        """
        :type enable: bool
        """
        self._enabled = enable

    def isEnabled(self):
        """
        :rtype: bool
        """
        return self._enabled

    def logEvent(self, name, value):
        """
        :type name: str
        :type value: str
        """
        try:
            if self.isEnabled():
                url = self._url + "&t=event&ec=" + name + "&ea=" + value
                self.send(url)
        except Exception:
            pass

    def logScreen(self, name):
        """
        :type name: str
        """
        try:
            if self.isEnabled():
                url = self._url + "&t=appview&cd=" + name
                self.send(url)
        except Exception:
            pass

    @property
    def cid(self):
        """
        :rtype: str
        """
        return getpass.getuser() + "-" + platform.node()

    @property
    def _url(self):
        """
        :rtype: str
        """
        url = "http://www.google-analytics.com/collect?" \
              "v=1&ul=en-us&a=448166238&_u=.sB&_v=ma1b3&qt=2500&z=185"

        return url + "&tid=" + self._tid + "&an=" + self._name + "&cid=" + self.cid + "&av=" + self._version

    @staticmethod
    def send(url):
        """
        :type url: str
        """
        t = threading.Thread(target=Analytics._send, args=(url,))
        t.start()

    @staticmethod
    def _send(url):
        """
        :type url: str
        """
        try:
            url = url.replace(" ", "")
            f = urllib2.urlopen(url, None, 1.0)
        except Exception, e:
            pass
