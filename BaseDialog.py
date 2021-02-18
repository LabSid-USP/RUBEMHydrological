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
import os, random
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import subprocess
import processing
import shutil


from PyQt5.QtWidgets import QDialog

from PluginBase.gui.generated.ui_dialog import Ui_BaseDialog


try:
    import sys
    from pydevd import *
except:
    None
 

Path_config= str('C:/Users/camil/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/PluginBase/config.ini')
Path_config2= str('D:/ADP/')

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

    def SetInput(self):
    
        selected_dir = QFileDialog.getExistingDirectory(self, caption='Choose Directory', directory=os.getcwd())
        self.lineEdit_4.setText(selected_dir) 
        OutputPathConfig = self.lineEdit_4.text()
        

        a_file = open(Path_config, "r")
        list_of_lines = a_file.readlines()
        list_of_lines[3] = str('input = '+OutputPathConfig+'\n')
        a_file = open(Path_config, "w")
        a_file.writelines(list_of_lines)
        a_file.close()

    def SetOutput(self):

        selected_dir = QFileDialog.getExistingDirectory(self, caption='Choose Directory',  directory=os.getcwd())
        self.lineEdit_2.setText(selected_dir) 
        OutputPathConfig = self.lineEdit_2.text()
        

        a_file = open(Path_config, "r")
        list_of_lines = a_file.readlines()
        list_of_lines[6] = str('output = '+OutputPathConfig+'\n')
        a_file = open(Path_config, "w")
        a_file.writelines(list_of_lines)
        a_file.close()

        shutil.copy(Path_config, OutputPathConfig)

    def SearchDem(self):
        Dem_File, _= QFileDialog.getOpenFileName(self,"Search Dem",self.lastOpenedFile,"*.map")
        self.lineEdit.setText(Dem_File) 
        DemPathConfig = self.lineEdit.text()
        self.fileInfo=QFileInfo(Dem_File)
        self.baseName=self.fileInfo.baseName()
        self.Demlayer=QgsRasterLayer(Dem_File,self.baseName)
        QgsProject.instance().addMapLayer(self.Demlayer)
        

        a_file = open(Path_config, "r")
        list_of_lines = a_file.readlines()
        list_of_lines[9] = str('dem = ' +DemPathConfig+'\n')
        a_file = open(Path_config, "w")
        a_file.writelines(list_of_lines)
        a_file.close()

    def SearchKc_min(self):
        Kc_min_File, _= QFileDialog.getOpenFileName(self,"SearchKc_min",self.lastOpenedFile,"*.txt")
        self.lineEdit_3.setText(Kc_min_File) 
        Kc_minPathConfig = self.lineEdit_3.text()

        a_file = open(Path_config, "r")
        list_of_lines = a_file.readlines()
        list_of_lines[17] = str('Kc_min = '+Kc_minPathConfig+'\n')
        a_file = open(Path_config, "w")
        a_file.writelines(list_of_lines)
        a_file.close()

    def DLL_Create(self):
        
        command ="D:/SSD Petrobras/HydrologicalModel/RainfallRunoff.exe"
        os.chdir("D:/SSD Petrobras/HydrologicalModel")
        subprocess.run(command, shell=True, check=True)
        test_File= "D:/SSD Petrobras/HydrologicalModel/REPLAN/CenarioBase/output/Vazao00001.tif"
        self.fileInfo=QFileInfo(test_File)
        self.baseName=self.fileInfo.baseName()
        self.testlayer=QgsRasterLayer(test_File,self.baseName)
        QgsProject.instance().addMapLayer(self.testlayer)



   

    def NewProject(self):
        # check for current project and ask to save
        newproject = True
        #tempname = QtGui.QFileDialog.getSaveFileName(self, "Save "+ptype+" project as", self.sphyLocationPath, "*.cfg")
        # check if a new project needs/can be created based on the criteria tested above    
        if newproject:
            #self.Path_config.read(os.path.join(os.path.dirname(__file__), "config", "sphy_config_template.cfg"))
            # clear project canvas
            qgsProject = QgsProject.instance()
            qgsProject.clear()
            # save as new project
            self.saveAsProject("new")

    def saveAsProject(self, ptype=False):
        if ptype:
            tempname = QFileDialog.getSaveFileName(self, "Save "+ptype+" project as",Path_config2, "*.qgs")
        else:
            tempname = QFileDialog.getSaveFileName(self, "Save current project as", Path_config2, "*.qgs")
        #if tempname:
            #self.currentConfigFileName = tempname
            #self.saveProject()
            # write the qgs project file
        qgsProjectFileName = str(tempname)
        qgsProject = QgsProject.instance()
        qgsProject.setFileName(qgsProjectFileName)
        qgsProject.write()
        
    def generateNewNumber(self): 
        r = random.randint(1,100)
        self.lineEdit_7.setText("The number is: " + str(r))