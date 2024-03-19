# coding=utf-8
# RUBEM Hydrological is a QGIS plugin that assists in setup the RUBEM model:
# Copyright (C) 2021-2024 LabSid PHA EPUSP

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

"""RUBEM Hydrological plugin starting point.

This file is required by Python’s import system.
Also, QGIS requires that this file contains a `classFactory()` function,\n
which is called when the plugin gets loaded into QGIS.
"""


def classFactory(iface):
    """Call when the plugin gets loaded into QGIS.

    :param iface: Reference to the instance of `QgisInterface`.
    :type iface: class

    :return: Object of RUBEM Hydrological plugin’s class from the\n
    `rubem_hydrological.py` (`RUBEMHydrological`).
    :rtype: class
    """
    try:
        from .plugin.core import RUBEMHydrological
    except ImportError:
        from plugin.core import RUBEMHydrological

    return RUBEMHydrological(iface)
