# -*- coding: utf-8 -*-
"""
/***************************************************************************
 **Nombre del plugin
                                 A QGIS plugin
 **Descripcion
                             -------------------
        begin                : **Fecha
        copyright            : **COPYRIGHT
        email                : **Mail de contacto
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 #   any later version.                                                    *
 *                                                                         *
 ***************************************************************************/
"""
import os.path
from qgis.core import *
from qgis.gui import *
import shutil
import os.path
from qgis.PyQt.QtCore import Qt
from qgis.gui import *
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from PyQt5.QtWidgets import QDialog

from PluginBase.gui.generated.ui_dialog import Ui_BaseDialog


try:
    import sys
    from pydevd import *
except:
    None
 
class BaseDialog(QDialog, Ui_BaseDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface
        self.lastOpenedFile = None
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))


    def showlabel(self):
        a=self.mMapLayerComboBox.currentLayer().name()
        self.label.setText(a)

    def DemSearch(self):
        self.filename, _= QFileDialog.getOpenFileName(self,"Search Dem",self.lastOpenedFile,"*.map")
        DemName= self.lineEdit.setText(self.filename) 
        DemPathConfig = self.lineEdit.text()
        
        with open('C:/Users/omary/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/PluginBase/Config.txt', 'a') as f:
            f.write(DemPathConfig)

