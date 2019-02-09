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


import studiolibrary


def showExample5():
    """
    Show two Studio Library widget instances.

    :rtype: None 
    """
    with studiolibrary.app():

        widget = studiolibrary.main(name="Example5-A", path="data")
        widget.setLocked(True)
        widget.move(100, 100)
        widget.theme().setAccentColor("rgb(250, 100, 50)")
        widget.theme().setBackgroundColor("rgb(80, 150, 120)")
        widget.show()

        widget = studiolibrary.main(name="Example5-B", path="data")
        widget.show()


if __name__ == "__main__":
    showExample5()
