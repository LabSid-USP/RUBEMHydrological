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
# import shutil
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
 

Path_config= "D:/testeRubem/config.ini"
Path_config1= ("D:/")

# x = configParams()
# dir(x)
# x.inputDir = 'D:/testeRubem'
# x.outputDir = 'D:/testeRubem/outPut'
# configParams.genConfigFile(x)


class configParams(object):
    
    __slots__ = ['inputDir','outputDir', 'startDt', 'endDt', 'dem', 'clone', 'samplePts',
                 'etpSeries','etpfileprefix','ndviSeries','ndviMax','ndviMin','precSeries','precfileprefix', 'kpSeries','kpfileprefix','lcSeries',
                 'soilFile','kcMax','kcMin','rainyDays','nManning', 'aiSoil','aiSoil','aiSoil','aiSoil',
                 'gdSoil','krSoil','capCampoSoil', 'TporSoil', 'TsatSoil','TwSoil','rootZoneSoil',
                 'cellArea', 'initSoilMoisture', 'initEbSoil', 'initTuSoil', 'EbLimSoil','fparMax',
                 'fparMax','fparMin','laiMax','impInter','paramAlfa','paramB','paramW1','paramW2',
                 'paramW3','paramRCD','paramF','paramAlfagw','expInt','expEb','expEsd','expEvp',
                 'expLf','expRec','expTur','expRunoff']
    
    def __init__(self, **attrs):
        if attrs:
            for key, value in attrs.iteritems():
                setattr(self, key, value)
                
    def genConfigFile(self):  
        
        getKeys = self.__slots__
        getVals = []
        for i in range(len(getKeys)):
            try:
                print(getattr(self,getKeys[i]))                
                getVals.append(str(str(getKeys[i])+' = '+str(getattr(self,getKeys[i]))+'\n'))
            except:
                AttributeError
                     
        # mkDir
        isOutputFolder = os.path.isdir(str(self.inputDir))
        if isOutputFolder == False:
            os.mkdir(str(self.inputDir))
        
        #config folder = project folder
        cfFolder = self.inputDir[:-6] 
        cfFile = open(cfFolder+'/config.ini', 'a')
        cfFile = open(cfFolder+'/config.ini', 'w')
        cfFile.writelines(getVals)       
        cfFile.close()
        
        
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
        self.txtEdt_InputFolder.setText(selected_dir)
        ProjectPathConfig = self.txtEdt_InputFolder.text()
        
        inputDir = ProjectPathConfig + "/input"
        outputDir = ProjectPathConfig + "/output"
        
        self.txtEdt_InputFolder.setText(inputDir)
        self.txtEdt_OutputFolder.setText(outputDir)
        
        if os.path.isdir(str(inputDir)) == False:
            os.mkdir(str(inputDir)) 
        if os.path.isdir(str(outputDir)) == False:
            os.mkdir(str(outputDir))
            
        self.x = configParams()
        dir(self.x)
        self.x.inputDir = inputDir
        self.x.outputDir = outputDir
        

    def SetOutput(self):
        selected_dir = QFileDialog.getExistingDirectory(self, caption='Choose Directory',  directory=os.getcwd())
        self.txtEdt_OutputFolder.setText(selected_dir)
        OutputPathConfig = self.selected_dir.text()
        self.x.outputDir = selected_dir        

    def BtnSave_Click(self):
        configParams.genConfigFile(self.x)                

    def SearchDem(self):
        Dem_File, _= QFileDialog.getOpenFileName(self,"Search Dem",self.lastOpenedFile,"*.map")
        self.dem_box.setText(Dem_File)
        Dem = self.dem_box.text()
        self.fileInfo=QFileInfo(Dem_File)
        self.baseName=self.fileInfo.baseName()
        self.Demlayer=QgsRasterLayer(Dem_File,self.baseName)
        QgsProject.instance().addMapLayer(self.Demlayer)
        
        self.x.dem = Dem

    def SearchLandUse(self):
        LU_File, _ = QFileDialog.getOpenFileName(self, "Search Dem", self.lastOpenedFile, "*.map")
        self.land_box.setText(LU_File)
        LandUse = self.land_box.text()
        self.fileInfo = QFileInfo(LU_File)
        self.baseName = self.fileInfo.baseName()
        self.LUlayer = QgsRasterLayer(LU_File, self.baseName)
        QgsProject.instance().addMapLayer(self.LUlayer)

        self.x.soilFile = LandUse
        
    def Initial_Soil_Moisture(self):
        Initial_Soil_Moisture_value= self.ini_moist.text()

        self.x.initSoilMoisture = Initial_Soil_Moisture_value

    def SearchPrec(self):
        Prec_Files, _= QFileDialog.getOpenFileName(self,"Search Precipitation Series",self.lastOpenedFile,"*.001")
        self.prep_box.setText(Prec_Files[:-12]) 
        PrecPath = self.prep_box.text()
        PrecPrefix=Prec_Files[-12:].replace('.001', '').replace('0', '')

        self.x.precSeries = PrecPath
        self.x.precfileprefix=PrecPrefix


    def Search_ETP(self):
        Evapo_Files, _= QFileDialog.getOpenFileName(self,"Search Evapotranspiration Series",self.lastOpenedFile,"*.001")
        self.evapo_box.setText(Evapo_Files[:-12]) 
        EvapoPath = self.evapo_box.text()
        EvapoPrefix=Evapo_Files[-12:].replace('.001', '').replace('0', '')
              
        self.x.etpSeries = EvapoPath
        self.x.etpfileprefix=EvapoPrefix
    

    
    def Search_Kp(self):
        Kp_Files, _= QFileDialog.getOpenFileName(self,"Search Kp Series",self.lastOpenedFile,"*.001")
        self.Kp_box.setText(Kp_Files[:-12]) 
        KpPath = self.Kp_box.text()
        KpPrefix=Kp_Files[-12:].replace('.001', '').replace('0', '')
        
              
        self.x.kpSeries = KpPath
        self.x.kpfileprefix=KpPrefix


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

    def SetStartDate(self):
 
        year=str(self.dateEdit.date().year())
        month=str(self.dateEdit.date().month())
        day=str(self.dateEdit.date().day())
               

        a_file = open(Path_config, "r+")
        list_of_lines = a_file.readlines()
        list_of_lines[13] = str('start = '+day+"/"+month+"/"+year+'\n')
        a_file = open(Path_config, "w")
        a_file.writelines(list_of_lines)
        a_file.close()

    def SetEndDate(self):
     
        year=str(self.dateEdit_2.date().year())
        month=str(self.dateEdit_2.date().month())
        day=str(self.dateEdit_2.date().day())
               

        a_file = open(Path_config, "r+")
        list_of_lines = a_file.readlines()
        list_of_lines[14] = str('end = '+day+"/"+month+"/"+year+'\n')
        a_file = open(Path_config, "w")
        a_file.writelines(list_of_lines)
        a_file.close()
        
    # def generateNewNumber(self): 
    #     r = random.randint(1,100)
    #     self.lineEdit_7.setText("The number is: " + str(r))


    def NewProject(self,ptype=False):
        template=os.path.join(self.plugin_dir, "config/config.ini")
        if ptype:
            tempname = QFileDialog.getSaveFileName(self, "Save "+ptype+" project as",Path_config1, "*.ini")
        else:
            tempname = QFileDialog.getSaveFileName(self, "Save .ini as", Path_config1, "*.ini")

        out=str(tempname).partition("('")[2].partition("',")[0]
        newPath = shutil.copy(template, out)
        # clear project canvas
        qgsProject = QgsProject.instance()
        qgsProject.clear()
        global Path_config
        Path_config=newPath
        self.lineEdit_4.setText(" ") 
        self.lineEdit_2.setText(" ") 
        self.lineEdit_3.setText(" ") 
        self.lineEdit.setText(" ") 
        Default_start_date = "01/01/2000";
        Data = QDate.fromString(Default_start_date,"dd/MM/yyyy");
        self.dateEdit.setDate(Data)
        Default_End_date = "31/12/2000";
        Data2 = QDate.fromString(Default_start_date,"dd/MM/yyyy");
        self.dateEdit_2.setDate(Data2)
