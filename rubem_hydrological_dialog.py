# coding=utf-8
"""
/***************************************************************************
 **RUBEM Hydrological
                A Rainfall rUnoff Balance Enhanced Model wizard
 **Description
                             -------------------
        begin                : **2021
        copyright            : **Laboratório de Sistemas de Suporte a 
                             :   Decisões Aplicados à Engenharia Ambiental e 
                             :   de Recursos Hídricos (LabSid) PHA-EPUSP
        email                : **rubem.hydrological@labsid.eng.br
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

__author__ = 'rubem.hydrological@labsid.eng.br'
__date__ = '2021-05-19'
__copyright__ = 'Copyright 2021, LabSid'

import os
import io
from pathlib import Path
import configparser
import subprocess

try:
    from qgis.PyQt.QtWidgets import QDialog, QFileDialog
    from qgis.PyQt.QtCore import QObject, QThread, pyqtSignal
except ImportError:
    from PyQt5.QtWidgets import QDialog, QFileDialog
    from PyQt5.QtCore import QObject, QThread, pyqtSignal

from .rubem_hydrological_dialog_base_ui import Ui_RUBEMHydrological
        
class RUBEMHydrologicalDialog(QDialog, Ui_RUBEMHydrological):
    def __init__(self, iface):
        """Constructor."""
                
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface
        self.lastOpenedFile = None
        self.lastOpenedDirectory = None
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.modelFilePath = None
        self.configFilePath = None
        self.config = configparser.ConfigParser()
        
        self.config['SIM_TIME'] = {
                    'start' : '',
                    'end' : ''
        }
            
        self.config['FILES'] = { 
                'input' : '',
                'dem' : '',
                'demtif' : '',
                'clone' : '',
                'lddTif' : '',
                'etp' : '',
                'prec' : '',
                'ndvi' : '',
                'kp' : '',
                'landuse' : '',
                'solo' : '',
                'output' : '',
                'samples' : '',
                'etpFilePrefix' : '',
                'precFilePrefix' : '',
                'ndviFilePrefix' : '',  
                'ndvimax' : '', 
                'ndvimin' : '', 
                'kpFilePrefix' : '',
                'landuseFilePrefix' : ''
        }
        self.config['PARAMETERS'] = {
                'rainydays' : '',
                'a_i' : '',
                'a_o' : '',
                'a_s' : '',
                'a_v' : '',
                'manning' : '',
                'dg' : '',
                'kr' : '',
                'capCampo' : '',
                'porosidade' : '',
                'saturacao' : '',
                'pontomurcha' : '',
                'zr' : '',
                'kcmin' : '',
                'kcmax' : ''
        }
        self.config['GRID'] = {
                'grid' : ''
        }
        self.config['CALIBRATION'] = {
                'alfa' : '',
                'b' : '',
                'w1' : '',
                'w2' : '',
                'w3' : '',
                'rcd' : '',
                'f' : '',
                'alfa_gw' : '',
                'x' : ''
        }
        self.config['INITIAL SOIL CONDITIONS'] = {
                'ftur_ini' : '',
                'eb_ini' : '',
                'eb_lim' : '',
                'tus_ini' : ''
        }
        self.config['CONSTANT'] = {
                'fpar_max' : '',
                'fpar_min' : '',
                'lai_max' : '',
                'i_imp' : ''
        }
        self.config['GENERATE_FILE'] = {
                'Int' : 'True', 
                'Eb' : 'True',
                'Esd' : 'False',
                'Evp' : 'False',
                'Lf' : 'False',
                'Rec' : 'False', 
                'Tur' : 'False', 
                'Vazao' : 'False',
                'auxQtot' : 'False', 
                'auxRec' : 'False'
        } 

    def getDirectoryPath(self, caption):
        """Gets the path of an existing directory using QFileDialog and returns it.

        :param caption: This is the title of the file selection window. 
        :type caption: String

        :returns: Directory path selected by the user.
        :rtype: String
        """
        directoryPath = QFileDialog.getExistingDirectory(self, caption=caption, directory=self.lastOpenedDirectory)
        return directoryPath

    def getFilePath(self, caption, filter):
        """Gets the path of an existing file using QFileDialog and returns it.    

        :param caption: This is the title of the file selection window. 
        :type caption: String
        
        :param filter: Only files that match the given filter are shown.
        :type filter: String

        :returns: File path selected by the user.
        :rtype: String        
        """        
        filePath, _ = QFileDialog.getOpenFileName(self, caption=caption, directory=self.lastOpenedDirectory, initialFilter=filter)
        return filePath 

    def splitDirFilePrefix(self, filePath):
        """Split directory path and file prefix from file path.

        Adds trailing separator to directory path (OS-agnostic).

        :param filePath: File path.
        :filePath type: String

        :returns: Directory path with trailing separator and file prefix
        :rtype: str, str
        """
        # Split directory path from file name with extension
        directoryPath, fileName = os.path.split(filePath)
        # Split extension from file name
        filePrefix, _ = os.path.splitext(fileName)         
        return f'{directoryPath}/', ''.join(filter(str.isalpha, filePrefix))

    # Project Folder
    def setInputDirectoryPath(self):
        """Defines the directory containing the project's input data.
        
        :Slot signal: clicked
        :Signal sender: toolButton_InputFolder
        """    
        directoryPath = self.getDirectoryPath(caption="Select Input Directory")
        self.config['FILES']['input'] = directoryPath
        self.lineEdt_InputFolder.setText(directoryPath)

        #TODO: Create dialog message to ask if the user want to load the config.ini
        #       file found in the parend directory
        # Check if parent directory has a config.ini file and load it
        # path = Path(directoryPath)
        # configFilePath = os.path.join(path.parent.absolute(), 'config.ini')
        # if os.path.isfile(configFilePath):
        #     self.loadConfigFromFile(configFilePath)

    def setOutputDirectoryPath(self):
        """Defines the directory containing the project's output data.
        
        :Slot signal: clicked
        :Signal sender: toolButton_OutputFolder
        """              
        directoryPath = self.getDirectoryPath(caption="Select Output Directory")
        self.config['FILES']['output'] = directoryPath
        self.lineEdt_OutputFolder.setText(directoryPath)

    # Tab widget
    ## Settings tab
    ### Model General Settings
    def setDEMFilePath(self):
        """Defines the project's DEM map file.
        
        Also updates the lineEdt_Dem field with the selected file path.
        
        :Slot signal: clicked
        :Signal sender: btn_Dem        
        """            
        filePath = self.getFilePath(caption="Select DEM map File", filter="*.map")
        self.config['FILES']['dem'] = filePath
        self.lineEdt_Dem.setText(filePath)

    def setCloneFilePath(self):
        """Defines the project's Clone file.
        
        Also updates the lineEdt_Clone field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_Clone        
        """                    
        filePath = self.getFilePath(caption="Select Clone File", filter="*.map")
        self.config['FILES']['clone'] = filePath
        self.lineEdt_Clone.setText(filePath)     

    def setExportSampleLocations(self):
        """Defines as enabled the fields related to the Sample file.
        
        Fields: lineEdt_Sample, btn_Sample and label_SelectSample.
        
        :Slot signal: checked
        :Signal sender: checkBox_Sample     
        """
        if self.checkBox_Sample.isChecked(): 
            self.lineEdt_Sample.setEnabled(True)
            self.btn_Sample.setEnabled(True)
            self.label_SelectSample.setEnabled(True)
        else:
            self.lineEdt_Sample.setEnabled(False)
            self.btn_Sample.setEnabled(False) 
            self.label_SelectSample.setEnabled(False)      

    def setSampleFilePath(self):
        """Defines the project's Sample file.
        
        Also updates the lineEdt_Sample field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_Sample        
        """  
        filePath = self.getFilePath(caption="Select Sample File", filter="CSV files (*.csv);;Text files (*.txt)")
        self.config['FILES']['samples'] = filePath         
        self.lineEdt_Sample.setText(filePath)                

    def setGridSize(self):
        """Defines the project's Grid size.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_GridSize        
        """    
        self.config['GRID']['grid'] = str(self.doubleSpinBox_GridSize.value())

    ### Simulation Period
    def setStartSimulationPeriod(self):
        """Defines the start date of the model simulation period. 
        
        Follows the format 'dd/MM/yyyy'.
                
        :Slot signal: editingFinished
        :Signal sender: dtEdt_StartSim        
        """ 
        self.config['SIM_TIME']['start'] = self.dtEdt_StartSim.date().toString('dd/MM/yyyy')
    
    def setEndSimulationPeriod(self):
        """Defines the end date of the model simulation period. 
        
        Follows the format 'dd/MM/yyyy'. 
                
        :Slot signal: editingFinished
        :Signal sender: dtEdt_EndSim        
        """ 
        self.config['SIM_TIME']['end'] = self.dtEdt_EndSim.date().toString('dd/MM/yyyy')

    ## Soil tab
    ### Soil Parameters
    def setSoilMapFilePath(self):
        """Defines the project's Soil Map file.
        
        Also updates the lineEdt_SoilMap field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_SoilMap        
        """            
        filePath = self.getFilePath(caption="Select Soil Map File", filter="*.map")
        self.config['FILES']['solo'] = filePath 
        self.lineEdt_SoilMap.setText(filePath)  

    def setDensityFilePath(self):
        """Defines the project's Density file.
        
        Also updates the lineEdt_DensityDg field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_DensityDg        
        """    
        filePath = self.getFilePath(caption="Select Density File", filter="*.map")
        self.config['PARAMETERS']['dg'] = filePath            
        self.lineEdt_DensityDg.setText(filePath)  

    def setHydraulicConductivityFilePath(self):
        """Defines the project's HydraulicConductivity file.
        
        Also updates the lineEdt_HydraulicConductivityKr field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_HydraulicConductivityKr       
        """     
        filePath = self.getFilePath(caption="Select Hydraulic Conductivity File", filter="*.map")
        self.config['PARAMETERS']['kr'] = filePath     
        self.lineEdt_HydraulicConductivityKr.setText(filePath)  

    def setFieldCapacityFilePath(self):
        """Defines the project's Field Capacity file.
        
        Also updates the lineEdt_FieldCapacityCC field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_FieldCapacityCC        
        """         
        filePath = self.getFilePath(caption="Select Field Capacity File", filter="*.map")
        self.config['PARAMETERS']['capCampo'] = filePath
        self.lineEdt_FieldCapacityCC.setText(filePath) 

    def setWiltingPointFilePath(self):
        """Defines the project's Wilting Point file.
        
        Also updates the lineEdt_WiltingPointWP field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_WiltingPointWP        
        """              
        filePath = self.getFilePath(caption="Select Wilting Point File", filter="*.map")
        self.config['PARAMETERS']['pontomurcha'] = filePath
        self.lineEdt_WiltingPointWP.setText(filePath) 

    def setPorosityFilePath(self):
        """Defines the project's Porosity file.
        
        Also updates the lineEdt_Porosity field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_Porosity        
        """           
        filePath = self.getFilePath(caption="Select Porosity File", filter="*.map")
        self.config['PARAMETERS']['porosidade'] = filePath
        self.lineEdt_Porosity.setText(filePath) 

    def setSaturationFilePath(self):
        """Defines the project's Saturation file.
        
        Also updates the lineEdt_Saturation field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_Saturation        
        """         
        filePath = self.getFilePath(caption="Select Saturation File", filter="*.map")
        self.config['PARAMETERS']['saturacao'] = filePath
        self.lineEdt_Saturation.setText(filePath) 

    def setRootZoneThicknessFilePath(self):
        """Defines the project's Root Zone Thickness file.
        
        Also updates the lineEdt_RootZoneThicknessZr field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_RootZoneThicknessZr        
        """         
        filePath = self.getFilePath(caption="Select Root Zone Thickness File", filter="*.map")
        self.config['PARAMETERS']['zr'] = filePath
        self.lineEdt_RootZoneThicknessZr.setText(filePath) 

    ### Initial Soil Conditions
    def setInitialSoilMoisture(self):
        """Defines the project's Initial soil moisture value in millimeters.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_InitialSoilMoisture           
        """ 
        self.config['INITIAL SOIL CONDITIONS']['ftur_ini'] = str(self.doubleSpinBox_InitialSoilMoisture.value())      

    def setInitialBaseFlow(self):
        """Defines the project's Initial Base Flow value in millimeters.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_BaseFlowInitial           
        """
        self.config['INITIAL SOIL CONDITIONS']['eb_ini'] = str(self.doubleSpinBox_BaseFlowInitial.value())  

    def setBaseFlowLimit(self):
        """Defines the project's Base Flow Limit value in millimeters.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_BaseFlowLimit           
        """
        self.config['INITIAL SOIL CONDITIONS']['eb_lim'] = str(self.doubleSpinBox_BaseFlowLimit.value())   

    def setInitialTus(self):
        """Defines the project's Initial Tus value in millimeters.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_TusInitial           
        """
        self.config['INITIAL SOIL CONDITIONS']['tus_ini'] = str(self.doubleSpinBox_TusInitial.value()) 

    ## Land Use tab
    ### Land Use Series
    def setLandUseSeriesFilePath(self):
        """Defines the project's Land Use Series file folder. 
        
        Also updates the lineEdt_LandUseSeries field with the selected file path and set land use file prefix.
                
        :Slot signal: clicked
        :Signal sender: btn_LandUseSeries        
        """    
        filePath = self.getFilePath(caption="Select Land Use Series File", filter="*.001")
        self.config['FILES']['landuse'], self.config['FILES']['landuseFilePrefix'] = self.splitDirFilePrefix(filePath)              
        self.lineEdt_LandUseSeries.setText(filePath) 

    ### NDVI
    def setNDVISeriesFilePath(self):
        """Defines the project's NDVISeries file folder. 
        
        Also updates the lineEdt_NDVISeries field with the selected file path and define the ndvi file prefix.
                
        :Slot signal: clicked
        :Signal sender: btn_NDVISeries        
        """             
        filePath = self.getFilePath(caption="Select NDVI Series File", filter="*.001")
        self.config['FILES']['ndvi'], self.config['FILES']['ndviFilePrefix'] = self.splitDirFilePrefix(filePath)          
        self.lineEdt_NDVISeries.setText(filePath)     

    def setNDVIMaximumSeriesFilePath(self):
        """Defines the project's NDVIMax file. 
        
        Also updates the lineEdt_NDVIMax field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_NDVIMax        
        """               
        filePath = self.getFilePath(caption="Select Maximum NDVI Series File", filter="CSV files (*.csv);;Text files (*.txt)")
        self.config['FILES']['ndvimax'] = filePath 
        self.lineEdt_NDVIMax.setText(filePath)         

    def setNDVIMinimumSeriesFilePath(self):
        """Defines the project's NDVIMin file. 
        
        Also updates the lineEdt_NDVIMin field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_NDVIMin        
        """           
        filePath = self.getFilePath(caption="Select Minimum NDVI Series File", filter="CSV files (*.csv);;Text files (*.txt)")
        self.config['FILES']['ndvimin'] = filePath
        self.lineEdt_NDVIMin.setText(filePath)    

    ### a
    def setAiFilePath(self):
        """Defines the project's a_i file. 
        
        Also updates the lineEdt_a_i field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_a_i        
        """           
        filePath = self.getFilePath(caption="Select a_i File", filter="CSV files (*.csv);;Text files (*.txt)")
        self.config['PARAMETERS']['a_i'] = filePath
        self.lineEdt_a_i.setText(filePath)     

    def setAoFilePath(self):
        """Defines the project's a_o file. 
        
        Also updates the lineEdt_a_o field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_a_o        
        """              
        filePath = self.getFilePath(caption="Select a_o File", filter="CSV files (*.csv);;Text files (*.txt)")       
        self.config['PARAMETERS']['a_o'] = filePath
        self.lineEdt_a_o.setText(filePath)               

    def setAsFilePath(self):
        """Defines the project's a_s file. 
        
        Also updates the lineEdt_a_s field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_a_s        
        """           
        filePath = self.getFilePath(caption="Select a_s File", filter="CSV files (*.csv);;Text files (*.txt)")
        self.config['PARAMETERS']['a_s'] = filePath
        self.lineEdt_a_s.setText(filePath)   

    def setAvFilePath(self):
        """Defines the project's a_v file. 
        
        Also updates the lineEdt_a_v field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_a_v        
        """          
        filePath = self.getFilePath(caption="Select a_v File", filter="CSV files (*.csv);;Text files (*.txt)")
        self.config['PARAMETERS']['a_v'] = filePath
        self.lineEdt_a_v.setText(filePath) 

    ### Manning
    def setManningFilePath(self):
        """Defines the project's Manning file. 
        
        Also updates the lineEdt_Manning field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_Manning        
        """               
        filePath = self.getFilePath(caption="Select Manning File", filter="CSV files (*.csv);;Text files (*.txt)")
        self.config['PARAMETERS']['manning'] = filePath
        self.lineEdt_Manning.setText(filePath)
                

    ### Kc
    def setKcMaximumFilePath(self):
        """Defines the project's KcMax file. 
        
        Also updates the lineEdt_KcMax field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_KcMax        
        """     
        filePath = self.getFilePath(caption="Select Kc Maximum File", filter="CSV files (*.csv);;Text files (*.txt)")
        self.config['PARAMETERS']['kcmax'] = filePath      
        self.lineEdt_KcMax.setText(filePath)         

    def setKcMinimumFilePath(self):
        """Defines the project's KcMin file. 
        
        Also updates the lineEdt_KcMin field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_KcMin        
        """    
        filePath = self.getFilePath(caption="Select Kc Minimum File", filter="CSV files (*.csv);;Text files (*.txt)")
        self.config['PARAMETERS']['kcmin'] = filePath             
        self.lineEdt_KcMin.setText(filePath)    

    ### Fpar
    def setFparMaximum(self):
        """Defines the project's Fpar Maximum value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_FparMax        
        """  
        self.config['CONSTANT']['fpar_max'] = str(self.doubleSpinBox_FparMax.value())     

    def setFparMinimum(self):
        """Defines the project's Fpar Minimum value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_FparMin        
        """  
        self.config['CONSTANT']['fpar_min'] = str(self.doubleSpinBox_FparMin.value())  

    ### Interception
    def setInterception(self):
        """Defines the project's Interception value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_Interception        
        """  
        self.config['CONSTANT']['i_imp'] = str(self.doubleSpinBox_Interception.value())  

    # Leaf Area Index
    def setLeafAreaIndexMaximum(self):
        """Defines the project's Maximum Leaf Area Index value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_LeafAreaIndexMax        
        """  
        self.config['CONSTANT']['lai_max'] = str(self.doubleSpinBox_LeafAreaIndexMax.value())  

    # Climate tab
    def setPrecipitationSeriesFilePath(self):
        """Defines the project's Precipitation folder file. 
        
        Alsochange the lineEdt_Precipitation field with the selected file path and define the prec file prefix.
                
        :Slot signal: clicked
        :Signal sender: btn_Precipitation        
        """          
        filePath = self.getFilePath(caption="Select Precipitation Series File", filter="*.001")
        self.config['FILES']['prec'], self.config['FILES']['precFilePrefix'] = self.splitDirFilePrefix(filePath) 
        self.lineEdt_Precipitation.setText(filePath)     

    def setEvapotranspirationSeriesFilePath(self):
        """Defines the project's Evapotranspiration folder file. 
        
        Also updates the lineEdt_EvapoTranspiration field with the selected file path and define the etp file prefix.
                
        :Slot signal: clicked
        :Signal sender: btn_EvapoTranspiration        
        """              
        filePath = self.getFilePath(caption="Select Evapotranspiration Series File", filter="*.001")
        self.config['FILES']['etp'], self.config['FILES']['etpFilePrefix'] = self.splitDirFilePrefix(filePath)
        self.lineEdt_EvapoTranspiration.setText(filePath)     

    def setKpSeriesFilePath(self):
        """Defines the project's Pan Coefficient (Kp) folder file. 
        
        Also updates the lineEdt_PanCoefficientKp field with the selected file path and define the Kp file prefix.
                
        :Slot signal: clicked
        :Signal sender: btn_PanCoefficientKp        
        """           
        filePath = self.getFilePath(caption="Select Kp Series File", filter="*.001")
        directoryPath, fileName = os.path.split(filePath)
        self.config['FILES']['kp'], self.config['FILES']['kpFilePrefix'] = self.splitDirFilePrefix(filePath)        
        self.lineEdt_PanCoefficientKp.setText(filePath) 

    def setRainyDaysSeriesFilePath(self):
        """Defines the project's Rainy Days file. 
        
        Alsod change the lineEdt_RainyDays field with the selected file path.
                
        :Slot signal: clicked
        :Signal sender: btn_RainyDays        
        """           
        filePath = self.getFilePath(caption="Select Rainy Days Series File", filter="CSV files (*.csv);;Text files (*.txt)")
        self.config['PARAMETERS']['rainydays'] = filePath
        self.lineEdt_RainyDays.setText(filePath) 

    ## Parameters tab
    ### Model Parameters
    def setExponentCh(self):
        """Defines the project's Exponent of Ch value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_ExponentCh        
        """ 
        self.config['CALIBRATION']['b'] = str(self.doubleSpinBox_ExponentCh.value()) 

    def setDelayFactor(self):
        """Defines the project's Delay Factor value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_DelayFactor        
        """
        self.config['CALIBRATION']['x'] = str(self.doubleSpinBox_DelayFactor.value()) 

    def setRegionalConsecutiveDrynessLevel(self):
        """Defines the project's Regional Consecutive Dryness (RCD) Level value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_RegionalConsecutiveDrynessLevel        
        """
        self.config['CALIBRATION']['rcd'] = str(self.doubleSpinBox_RegionalConsecutiveDrynessLevel.value())         

    def setDelayCoefficientBaseFlow(self):
        """Defines the project's Delay Coefficient Base Flow value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_DelayCoefficientBaseFlow        
        """
        self.config['CALIBRATION']['alfa_gw'] = str(self.doubleSpinBox_DelayCoefficientBaseFlow.value())         

    def setPartitioningCoefficientRelated(self):
        """Defines the project's Partitioning Coefficient Related value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_PartitioningCoefficientRelatedSoil        
        """
        self.config['CALIBRATION']['f'] = str(self.doubleSpinBox_PartitioningCoefficientRelatedSoil.value()) 

    def setInterceptionCalibration(self):
        """Defines the project's Interception Calibration value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_InterceptionCalibrationAlpha        
        """
        self.config['CALIBRATION']['alfa'] = str(self.doubleSpinBox_InterceptionCalibrationAlpha.value()) 

    #### Weight Factors
    def setManningRelatedWeightFactor(self):
        """Defines the project's Manning Related Weight Factor (w1) value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_ManningRelatedWeightFactor        
        """
        self.config['CALIBRATION']['w1'] = str(self.doubleSpinBox_ManningRelatedWeightFactor.value())  
    
    def setSoilRelatedWeightFactor(self):
        """Defines the project's Soil Related Weight Factor (w2) value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_SoilRelatedWeightFactor        
        """
        self.config['CALIBRATION']['w2'] = str(self.doubleSpinBox_SoilRelatedWeightFactor.value())             

    def setSlopeRelatedWeightFactor(self):
        """Defines the project's Slope Related Weight Factor (w3) value.
                
        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_SlopeRelatedWeightFactor        
        """
        self.config['CALIBRATION']['w3'] = str(self.doubleSpinBox_SlopeRelatedWeightFactor.value()) 

    ## Run tab
    ### Geneate Files
    def setInterceptionGenerateFile(self):
        """Defines whether the Interception file will be generated as 
            output from the model execution.
        
        :Slot signal: checked
        :Signal sender: checkBox_InterceptionInt     
        """        
        self.config['GENERATE_FILE']['Int'] = str(self.checkBox_InterceptionInt.isChecked())  

    def setInterceptionEbGenerateFile(self):
        """Defines whether the Interception Eb file will be generated as 
            output from the model execution.
        
        :Slot signal: checked
        :Signal sender: checkBox_InterceptionEb     
        """        
        self.config['GENERATE_FILE']['Eb'] = str(self.checkBox_InterceptionEb.isChecked())  

    def setEvapotranspirationGenerateFile(self):
        """Defines whether the Evapotranspiration file will be generated as 
            output from the model execution.
        
        :Slot signal: checked
        :Signal sender: checkBox_EvapotranspirationEvp     
        """        
        self.config['GENERATE_FILE']['Evp'] = str(self.checkBox_EvapotranspirationEvp.isChecked())   

    def setRechargeGenerateFile(self):
        """Defines whether the Recharge file will be generated as 
            output from the model execution.
        
        :Slot signal: checked
        :Signal sender: checkBox_RechargeRec     
        """        
        self.config['GENERATE_FILE']['Rec'] = str(self.checkBox_RechargeRec.isChecked())                           

    def setSoilMoistureGenerateFile(self):
        """Defines whether the Soil Moisture file will be generated as 
            output from the model execution.
        
        :Slot signal: checked
        :Signal sender: checkBox_SoilMoistureTur     
        """        
        self.config['GENERATE_FILE']['Tur'] = str(self.checkBox_SoilMoistureTur.isChecked())   

    def setLateralFLowGenerateFile(self):
        """Defines whether the Lateral FLow file will be generated as 
            output from the model execution.
        
        :Slot signal: checked
        :Signal sender: checkBox_LateralFlowLf     
        """        
        self.config['GENERATE_FILE']['Lf'] = str(self.checkBox_LateralFlowLf.isChecked())   

    def setRunoffEsdGenerateFile(self):
        """Defines whether the Runoff Esd file will be generated as 
            output from the model execution.
        
        :Slot signal: checked
        :Signal sender: checkBox_RunoffEsd     
        """        
        self.config['GENERATE_FILE']['Esd'] = str(self.checkBox_RunoffEsd.isChecked())   

    #TODO: Rename setRunoffVazaoGenerateFile, checkBox_RunoffVazao, GUI and config section GENERATE_FILES option Vazao
    def setRunoffVazaoGenerateFile(self):
        """Defines whether the Runoff Vazao file will be generated as 
            output from the model execution.
        
        :Slot signal: checked
        :Signal sender: checkBox_RunoffVazao     
        """        
        self.config['GENERATE_FILE']['Vazao'] = str(self.checkBox_RunoffVazao.isChecked()) 

    #TODO: Rename setAuxQtotGenerateFile and checkBox_auxQtot
    # def setAuxQtotGenerateFile(self):
        # """Defines whether the AuxQtot file will be generated as 
        #     output from the model execution.
        
        # :Slot signal: checked
        # :Signal sender: checkBox_auxQtot     
        # """        
    #     self.config['GENERATE_FILE']['auxQtot'] = str(self.checkBox_auxQtot.isChecked()) 

    #TODO: Rename setAuxRecGenerateFile and checkBox_auxRec
    # def setAuxRecGenerateFile(self):
        # """Defines whether the AuxRec file will be generated as 
        #     output from the model execution.
        
        # :Slot signal: checked
        # :Signal sender: checkBox_auxRec     
        # """        
    #     self.config['GENERATE_FILE']['auxRec'] = str(self.checkBox_auxRec.isChecked())         

    def updateConfigFromGUI(self):  
        """Updates the configuration dictionary with the values present in the GUI's data entry objects."""

        self.textBrowser_log.append("Updating configuration with current values...")
        
        # Project Folder
        self.config['FILES']['input'] = self.lineEdt_InputFolder.text()
        self.config['FILES']['output'] = self.lineEdt_OutputFolder.text()

        # Tab widget
        ## Settings tab
        ### Model General Settings
        self.config['FILES']['dem'] = self.lineEdt_Dem.text()
        self.config['FILES']['demtif'] = self.lineEdt_DemTif.text()
        self.config['FILES']['clone'] = self.lineEdt_Clone.text()     

        if self.checkBox_Sample.isChecked(): 
            self.config['FILES']['samples'] = self.lineEdt_Sample.text()                
        
        ### Grid Size
        self.config['GRID']['grid'] = str(self.doubleSpinBox_GridSize.value())

        ### Simulation Period
        self.config['SIM_TIME']['start'] = self.dtEdt_StartSim.date().toString('dd/MM/yyyy')
        self.config['SIM_TIME']['end'] = self.dtEdt_EndSim.date().toString('dd/MM/yyyy')

        ## Soil tab
        ### Soil Parameters
        self.config['FILES']['solo'] = self.lineEdt_SoilMap.text()  
        self.config['PARAMETERS']['dg'] = self.lineEdt_DensityDg.text()  
        self.config['PARAMETERS']['kr'] = self.lineEdt_HydraulicConductivityKr.text()  

        self.config['PARAMETERS']['capCampo'] = self.lineEdt_FieldCapacityCC.text() 
        self.config['PARAMETERS']['pontomurcha'] = self.lineEdt_WiltingPointWP.text() 
        self.config['PARAMETERS']['porosidade'] = self.lineEdt_Porosity.text() 
        self.config['PARAMETERS']['saturacao'] = self.lineEdt_Saturation.text() 
        self.config['PARAMETERS']['zr'] = self.lineEdt_RootZoneThicknessZr.text() 

        ### Initial Soil Conditions
        self.config['INITIAL SOIL CONDITIONS']['ftur_ini'] = str(self.doubleSpinBox_InitialSoilMoisture.value())      
        self.config['INITIAL SOIL CONDITIONS']['eb_ini'] = str(self.doubleSpinBox_BaseFlowInitial.value())  
        self.config['INITIAL SOIL CONDITIONS']['eb_lim'] = str(self.doubleSpinBox_BaseFlowLimit.value())   
        self.config['INITIAL SOIL CONDITIONS']['tus_ini'] = str(self.doubleSpinBox_TusInitial.value()) 

        ## Land Use tab
        ### Land Use Series
        self.config['FILES']['landuse'], self.config['FILES']['landuseFilePrefix'] = self.splitDirFilePrefix(self.lineEdt_LandUseSeries.text())
        self.config['FILES']['ndvi'], self.config['FILES']['ndviFilePrefix'] = self.splitDirFilePrefix(self.lineEdt_NDVISeries.text())     
        self.config['FILES']['ndvimax'] = self.lineEdt_NDVIMax.text()          
        self.config['FILES']['ndvimin'] = self.lineEdt_NDVIMin.text()    

        ### a
        self.config['PARAMETERS']['a_i'] = self.lineEdt_a_i.text()        
        self.config['PARAMETERS']['a_o'] = self.lineEdt_a_o.text()               
        self.config['PARAMETERS']['a_s'] = self.lineEdt_a_s.text()   
        self.config['PARAMETERS']['a_v'] = self.lineEdt_a_v.text() 

        ### Manning
        self.config['PARAMETERS']['manning'] = self.lineEdt_Manning.text()
      
        ### Kc
        self.config['PARAMETERS']['kcmax'] = self.lineEdt_KcMax.text()        
        self.config['PARAMETERS']['kcmin'] = self.lineEdt_KcMin.text()              

        ### Fpar
        self.config['CONSTANT']['fpar_max'] = str(self.doubleSpinBox_FparMax.value())     
        self.config['CONSTANT']['fpar_min'] = str(self.doubleSpinBox_FparMin.value())  


        ### Interception
        self.config['CONSTANT']['i_imp'] = str(self.doubleSpinBox_Interception.value())  

        ### Leaf Area Index
        self.config['CONSTANT']['lai_max'] = str(self.doubleSpinBox_LeafAreaIndexMax.value())  

        ## Climate tab
        self.config['FILES']['prec'], self.config['FILES']['precFilePrefix'] = self.splitDirFilePrefix(self.lineEdt_Precipitation.text())          
        self.config['FILES']['etp'], self.config['FILES']['etpFilePrefix'] = self.splitDirFilePrefix(self.lineEdt_EvapoTranspiration.text())      
        self.config['FILES']['kp'], self.config['FILES']['kpFilePrefix'] = self.splitDirFilePrefix(self.lineEdt_PanCoefficientKp.text())     
        self.config['PARAMETERS']['rainydays'] = self.lineEdt_RainyDays.text()

        ## Parameters tab
        ### Model Parameters
        self.config['CALIBRATION']['b'] = str(self.doubleSpinBox_ExponentCh.value()) 
        self.config['CALIBRATION']['x'] = str(self.doubleSpinBox_DelayFactor.value()) 
        self.config['CALIBRATION']['rcd'] = str(self.doubleSpinBox_RegionalConsecutiveDrynessLevel.value())         
        self.config['CALIBRATION']['alfa_gw'] = str(self.doubleSpinBox_DelayCoefficientBaseFlow.value())         
        self.config['CALIBRATION']['f'] = str(self.doubleSpinBox_PartitioningCoefficientRelatedSoil.value()) 
        self.config['CALIBRATION']['alfa'] = str(self.doubleSpinBox_InterceptionCalibrationAlpha.value()) 

        ### Weight Factors
        self.config['CALIBRATION']['w1'] = str(self.doubleSpinBox_ManningRelatedWeightFactor.value())  
        self.config['CALIBRATION']['w2'] = str(self.doubleSpinBox_SoilRelatedWeightFactor.value())             
        self.config['CALIBRATION']['w3'] = str(self.doubleSpinBox_SlopeRelatedWeightFactor.value()) 

        ## Run tab
        ### Geneate Files
        self.config['GENERATE_FILE']['Int'] = str(self.checkBox_InterceptionInt.isChecked())  
        self.config['GENERATE_FILE']['Eb'] = str(self.checkBox_InterceptionEb.isChecked())  
        self.config['GENERATE_FILE']['Evp'] = str(self.checkBox_EvapotranspirationEvp.isChecked())   
        self.config['GENERATE_FILE']['Rec'] = str(self.checkBox_RechargeRec.isChecked())                           
        self.config['GENERATE_FILE']['Tur'] = str(self.checkBox_SoilMoistureTur.isChecked())   
        self.config['GENERATE_FILE']['Lf'] = str(self.checkBox_LateralFlowLf.isChecked())   
        self.config['GENERATE_FILE']['Esd'] = str(self.checkBox_RunoffEsd.isChecked())   
        self.config['GENERATE_FILE']['Vazao'] = str(self.checkBox_RunoffVazao.isChecked()) 
        # self.config['GENERATE_FILE']['auxQtot'] = str(self.checkBox_auxQtot.isChecked()) 
        # self.config['GENERATE_FILE']['auxRec'] = str(self.checkBox_auxRec.isChecked()) 
        
        self.textBrowser_log.append("Configuration updated with current values")      

    def loadConfigFromFile(self, configFilePath):
        """Reads the configuration file argument and sets the values of 
            the GUI's data entry objects to those contained in the file.

        :param configFilePath: Valid path to the configuration file.
        :type configFilePath: String
        """
        self.textBrowser_log.append("Loading configurations from file " + configFilePath + ' ...')
        
        with open(configFilePath, 'r') as configfile:
            self.config.read_file(configfile)
            configfile.close()  

        # Project Folder
        self.lineEdt_InputFolder.setText(self.config['FILES']['input'])
        self.lineEdt_OutputFolder.setText(self.config['FILES']['output'])

        # Tab widget
        ## Settings tab
        ### Model General Settings
        self.lineEdt_Dem.setText(self.config['FILES']['dem'])
        self.lineEdt_DemTif.setText(self.config['FILES']['demtif'])
        self.lineEdt_Clone.setText(self.config['FILES']['clone'])     
       
        if self.config['FILES']['samples']:
            self.checkBox_Sample.setChecked(True)
            self.lineEdt_Sample.setText(self.config['FILES']['samples'])

        self.doubleSpinBox_GridSize.setValue(self.config.getfloat('GRID','grid'))   
        self.dtEdt_StartSim.date().fromString(self.config['SIM_TIME']['start'], 'dd/MM/yyyy')
        self.dtEdt_EndSim.date().fromString(self.config['SIM_TIME']['end'], 'dd/MM/yyyy')

        ## Soil tab
        ### Soil Parameters 
        self.lineEdt_SoilMap.setText(self.config['FILES']['solo'])  
        self.lineEdt_DensityDg.setText(self.config['PARAMETERS']['dg'])  
        self.lineEdt_HydraulicConductivityKr.setText(self.config['PARAMETERS']['kr'])  
        self.lineEdt_FieldCapacityCC.setText(self.config['PARAMETERS']['capCampo']) 
        self.lineEdt_WiltingPointWP.setText(self.config['PARAMETERS']['pontomurcha']) 
        self.lineEdt_Porosity.setText(self.config['PARAMETERS']['porosidade']) 
        self.lineEdt_Saturation.setText(self.config['PARAMETERS']['saturacao']) 
        self.lineEdt_RootZoneThicknessZr.setText(self.config['PARAMETERS']['zr']) 

        ### Initial Soil Conditions
        self.doubleSpinBox_InitialSoilMoisture.setValue(self.config.getfloat('INITIAL SOIL CONDITIONS','ftur_ini'))      
        self.doubleSpinBox_BaseFlowInitial.setValue(self.config.getfloat('INITIAL SOIL CONDITIONS','eb_ini'))  
        self.doubleSpinBox_BaseFlowLimit.setValue(self.config.getfloat('INITIAL SOIL CONDITIONS','eb_lim'))   
        self.doubleSpinBox_TusInitial.setValue(self.config.getfloat('INITIAL SOIL CONDITIONS','tus_ini')) 

        ## Land Use tab
        ### Land Use Series       
        self.lineEdt_LandUseSeries.setText(self.config['FILES']['landuse']) 

        ### NDVI
        self.lineEdt_NDVISeries.setText(self.config['FILES']['ndvi'])     
        self.lineEdt_NDVIMax.setText(self.config['FILES']['ndvimax'])          
        self.lineEdt_NDVIMin.setText(self.config['FILES']['ndvimin'])    

        ### a
        self.lineEdt_a_i.setText(self.config['PARAMETERS']['a_i'])     
        self.lineEdt_a_o.setText(self.config['PARAMETERS']['a_o'])               
        self.lineEdt_a_s.setText(self.config['PARAMETERS']['a_s'])   
        self.lineEdt_a_v.setText(self.config['PARAMETERS']['a_v']) 

        ### Manning
        self.lineEdt_Manning.setText(self.config['PARAMETERS']['manning'])
                
        ### Kc     
        self.lineEdt_KcMax.setText(self.config['PARAMETERS']['kcmax'])         
        self.lineEdt_KcMin.setText(self.config['PARAMETERS']['kcmin'])    

        ### Fpar
        self.doubleSpinBox_FparMax.setValue(self.config.getfloat('CONSTANT','fpar_max'))    
        self.doubleSpinBox_FparMin.setValue(self.config.getfloat('CONSTANT','fpar_min'))  

        ### Interception
        self.doubleSpinBox_Interception.setValue(self.config.getfloat('CONSTANT','i_imp'))  

        ### Leaf Area Index
        self.doubleSpinBox_LeafAreaIndexMax.setValue(self.config.getfloat('CONSTANT','lai_max'))  

        ## Climate tab
        self.lineEdt_Precipitation.setText(self.config['FILES']['prec'])     
        self.lineEdt_EvapoTranspiration.setText(self.config['FILES']['etp'])     
        self.lineEdt_PanCoefficientKp.setText(self.config['FILES']['kp']) 
        self.lineEdt_RainyDays.setText(self.config['PARAMETERS']['rainydays']) 

        ## Parameters tab
        ### Model Parameters
        self.doubleSpinBox_ExponentCh.setValue(self.config.getfloat('CALIBRATION','b')) 
        self.doubleSpinBox_DelayFactor.setValue(self.config.getfloat('CALIBRATION','x')) 
        self.doubleSpinBox_RegionalConsecutiveDrynessLevel.setValue(self.config.getfloat('CALIBRATION','rcd'))         
        self.doubleSpinBox_DelayCoefficientBaseFlow.setValue(self.config.getfloat('CALIBRATION','alfa_gw'))         
        self.doubleSpinBox_PartitioningCoefficientRelatedSoil.setValue(self.config.getfloat('CALIBRATION','f')) 
        self.doubleSpinBox_InterceptionCalibrationAlpha.setValue(self.config.getfloat('CALIBRATION','alfa'))

        #### Weight Factors
        self.doubleSpinBox_ManningRelatedWeightFactor.setValue(self.config.getfloat('CALIBRATION','w1'))  
        self.doubleSpinBox_SoilRelatedWeightFactor.setValue(self.config.getfloat('CALIBRATION','w2'))             
        self.doubleSpinBox_SlopeRelatedWeightFactor.setValue(self.config.getfloat('CALIBRATION','w3')) 

        ## Run tab
        ### Generate Files
        self.checkBox_InterceptionInt.setChecked(self.config.getboolean('GENERATE_FILE','Int'))  
        self.checkBox_InterceptionEb.setChecked(self.config.getboolean('GENERATE_FILE','Eb'))  
        self.checkBox_EvapotranspirationEvp.setChecked(self.config.getboolean('GENERATE_FILE','Evp'))   
        self.checkBox_RechargeRec.setChecked(self.config.getboolean('GENERATE_FILE','Rec'))                           
        self.checkBox_SoilMoistureTur.setChecked(self.config.getboolean('GENERATE_FILE','Tur'))   
        self.checkBox_LateralFlowLf.setChecked(self.config.getboolean('GENERATE_FILE','Lf'))   
        self.checkBox_RunoffEsd.setChecked(self.config.getboolean('GENERATE_FILE','Esd'))   
        self.checkBox_RunoffVazao.setChecked(self.config.getboolean('GENERATE_FILE','Vazao')) 
        self.textBrowser_log.append("Configurations loaded")

    def saveConfigToFile(self, filePath):
        """Saves the values present in the configuration dictionary to a specified file.

        :param filePath: Valid path to the configuration file.
        :type filePath: String
        """        
        with open(filePath, 'w') as configfile:
            self.config.write(configfile)
            configfile.close()    
        self.textBrowser_log.append("Configuration file saved in " + filePath)        

    def showConfig(self):
        """Go through the settings dictionary and print the respective sections, options and 
            values in the textBrowser_log (in the 'Run' tab).
        """
        self.textBrowser_log.append("Showing current configuration:")
        for section in self.config.sections():
            self.textBrowser_log.append('[' + section + ']')
            for option in self.config.options(section):
                self.textBrowser_log.append(self.tr('\t'+ option +' = '+ self.config.get(section, option)))

    #TODO: Capture execution log fom RainfallRunoff.exe without freezing GUI
    def setRunState(self):
        """Invokes the model's standalone executable including the configuration file generated 
            from user input as an argument in the CLI.
        """
        
        # Use the directory immediately preceding the input directory to save the config.ini file
        path = Path(self.config['FILES'].get('input'))
        self.configFilePath = os.path.join(path.parent.absolute(), 'config.ini')

        # Use the standalone executable file of the model present in the plugin's root directory
        self.modelFilePath = os.path.join(self.plugin_dir, 'RainfallRunoff.exe')

        self.updateConfigFromGUI()
        self.saveConfigToFile(self.configFilePath)
        self.showConfig()

        self.textBrowser_log.append("\n# RUBEM execution started...")

        # Make command list available to execution thread
        global command
        command = [self.modelFilePath, "--configfile", self.configFilePath]
        self.runLongTask()

    def reportExecutionLog(self, outputLog):
        """Update textBrowser_log with output captured from execution"""
        self.textBrowser_log.append(outputLog.strip())

    def reportProgress(self, n):
        """Update progressBar with int representing overall progress of exec thread
        
        :Slot signal: emit(int) 
        :Signal sender: pyqtSignal(int)
        """
        self.progressBar.setValue(n)

    def runLongTask(self):
        """Configure QThread"""
        # Create a QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = Worker()
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.worker.finished.connect(self.reportExecutionLog)
        # Start the thread
        self.thread.start()

        # Final resets
        self.btn_Run.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.btn_Run.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.progressBar.setValue(0)
        )

# Create a worker class
class Worker(QObject):
    """Constructor"""
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)

    def run(self):
        """RUBEM Long-running task"""
        proc = subprocess.Popen(command, shell=True, encoding='latin-1', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        proc.wait()
        self.progress.emit(100)
        self.finished.emit(proc.communicate()[0])