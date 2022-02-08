# coding=utf-8
# RUBEM Hydrological is a QGIS plugin that assists in setup the RUBEM model:
# Copyright (C) 2021-2022 LabSid PHA EPUSP

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact: rubem.hydrological@labsid.eng.br

"""RUBEM Hydrological plugin tree view data model code."""

from os.path import split

try:
    from qgis.PyQt.QtGui import QStandardItem
except ImportError:
    from PyQt5.QtGui import QStandardItem

# TODO: Add docstring information and comments
class StandardItem(QStandardItem):
    def __init__(self, txt="", isPath=False):
        super().__init__()

        self.setEditable(False)

        if isPath:
            _, self.title = split(txt)
            self.setText(self.title)
        else:
            self.setText(txt)
