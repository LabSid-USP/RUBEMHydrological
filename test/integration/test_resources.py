# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = "rubem.hydrological@labsid.eng.br"
__date__ = "2021-05-19"
__copyright__ = "Copyright 2021, LabSid"

from logging import root
import os
import unittest

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QApplication


class RUBEMHydrologicalResourcesTest(unittest.TestCase):
    """Test resources work."""

    def setUp(self):
        """Runs before each test."""
        self.app = QApplication([])

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_icon_png(self):
        """"""
        path = ":imgBase/images/icon.png"
        icon = QIcon(path)
        self.assertFalse(icon.isNull())

    # def test_icon_svg(self):
    #     """"""
    #     path = ":imgBase/images/icon.svg"
    #     icon = QIcon(path)
    #     self.assertFalse(icon.isNull())  
        
    def test_logo_labsid(self):
        """"""
        path = ":imgBase/images/labsid.png"
        icon = QIcon(path)
        self.assertFalse(icon.isNull())  
        
    def test_logo_epusp(self):
        """"""
        path = ":imgBase/images/epusp.png"
        icon = QIcon(path)
        self.assertFalse(icon.isNull())  
        
    def test_logo_adp(self):
        """"""
        path = ":imgBase/images/adp.png"
        icon = QIcon(path)
        self.assertFalse(icon.isNull())  

    def test_icon_action_file_new(self):
        """"""
        path = ":iconMenu/images/qgis-default-theme/mActionFileNew.svg"
        icon = QIcon(path)
        self.assertFalse(icon.isNull())  
        
    def test_icon_action_file_open(self):
        """"""
        path = ":iconMenu/images/qgis-default-theme/mActionFileOpen.svg"
        icon = QIcon(path)
        self.assertFalse(icon.isNull())  
        
    def test_icon_action_file_save(self):
        """"""
        path = ":iconMenu/images/qgis-default-theme/mActionFileSave.svg"
        icon = QIcon(path)
        self.assertFalse(icon.isNull())  

    def test_icon_action_file_save_as(self):
        """"""
        path = ":iconMenu/images/qgis-default-theme/mActionFileSaveAs.svg"
        icon = QIcon(path)
        self.assertFalse(icon.isNull())  
        
    def test_icon_action_help_contents(self):
        """"""
        path = ":iconMenu/images/qgis-default-theme/mActionHelpContents.svg"
        icon = QIcon(path)
        self.assertFalse(icon.isNull())  
        
    def test_icon_action_plugin_new(self):
        """"""
        path = ":iconMenu/images/qgis-default-theme/pluginNew.svg"
        icon = QIcon(path)
        self.assertFalse(icon.isNull())                  

if __name__ == "__main__":
    suite = unittest.makeSuite(RUBEMHydrologicalResourcesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
