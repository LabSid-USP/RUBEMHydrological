# coding=utf-8
# RUBEM Hydrological is a QGIS plugin that assists in setup the RUBEM model:
# Copyright (C) 2021 LabSid PHA EPUSP

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

"""RUBEM Hydrological plugin dialog window."""

__author__ = "LabSid PHA EPUSP"
__email__ = "rubem.hydrological@labsid.eng.br"
__copyright__ = "Copyright 2021, LabSid PHA EPUSP"
__license__ = "GPL"
__date__ = "2021-05-19"
__version__ = "1.3.2"

import configparser
import os
from glob import glob
from pathlib import Path

from qgis.core import (
    Qgis,
    QgsProject,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsLayerTreeLayer,
    QgsCoordinateReferenceSystem,
)

from qgis.gui import QgsMapToolEmitPoint, QgsMessageBar

from qgis.utils import showPluginHelp

try:
    from qgis.PyQt.QtCore import Qt, QDate, QThread, QModelIndex
    from qgis.PyQt.QtWidgets import (
        QDialog,
        QFileDialog,
        QMessageBox,
        QLabel,
        QLineEdit,
        QMessageBox,
        QDateEdit,
        QSizePolicy,
    )
    from qgis.PyQt.QtGui import QStandardItemModel
except ImportError:
    from PyQt5.QtCore import Qt, QDate, QThread, QModelIndex
    from PyQt5.QtWidgets import (
        QDialog,
        QFileDialog,
        QMessageBox,
        QLabel,
        QLineEdit,
        QMessageBox,
        QDateEdit,
        QSizePolicy,
    )
    from PyQt5.QtGui import QStandardItemModel

try:
    from .rubem_config import defaultConfigSchema
    from .rubem_hydrological_dialog_base_ui import Ui_RUBEMHydrological
    from .rubem_thread_workers import RUBEMStandaloneWorker
    from .rubem_output_item import StandardItem
    from .rubem_output_plot import plotTimeSeriesData
    from .rubem_input_validators import *
except ImportError:
    from rubem_config import defaultConfigSchema
    from rubem_hydrological_dialog_base_ui import Ui_RUBEMHydrological
    from rubem_thread_workers import RUBEMStandaloneWorker
    from rubem_output_item import StandardItem
    from rubem_output_plot import plotTimeSeriesData
    from rubem_input_validators import *


class RUBEMHydrologicalDialog(QDialog, Ui_RUBEMHydrological):
    """[summary].

    :param QDialog: [description].
    :type QDialog: [type]

    :param Ui_RUBEMHydrological: [description].
    :type Ui_RUBEMHydrological: [type]
    """

    def __init__(self, iface):
        """[summary].

        :param iface: [description].
        :type iface: [type]
        """
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface

        self.bar = QgsMessageBar(self)
        self.bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout().addWidget(self.bar, 1, Qt.AlignTop | Qt.AlignJustify)

        self.lastOpenedFile = None
        self.lastOpenedDirectory = None
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.modelFilePath = None
        self.projectFilePath = None
        self.config = configparser.ConfigParser()
        self.config.read_dict(defaultConfigSchema)

        self.pushButton_SaveProject.setDisabled(True)
        self.pushButton_SaveAsProject.setDisabled(True)
        self.tabWidget.setDisabled(True)
        self.tab_Results.setDisabled(True)

        self.hasCurrentProject = False
        self.hasProjectBeenModified = False

        self.treeView_MapSeriesData.setHeaderHidden(True)
        self.treeView_TimeSeriesData.setHeaderHidden(True)

        self.timeSeriesTreeModel = QStandardItemModel()
        self.mapSeriesTreeModel = QStandardItemModel()

        # TODO: Implement interaction with active raster layer on QGIS canvas
        # self.canvas = iface.mapCanvas()
        # self.pointTool = QgsMapToolEmitPoint(self.canvas)
        # self.pointTool.canvasClicked.connect(self.displayPoint)
        # self.canvas.setMapTool(self.pointTool)

        self.uiDirPathDict = {
            "input": (self.lineEdit_InputFolder, self.label_InputFolder),
            "output": (self.lineEdit_OutputFolder, self.label_OutputFolder),
        }

        self.uiFilePathDict = {
            "dem": (self.lineEdt_Dem, self.label_Dem, (".map")),
            "demtif": (self.lineEdt_DemTif, self.label_DemTif, (".tif", ".tiff")),
            "clone": (self.lineEdt_Clone, self.label_Clone, (".map")),
            "samples": (self.lineEdt_Sample, self.label_SelectSample, (".map")),
            # Soil tab
            # Soil Parameters
            "solo": (self.lineEdt_SoilMap, self.label_SoilMap, (".map")),
            "dg": (self.lineEdt_DensityDg, self.label_DensityDg, (".txt", ".csv")),
            "kr": (
                self.lineEdt_HydraulicConductivityKr,
                self.label_HydraulicConductivityKr,
                (".txt", ".csv"),
            ),
            "capCampo": (
                self.lineEdt_FieldCapacityCC,
                self.label_FieldCapacityCC,
                (".txt", ".csv"),
            ),
            "pontomurcha": (
                self.lineEdt_WiltingPointWP,
                self.label_WiltingPointWP,
                (".txt", ".csv"),
            ),
            "saturacao": (
                self.lineEdt_Saturation,
                self.label_Saturation,
                (".txt", ".csv"),
            ),
            "zr": (
                self.lineEdt_RootZoneThicknessZr,
                self.label_RootZoneThickNessZr,
                (".txt", ".csv"),
            ),
            # Land Use tab
            # Land Use Series
            "landuse": (
                self.lineEdt_LandUseSeries,
                self.groupBox_LandUseSeries,
                (".001"),
            ),
            # "landuseFilePrefix", tmpPrefix
            "ndvi": (self.lineEdt_NDVISeries, self.label_NDVISeries, (".001")),
            # "ndviFilePrefix", tmpPrefix
            "ndvimax": (self.lineEdt_NDVIMax, self.label_NDVIMax, (".map")),
            "ndvimin": (self.lineEdt_NDVIMin, self.label_NDVIMin, (".map")),
            # a
            "a_i": (self.lineEdt_a_i, self.label_a_i, (".txt", ".csv")),
            "a_o": (self.lineEdt_a_o, self.label_a_o, (".txt", ".csv")),
            "a_s": (self.lineEdt_a_s, self.label_a_s, (".txt", ".csv")),
            "a_v": (self.lineEdt_a_v, self.label_a_v, (".txt", ".csv")),
            # Manning
            "manning": (self.lineEdt_Manning, self.groupBox_Manning, (".txt", ".csv")),
            # Kc
            "kcmax": (self.lineEdt_KcMax, self.label_KcMax, (".txt", ".csv")),
            "kcmin": (self.lineEdt_KcMin, self.label_KcMin, (".txt", ".csv")),
            # Climate tab
            "prec": (self.lineEdt_Precipitation, self.label_Precipitation, (".001")),
            # "precFilePrefix", tmpPrefix
            "etp": (
                self.lineEdt_EvapoTranspiration,
                self.label_Evapotranspiration,
                (".001"),
            ),
            # "etpFilePrefix", tmpPrefix
            "kp": (
                self.lineEdt_PanCoefficientKp,
                self.label_PanCoefficientKp,
                (".001"),
            ),
            # "kpFilePrefix", tmpPrefix
            "rainydays": (
                self.lineEdt_RainyDays,
                self.label_RainyDays,
                (".txt", ".csv"),
            ),
        }

        self.uiGenerateFilesDict = {
            # Run tab
            # Geneate Files
            "Int": self.checkBox_InterceptionInt,
            "bflow": self.checkBox_InterceptionEb,
            "etp": self.checkBox_EvapotranspirationEvp,
            "Rec": self.checkBox_RechargeRec,
            "ssat": self.checkBox_SoilMoistureTur,
            "Lf": self.checkBox_LateralFlowLf,
            "sfrun": self.checkBox_RunoffEsd,
            "runoff": self.checkBox_RunoffVazao,
        }

        # self.uiSpinBoxDict = {
        #     # Grid Size
        #     "grid": self.doubleSpinBox_GridSize,
        #     # Initial Soil Conditions
        #     "ftur_ini": self.doubleSpinBox_InitialSoilMoisture,
        #     "eb_ini": self.doubleSpinBox_BaseFlowInitial,
        #     "eb_lim": self.doubleSpinBox_BaseFlowLimit,
        #     "tus_ini": self.doubleSpinBox_TusInitial,
        #     # Fpar
        #     "fpar_max": self.doubleSpinBox_FparMax,
        #     "fpar_min": self.doubleSpinBox_FparMin,
        #     # Interception
        #     "i_imp": self.doubleSpinBox_Interception,
        #     # Leaf Area Index
        #     "lai_max": self.doubleSpinBox_LeafAreaIndexMax,
        #     # Parameters tab
        #     # Model Parameters
        #     "b": self.doubleSpinBox_ExponentCh,
        #     "x": self.doubleSpinBox_DelayFactor,
        #     "rcd": self.doubleSpinBox_RegionalConsecutiveDrynessLevel,
        #     "alfa_gw": self.doubleSpinBox_DelayCoefficientBaseFlow,
        #     "f": self.doubleSpinBox_PartitioningCoefficientRelatedSoil,
        #     "alfa": self.doubleSpinBox_InterceptionCalibrationAlpha,
        #     # Weight Factors
        #     "w1": self.doubleSpinBox_ManningRelatedWeightFactor,
        #     "w2": self.doubleSpinBox_SoilRelatedWeightFactor,
        #     "w3": self.doubleSpinBox_SlopeRelatedWeightFactor,
        # }

        self.setupUserInputValidators()

        # TODO: Reorganize information in dictionaries
        self.mapSeriesDictFileNames = {
            "Runoff [m³/s]": "Runoff",
            "Interception [mm]": "Int",
            "Baseflow [mm]": "Bflow",
            "Surface Runoff [mm]": "SfRun",
            "ETa [mm]": "Etp",
            "Lateral Flow [mm]": "Lf",
            "Recharge [mm]": "Rec",
            "Soil Moisture Content [mm]": "Ssat",
        }

        # TODO: Reorganize information in dictionaries
        self.timeSeriesDictFileNames = {
            "Runoff [m³/s]": "outRun",
            "Interception [mm]": "outInt",
            "Baseflow [mm]": "outBflow",
            "Surface Runoff [mm]": "outSfRun",
            "ETa [mm]": "outEtp",
            "Lateral Flow [mm]": "outLf",
            "Recharge [mm]": "outRec",
            "Soil Moisture Content [mm]": "outSsat",
        }

        # TODO: Reorganize information in dictionaries. Preferably use this format.
        # ? Should this dictionary be here or in another specific location?
        self.timeSeriesDict = {
            "outRun": {
                "plot": {
                    "title": "Total Runoff",
                    "x_label": "Time Steps [month]",
                    "y_label": "Value [m³/s]",
                },
            },
            "outInt": {
                "plot": {
                    "title": "Interception",
                    "x_label": "Time Steps [month]",
                    "y_label": "Value [mm]",
                },
            },
            "outBflow": {
                "plot": {
                    "title": "Baseflow",
                    "x_label": "Time Steps [month]",
                    "y_label": "Value [mm]",
                },
            },
            "outSfRun": {
                "plot": {
                    "title": "Surface Runoff",
                    "x_label": "Time Steps [month]",
                    "y_label": "Value [mm]",
                },
            },
            "outEtp": {
                "plot": {
                    "title": "Actual Evapotranspiration",
                    "x_label": "Time Steps [month]",
                    "y_label": "Value [mm]",
                },
            },
            "outLf": {
                "plot": {
                    "title": "Lateral Flow",
                    "x_label": "Time Steps [month]",
                    "y_label": "Value [mm]",
                },
            },
            "outRec": {
                "plot": {
                    "title": "Recharge",
                    "x_label": "Time Steps [month]",
                    "y_label": "Value [mm]",
                },
            },
            "outSsat": {
                "plot": {
                    "title": "Soil Moisture Content",
                    "x_label": "Time Steps [month]",
                    "y_label": "Value [mm]",
                },
            },
        }

    # TODO: Add docstring information and comments
    def helpHandler(self):
        helpIndexPath = os.path.join(self.plugin_dir, "help/build/html/index")
        showPluginHelp(filename=helpIndexPath)

    # TODO: Add docstring information and comments
    def aboutHandler(self):
        helpAboutPath = os.path.join(self.plugin_dir, "help/about.html")
        with open(helpAboutPath, "r") as aboutContent:
            QMessageBox.about(self, "About RUBEM Hydrological", aboutContent.read())

    # TODO: Add docstring information and comments
    def populateMapSeriesTree(self):
        self.mapSeriesTreeModel.clear()
        mapSeriesRootNode = self.mapSeriesTreeModel.invisibleRootItem()
        for key, fileName in self.mapSeriesDictFileNames.items():
            tmpOutMapFileList = glob(
                os.path.join(self.config.get("FILES", "output") + fileName) + "*.[0-9]*"
            )
            if tmpOutMapFileList:
                tmpOutMapSeries = StandardItem(key)
                tmpOutMapSeries.setSelectable(False)
                tmpOutMapSeries.appendRows(
                    [StandardItem(item, isPath=True) for item in tmpOutMapFileList]
                )
                mapSeriesRootNode.appendRow(tmpOutMapSeries)
                self.treeView_MapSeriesData.setModel(self.mapSeriesTreeModel)

    # TODO: Add docstring information and comments
    def populateTimeSeriesTree(self):
        self.timeSeriesTreeModel.clear()
        timeSeriesRootNode = self.timeSeriesTreeModel.invisibleRootItem()
        for key, fileName in self.timeSeriesDictFileNames.items():
            tmpTimeSeriesFile = (
                os.path.join(self.config.get("FILES", "output") + fileName) + ".csv"
            )
            if os.path.exists(tmpTimeSeriesFile):
                tmpOutTimeSeries = StandardItem(key)
                tmpOutTimeSeries.setSelectable(False)
                tmpOutTimeSeries.appendRow(StandardItem(tmpTimeSeriesFile, isPath=True))
                timeSeriesRootNode.appendRow(tmpOutTimeSeries)
                self.treeView_TimeSeriesData.setModel(self.timeSeriesTreeModel)

    # TODO: Add docstring information and comments
    def plotWrapper(self, index: QModelIndex):
        if index.flags() & Qt.ItemIsSelectable:
            key = os.path.splitext(index.data())[0]
            plotTimeSeriesData(
                os.path.join(self.config.get("FILES", "output"), index.data()),
                self.timeSeriesDict.get(key).get("plot"),
                self.config.get("SIM_TIME", "start"),
                self.config.get("SIM_TIME", "end"),
            )

    # TODO: Add docstring information and comments
    def canvasHandler(self, index: QModelIndex):
        if index.flags() & Qt.ItemIsSelectable:
            rasterPath = os.path.join(self.config.get("FILES", "output"), index.data())
            legend = index.data()
            rlayer = QgsRasterLayer(rasterPath, legend)
            rlayer.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
            if not rlayer.isValid():
                # TODO: Move this message to plugin message bar
                self.iface.messageBar().pushMessage(
                    "Error", "Layer failed to load!", level=Qgis.Critical
                )
            elif QgsProject.instance().mapLayersByName(legend):
                # TODO: Move this message to plugin message bar
                self.iface.messageBar().pushMessage(
                    "Error",
                    "This raster has already been added to the current project in QGIS.",
                    level=Qgis.Critical,
                )
            else:
                QgsProject.instance().addMapLayer(rlayer, False)
                layerTree = self.iface.layerTreeCanvasBridge().rootGroup()
                layerTree.insertChildNode(-1, QgsLayerTreeLayer(rlayer))

    # TODO: Add docstring information and comments
    #! Obsolete and/or used for testing method only
    def displayPoint(self, pointTool):
        value = self.getValue(
            os.path.join(
                self.config.get("FILES", "output"), self.iface.activeLayer().name()
            ),
            pointTool[0],
            pointTool[1],
        )
        self.textBrowser_log.append(f"{pointTool[0]}, {pointTool[1]} => {value}")

    # TODO: Add docstring information and comments
    def setupUserInputValidators(self):

        for key, elementsTuple in self.uiDirPathDict.items():
            lineEdit, label = elementsTuple
            validator = DirectoryPathValidator(lineEdit, label)
            lineEdit.setValidator(validator)

        for key, elementsTuple in self.uiFilePathDict.items():
            lineEdit, label, allowedExt = elementsTuple
            validator = FilePathValidator(lineEdit, label, allowedExt)
            lineEdit.setValidator(validator)

    def getDirectoryPath(self, caption):
        """Get the path of an existing directory using QFileDialog\n
        and returns it.

        :param caption: This is the title of the file selection window.
        :type caption: String

        :returns: Directory path selected by the user.
        :rtype: String
        """
        directoryPath = QFileDialog.getExistingDirectory(
            self, caption=caption, directory=self.lastOpenedDirectory
        )
        if directoryPath:
            return f"{directoryPath}/"

    def getFilePath(self, caption, filter, selectedFilter=""):
        """Get the path of an existing file using QFileDialog and returns it.

        :param caption: This is the title of the file selection window.
        :type caption: String

        :param filter: Only files that match the given filter are shown.
        :type filter: String

        :returns: File path selected by the user.
        :rtype: String
        """
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            caption=caption,
            directory=self.lastOpenedDirectory,
            filter=filter,
            initialFilter=selectedFilter,
        )
        if filePath:
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
        return f"{directoryPath}/", "".join(filter(str.isalpha, filePrefix))

    def getFirstFileNameMapSeries(self, path):
        """[summary].

        :param path: [description]
        :type path: [type]

        :return: [description]
        :rtype: [type]
        """
        pattern = "*.0*"
        fileList = glob(f"{path}{pattern}")
        if fileList:
            return os.path.normpath(fileList[0])
        else:
            return ""

    def setProjectModified(self, *arguments):
        """[summary].

        :Slot signal:
        :Signal sender:
        """
        # Only a current project can be modified
        if self.hasCurrentProject:
            # Only update this flag if project hasn't been modified
            if not self.hasProjectBeenModified:
                self.hasProjectBeenModified = True

    # TODO: Add docstring information and comments
    def hasFilledAllFields(self):
        """Check if all fields have been properly filled in.

        Returns:
            [type]: [description]
        """
        emptyFields = []
        for element in self.uiDirPathDict.values():
            lineEdit, _ = element
            if not lineEdit.text() or not os.path.exists(lineEdit.text()):
                lineEdit.setStyleSheet(INVALID_LINEEDIT_STYLESHEET)
                emptyFields.append(lineEdit)

        # for lineEdit in self.findChildren(QLineEdit):
        for element in self.uiFilePathDict.values():
            lineEdit, _, _ = element
            if not lineEdit.text() or not os.path.exists(lineEdit.text()):
                lineEdit.setStyleSheet(INVALID_LINEEDIT_STYLESHEET)
                emptyFields.append(lineEdit)

        if emptyFields:
            self.bar.pushMessage(
                "Misconfiguration",
                "Data entered is missing or non-existent",
                level=Qgis.Warning,
            )

        checkedBoxes = []
        for element in self.uiGenerateFilesDict.values():
            if element.isChecked():
                checkedBoxes.append(element)

        if not checkedBoxes:
            self.groupBox_GenerateFiles.setStyleSheet(INVALID_LABEL_STYLESHEET)
            self.bar.pushMessage(
                "Misconfiguration", "No output variable selected", level=Qgis.Warning
            )
        else:
            self.groupBox_GenerateFiles.setStyleSheet(ACCEPTABLE_LABEL_STYLESHEET)

        hasValidDateRange = True
        if self.dtEdt_StartSim.date() >= self.dtEdt_EndSim.date():
            hasValidDateRange = False
            self.groupBox_SimulationPeriod.setStyleSheet(INVALID_LABEL_STYLESHEET)
            self.bar.pushMessage(
                "Misconfiguration",
                "The end date must be greater than the start date",
                level=Qgis.Warning,
            )
        else:
            self.groupBox_SimulationPeriod.setStyleSheet(ACCEPTABLE_LABEL_STYLESHEET)

        hasAreaFractionAddUpTo1 = True
        if (
            not self.doubleSpinBox_ManningRelatedWeightFactor.value()
            + self.doubleSpinBox_SoilRelatedWeightFactor.value()
            + self.doubleSpinBox_SlopeRelatedWeightFactor.value()
            == 1
        ):
            hasAreaFractionAddUpTo1 = False
            self.groupBox_WeightFactors.setStyleSheet(INVALID_LABEL_STYLESHEET)
            self.bar.pushMessage(
                "Misconfiguration",
                "The sum of the area fractions must add up to 1",
                level=Qgis.Warning,
            )
        else:
            self.groupBox_WeightFactors.setStyleSheet(ACCEPTABLE_LABEL_STYLESHEET)

        if (
            not emptyFields
            and checkedBoxes
            and hasValidDateRange
            and hasAreaFractionAddUpTo1
        ):
            return True
        else:
            return False

    # Project Folder
    def setInputDirectoryPath(self, userInputDir=None):
        """Define the directory containing the project's input data.

        :Slot signal: clicked
        :Signal sender: toolButton_InputFolder
        """
        directoryPath = self.getDirectoryPath(caption="Select Input Directory")
        if directoryPath:
            self.config.set("FILES", "input", directoryPath)
            self.lineEdit_InputFolder.setText(directoryPath)

    def setOutputDirectoryPath(self):
        """Define the directory containing the project's output data.

        :Slot signal: clicked
        :Signal sender: toolButton_OutputFolder
        """
        directoryPath = self.getDirectoryPath(caption="Select Output Directory")
        if directoryPath:
            # Folder is empty
            if not os.listdir(directoryPath):
                self.config.set("FILES", "output", directoryPath)
                self.lineEdit_OutputFolder.setText(directoryPath)
            else:
                response = self.getUserRetDirNotEmpty()
                if response == QMessageBox.Ok:
                    self.config.set("FILES", "output", directoryPath)
                    self.lineEdit_OutputFolder.setText(directoryPath)

    # Tab widget
    # Settings tab
    # Model General Settings
    def setDEMFilePath(self):
        """Define the project's DEM map file.

        Also updates the lineEdt_Dem field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_Dem
        """
        filePath = self.getFilePath(caption="Select DEM map File", filter="*.map")
        if filePath:
            self.config.set("FILES", "dem", filePath)
            self.lineEdt_Dem.setText(filePath)

    def setDEMTifFilePath(self):
        """Define the project's DEM TIFF file.

        Also updates the lineEdt_DemTif field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_DemTif
        """
        filePath = self.getFilePath(caption="Select DEM TIFF File", filter="*.tif")
        if filePath:
            self.config.set("FILES", "demTif", filePath)
            self.lineEdt_DemTif.setText(filePath)

    def setCloneFilePath(self):
        """Define the project's Clone file.

        Also updates the lineEdt_Clone field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_Clone
        """
        filePath = self.getFilePath(caption="Select Clone File", filter="*.map")
        if filePath:
            self.config.set("FILES", "clone", filePath)
            self.lineEdt_Clone.setText(filePath)

    def setExportSampleLocations(self):
        """Define as enabled the fields related to the Sample file.

        Fields: lineEdt_Sample, btn_Sample and label_SelectSample.

        :Slot signal: checked
        :Signal sender: checkBox_Sample
        """
        self.config.set(
            "GENERATE_FILE", "genTss", str(self.checkBox_Sample.isChecked())
        )

        if self.checkBox_Sample.isChecked():
            self.lineEdt_Sample.setEnabled(True)
            self.btn_Sample.setEnabled(True)
            self.label_SelectSample.setEnabled(True)
        else:
            self.lineEdt_Sample.clear()
            self.lineEdt_Sample.setEnabled(False)
            self.btn_Sample.setEnabled(False)
            self.label_SelectSample.setEnabled(False)

    def setSampleFilePath(self):
        """Define the project's Sample file.

        Also updates the lineEdt_Sample field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_Sample
        """
        filePath = self.getFilePath(
            caption="Select Sample Stations File", filter="*.map"
        )
        if filePath:
            self.config.set("FILES", "samples", filePath)
            self.lineEdt_Sample.setText(filePath)

    def setGridSize(self):
        """Define the project's Grid size.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_GridSize
        """
        self.config.set("GRID", "grid", str(self.doubleSpinBox_GridSize.value()))

    # Simulation Period
    def setStartSimulationPeriod(self):
        """Define the start date of the model simulation period.

        Follows the format 'dd/MM/yyyy'.

        :Slot signal: editingFinished
        :Signal sender: dtEdt_StartSim
        """
        self.config.set(
            "SIM_TIME", "start", self.dtEdt_StartSim.date().toString("dd/MM/yyyy")
        )

    def setEndSimulationPeriod(self):
        """Define the end date of the model simulation period.

        Follows the format 'dd/MM/yyyy'.

        :Slot signal: editingFinished
        :Signal sender: dtEdt_EndSim
        """
        self.config.set(
            "SIM_TIME", "end", self.dtEdt_EndSim.date().toString("dd/MM/yyyy")
        )

    # Soil tab
    # Soil Parameters
    def setSoilMapFilePath(self):
        """Define the project's Soil Map file.

        Also updates the lineEdt_SoilMap field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_SoilMap
        """
        filePath = self.getFilePath(caption="Select Soil Map File", filter="*.map")
        if filePath:
            self.config.set("FILES", "solo", filePath)
            self.lineEdt_SoilMap.setText(filePath)

    def setDensityFilePath(self):
        """Define the project's Density file.

        Also updates the lineEdt_DensityDg field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_DensityDg
        """
        filePath = self.getFilePath(
            caption="Select Soil Bulk Density File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "dg", filePath)
            self.lineEdt_DensityDg.setText(filePath)

    def setHydraulicConductivityFilePath(self):
        """Define the project's HydraulicConductivity file.

        Also updates the lineEdt_HydraulicConductivityKr field with the\n
         selected file path.

        :Slot signal: clicked
        :Signal sender: btn_HydraulicConductivityKr
        """
        filePath = self.getFilePath(
            caption="Select Soil Saturated Hydraulic Conductivity File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "kr", filePath)
            self.lineEdt_HydraulicConductivityKr.setText(filePath)

    def setFieldCapacityFilePath(self):
        """Define the project's Field Capacity file.

        Also updates the lineEdt_FieldCapacityCC field with the selected\n
         file path.

        :Slot signal: clicked
        :Signal sender: btn_FieldCapacityCC
        """
        filePath = self.getFilePath(
            caption="Select Soil Field Capacity File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "capCampo", filePath)
            self.lineEdt_FieldCapacityCC.setText(filePath)

    def setWiltingPointFilePath(self):
        """Define the project's Wilting Point file.

        Also updates the lineEdt_WiltingPointWP field with the selected\n
         file path.

        :Slot signal: clicked
        :Signal sender: btn_WiltingPointWP
        """
        filePath = self.getFilePath(
            caption="Select Soil Wilting Point File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "pontomurcha", filePath)
            self.lineEdt_WiltingPointWP.setText(filePath)

    def setSaturationFilePath(self):
        """Define the project's Saturation file.

        Also updates the lineEdt_Saturation field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_Saturation
        """
        filePath = self.getFilePath(
            caption="Select Soil Saturation File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "saturacao", filePath)
            self.lineEdt_Saturation.setText(filePath)

    def setRootZoneThicknessFilePath(self):
        """Define the project's Root Zone Thickness file.

        Also updates the lineEdt_RootZoneThicknessZr field with the selected\n
         file path.

        :Slot signal: clicked
        :Signal sender: btn_RootZoneThicknessZr
        """
        filePath = self.getFilePath(
            caption="Select Soil Rootzone Depth File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "zr", filePath)
            self.lineEdt_RootZoneThicknessZr.setText(filePath)

    # Initial Soil Conditions
    def setInitialSoilMoisture(self):
        """Define the project's Initial soil moisture value in millimeters.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_InitialSoilMoisture
        """
        self.config.set(
            "INITIAL SOIL CONDITIONS",
            "ftur_ini",
            str(self.doubleSpinBox_InitialSoilMoisture.value()),
        )

    def setInitialBaseFlow(self):
        """Define the project's Initial Base Flow value in millimeters.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_BaseFlowInitial
        """
        self.config.set(
            "INITIAL SOIL CONDITIONS",
            "eb_ini",
            str(self.doubleSpinBox_BaseFlowInitial.value()),
        )

    def setBaseFlowLimit(self):
        """Define the project's Base Flow Limit value in millimeters.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_BaseFlowLimit
        """
        self.config.set(
            "INITIAL SOIL CONDITIONS",
            "eb_lim",
            str(self.doubleSpinBox_BaseFlowLimit.value()),
        )

    def setInitialTus(self):
        """Define the project's Initial Tus value in millimeters.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_TusInitial
        """
        self.config.set(
            "INITIAL SOIL CONDITIONS",
            "tus_ini",
            str(self.doubleSpinBox_TusInitial.value()),
        )

    # Land Use tab
    # Land Use Series
    def setLandUseSeriesFilePath(self):
        """Define the project's Land Use Series file folder.

        Also updates the lineEdt_LandUseSeries field with the selected file
        path and set land use file prefix.

        :Slot signal: clicked
        :Signal sender: btn_LandUseSeries
        """
        filePath = self.getFilePath(
            caption="Select Land Use Series File", filter="(*.001);;All Files(*)"
        )
        if filePath:
            tmpDir, tmpPrefix = self.splitDirFilePrefix(filePath)
            self.config.set("FILES", "landuse", tmpDir)
            self.config.set("FILES", "landuseFilePrefix", tmpPrefix)
            self.lineEdt_LandUseSeries.setText(filePath)

    # NDVI
    def setNDVISeriesFilePath(self):
        """Define the project's NDVISeries file folder.

        Also updates the lineEdt_NDVISeries field with the selected file
        path and define the ndvi file prefix.

        :Slot signal: clicked
        :Signal sender: btn_NDVISeries
        """
        filePath = self.getFilePath(
            caption="Select NDVI Series File", filter="(*.001);;All Files(*)"
        )
        if filePath:
            tmpDir, tmpPrefix = self.splitDirFilePrefix(filePath)
            self.config.set("FILES", "ndvi", tmpDir)
            self.config.set("FILES", "ndviFilePrefix", tmpPrefix)
            self.lineEdt_NDVISeries.setText(filePath)

    def setNDVIMaximumSeriesFilePath(self):
        """Define the project's NDVIMax file.

        Also updates the lineEdt_NDVIMax field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_NDVIMax
        """
        filePath = self.getFilePath(
            caption="Select Maximum NDVI Series File", filter="(*.map)"
        )
        if filePath:
            self.config.set("FILES", "ndvimax", filePath)
            self.lineEdt_NDVIMax.setText(filePath)

    def setNDVIMinimumSeriesFilePath(self):
        """Define the project's NDVIMin file.

        Also updates the lineEdt_NDVIMin field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_NDVIMin
        """
        filePath = self.getFilePath(
            caption="Select Minimum NDVI Series File", filter="(*.map)"
        )
        if filePath:
            self.config.set("FILES", "ndvimin", filePath)
            self.lineEdt_NDVIMin.setText(filePath)

    # a
    def setAiFilePath(self):
        """Define the project's a_i file.

        Also updates the lineEdt_a_i field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_a_i
        """
        filePath = self.getFilePath(
            caption="Select Impervious Area Fraction (ai) File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "a_i", filePath)
            self.lineEdt_a_i.setText(filePath)

    def setAoFilePath(self):
        """Define the project's a_o file.

        Also updates the lineEdt_a_o field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_a_o
        """
        filePath = self.getFilePath(
            caption="Select Open Water Area Fraction (ao) File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "a_o", filePath)
            self.lineEdt_a_o.setText(filePath)

    def setAsFilePath(self):
        """Define the project's a_s file.

        Also updates the lineEdt_a_s field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_a_s
        """
        filePath = self.getFilePath(
            caption="Select Bare Soil Area Fraction (as) File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "a_s", filePath)
            self.lineEdt_a_s.setText(filePath)

    def setAvFilePath(self):
        """Define the project's a_v file.

        Also updates the lineEdt_a_v field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_a_v
        """
        filePath = self.getFilePath(
            caption="Select Vegetated Area Fraction (av) File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "a_v", filePath)
            self.lineEdt_a_v.setText(filePath)

    # Manning
    def setManningFilePath(self):
        """Define the project's Manning file.

        Also updates the lineEdt_Manning field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_Manning
        """
        filePath = self.getFilePath(
            caption="Select Manning File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "manning", filePath)
            self.lineEdt_Manning.setText(filePath)

    # Kc
    def setKcMaximumFilePath(self):
        """Define the project's KcMax file.

        Also updates the lineEdt_KcMax field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_KcMax
        """
        filePath = self.getFilePath(
            caption="Select Maximum Crop Coefficient (Kc) File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "kcmax", filePath)
            self.lineEdt_KcMax.setText(filePath)

    def setKcMinimumFilePath(self):
        """Define the project's KcMin file.

        Also updates the lineEdt_KcMin field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_KcMin
        """
        filePath = self.getFilePath(
            caption="Select Minimum Crop Coefficient (Kc) File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "kcmin", filePath)
            self.lineEdt_KcMin.setText(filePath)

    # Fpar
    def setFparMaximum(self):
        """Define the project's Fpar Maximum value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_FparMax
        """
        self.config.set("CONSTANT", "fpar_max", str(self.doubleSpinBox_FparMax.value()))

    def setFparMinimum(self):
        """Define the project's Fpar Minimum value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_FparMin
        """
        self.config.set("CONSTANT", "fpar_min", str(self.doubleSpinBox_FparMin.value()))

    # Interception
    def setInterception(self):
        """Define the project's Interception value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_Interception
        """
        self.config.set(
            "CONSTANT", "i_imp", str(self.doubleSpinBox_Interception.value())
        )

    # Leaf Area Index
    def setLeafAreaIndexMaximum(self):
        """Define the project's Maximum Leaf Area Index value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_LeafAreaIndexMax
        """
        self.config.set(
            "CONSTANT", "lai_max", str(self.doubleSpinBox_LeafAreaIndexMax.value())
        )

    # Climate tab
    def setPrecipitationSeriesFilePath(self):
        """Define the project's Precipitation folder file.

        Alsochange the lineEdt_Precipitation field with the selected file
        path and define the prec file prefix.

        :Slot signal: clicked
        :Signal sender: btn_Precipitation
        """
        filePath = self.getFilePath(
            caption="Select Rainfall Series File", filter="(*.001);;All Files(*)"
        )
        if filePath:
            tmpDir, tmpPrefix = self.splitDirFilePrefix(filePath)
            self.config.set("FILES", "prec", tmpDir)
            self.config.set("FILES", "precFilePrefix", tmpPrefix)
            self.lineEdt_Precipitation.setText(filePath)

    def setEvapotranspirationSeriesFilePath(self):
        """Define the project's Evapotranspiration folder file.

        Also updates the lineEdt_EvapoTranspiration field with the selected
        file path and define the etp file prefix.

        :Slot signal: clicked
        :Signal sender: btn_EvapoTranspiration
        """
        filePath = self.getFilePath(
            caption="Select Potential Evapotranspiration Series File",
            filter="(*.001);;All Files(*)",
        )
        if filePath:
            tmpDir, tmpPrefix = self.splitDirFilePrefix(filePath)
            self.config.set("FILES", "etp", tmpDir)
            self.config.set("FILES", "etpFilePrefix", tmpPrefix)
            self.lineEdt_EvapoTranspiration.setText(filePath)

    def setKpSeriesFilePath(self):
        """Define the project's Class A Pan Coefficient (Kp) folder file.

        Also updates the lineEdt_PanCoefficientKp field with the selected file
        path and define the Kp file prefix.

        :Slot signal: clicked
        :Signal sender: btn_PanCoefficientKp
        """
        filePath = self.getFilePath(
            caption="Select Class A Pan Coefficient (Kp) Series File",
            filter="(*.001);;All Files(*)",
        )
        if filePath:
            tmpDir, tmpPrefix = self.splitDirFilePrefix(filePath)
            self.config.set("FILES", "kp", tmpDir)
            self.config.set("FILES", "kpFilePrefix", tmpPrefix)
            self.lineEdt_PanCoefficientKp.setText(filePath)

    def setRainyDaysSeriesFilePath(self):
        """Define the project's Rainy Days file.

        Also updates the lineEdt_RainyDays field with the selected file path.

        :Slot signal: clicked
        :Signal sender: btn_RainyDays
        """
        filePath = self.getFilePath(
            caption="Select Rainy Days Series File",
            filter="CSV files (*.csv);;Text files (*.txt)",
            selectedFilter="Text files (*.txt)",
        )
        if filePath:
            self.config.set("PARAMETERS", "rainydays", filePath)
            self.lineEdt_RainyDays.setText(filePath)

    # Parameters tab
    # Model Parameters
    def setExponentCh(self):
        """Define the project's Exponent of Ch value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_ExponentCh
        """
        self.config.set("CALIBRATION", "b", str(self.doubleSpinBox_ExponentCh.value()))

    def setDelayFactor(self):
        """Define the project's Delay Factor value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_DelayFactor
        """
        self.config.set("CALIBRATION", "x", str(self.doubleSpinBox_DelayFactor.value()))

    def setRegionalConsecutiveDrynessLevel(self):
        """Define the project's Regional Consecutive Dryness (RCD) Level value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_RegionalConsecutiveDrynessLevel
        """
        self.config.set(
            "CALIBRATION",
            "rcd",
            str(self.doubleSpinBox_RegionalConsecutiveDrynessLevel.value()),
        )

    def setDelayCoefficientBaseFlow(self):
        """Define the project's Delay Coefficient Base Flow value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_DelayCoefficientBaseFlow
        """
        self.config.set(
            "CALIBRATION",
            "alfa_gw",
            str(self.doubleSpinBox_DelayCoefficientBaseFlow.value()),
        )

    def setPartitioningCoefficientRelated(self):
        """Define the project's Partitioning Coefficient Related value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_PartitioningCoefficientRelatedSoil
        """
        self.config.set(
            "CALIBRATION",
            "f",
            str(self.doubleSpinBox_PartitioningCoefficientRelatedSoil.value()),
        )

    def setInterceptionCalibration(self):
        """Define the project's Interception Calibration value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_InterceptionCalibrationAlpha
        """
        self.config.set(
            "CALIBRATION",
            "alfa",
            str(self.doubleSpinBox_InterceptionCalibrationAlpha.value()),
        )

    # Weight Factors
    def setManningRelatedWeightFactor(self):
        """Define the project's Manning Related Weight Factor (w1) value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_ManningRelatedWeightFactor
        """
        self.config.set(
            "CALIBRATION",
            "w1",
            str(self.doubleSpinBox_ManningRelatedWeightFactor.value()),
        )

    def setSoilRelatedWeightFactor(self):
        """Define the project's Soil Related Weight Factor (w2) value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_SoilRelatedWeightFactor
        """
        self.config.set(
            "CALIBRATION", "w2", str(self.doubleSpinBox_SoilRelatedWeightFactor.value())
        )

    def setSlopeRelatedWeightFactor(self):
        """Define the project's Slope Related Weight Factor (w3) value.

        :Slot signal: editingFinished
        :Signal sender: doubleSpinBox_SlopeRelatedWeightFactor
        """
        self.config.set(
            "CALIBRATION",
            "w3",
            str(self.doubleSpinBox_SlopeRelatedWeightFactor.value()),
        )

    # Run tab
    # Geneate Files
    def setInterceptionGenerateFile(self):
        """Define whether the Interception file will be generated as output
         from the model execution.

        :Slot signal: checked
        :Signal sender: checkBox_InterceptionInt
        """
        self.config.set(
            "GENERATE_FILE", "Int", str(self.checkBox_InterceptionInt.isChecked())
        )

    def setInterceptionEbGenerateFile(self):
        """Define whether the Interception Eb file will be generated as output
         from the model execution.

        :Slot signal: checked
        :Signal sender: checkBox_InterceptionEb
        """
        self.config.set(
            "GENERATE_FILE", "bflow", str(self.checkBox_InterceptionEb.isChecked())
        )

    def setEvapotranspirationGenerateFile(self):
        """Define whether the Evapotranspiration file will be generated as
         output from the model execution.

        :Slot signal: checked
        :Signal sender: checkBox_EvapotranspirationEvp
        """
        self.config.set(
            "GENERATE_FILE", "etp", str(self.checkBox_EvapotranspirationEvp.isChecked())
        )

    def setRechargeGenerateFile(self):
        """Define whether the Recharge file will be generated as output
         from the model execution.

        :Slot signal: checked
        :Signal sender: checkBox_RechargeRec
        """
        self.config.set(
            "GENERATE_FILE", "Rec", str(self.checkBox_RechargeRec.isChecked())
        )

    def setSoilMoistureGenerateFile(self):
        """Define whether the Soil Moisture file will be generated as output
         from the model execution.

        :Slot signal: checked
        :Signal sender: checkBox_SoilMoistureTur
        """
        self.config.set(
            "GENERATE_FILE", "ssat", str(self.checkBox_SoilMoistureTur.isChecked())
        )

    def setLateralFLowGenerateFile(self):
        """Define whether the Lateral FLow file will be generated as output
         from the model execution.

        :Slot signal: checked
        :Signal sender: checkBox_LateralFlowLf
        """
        self.config.set(
            "GENERATE_FILE", "Lf", str(self.checkBox_LateralFlowLf.isChecked())
        )

    def setRunoffEsdGenerateFile(self):
        """Define whether the Runoff Esd file will be generated as output
         from the model execution.

        :Slot signal: checked
        :Signal sender: checkBox_RunoffEsd
        """
        self.config.set(
            "GENERATE_FILE", "sfrun", str(self.checkBox_RunoffEsd.isChecked())
        )

    # TODO: Rename setRunoffVazaoGenerateFile, checkBox_RunoffVazao, GUI and
    #  config section GENERATE_FILES option Vazao
    def setRunoffVazaoGenerateFile(self):
        """Define whether the Runoff Vazao file will be generated as output
         from the model execution.

        :Slot signal: checked
        :Signal sender: checkBox_RunoffVazao
        """
        self.config.set(
            "GENERATE_FILE", "runoff", str(self.checkBox_RunoffVazao.isChecked())
        )

    def updateConfigFromGUI(self):
        """Update the configuration dictionary with the values present in the GUI's data entry objects."""
        self.textBrowser_log.append("Updating configuration with current values...")

        # Project Folder
        self.config.set("FILES", "input", self.lineEdit_InputFolder.text())
        self.config.set("FILES", "output", self.lineEdit_OutputFolder.text())

        # Tab widget
        # Settings tab
        # Model General Settings
        self.config.set("FILES", "dem", self.lineEdt_Dem.text())
        self.config.set("FILES", "demtif", self.lineEdt_DemTif.text())
        self.config.set("FILES", "clone", self.lineEdt_Clone.text())

        self.config.set(
            "GENERATE_FILE", "genTss", str(self.checkBox_Sample.isChecked())
        )
        if self.checkBox_Sample.isChecked():
            self.config.set("FILES", "samples", self.lineEdt_Sample.text())

        # Grid Size
        self.config.set("GRID", "grid", str(self.doubleSpinBox_GridSize.value()))

        # Simulation Period
        self.config.set(
            "SIM_TIME", "start", self.dtEdt_StartSim.date().toString("dd/MM/yyyy")
        )
        self.config.set(
            "SIM_TIME", "end", self.dtEdt_EndSim.date().toString("dd/MM/yyyy")
        )

        # Soil tab
        # Soil Parameters
        self.config.set("FILES", "solo", self.lineEdt_SoilMap.text())
        self.config.set("PARAMETERS", "dg", self.lineEdt_DensityDg.text())
        self.config.set("PARAMETERS", "kr", self.lineEdt_HydraulicConductivityKr.text())

        self.config.set("PARAMETERS", "capCampo", self.lineEdt_FieldCapacityCC.text())
        self.config.set("PARAMETERS", "pontomurcha", self.lineEdt_WiltingPointWP.text())
        self.config.set("PARAMETERS", "saturacao", self.lineEdt_Saturation.text())
        self.config.set("PARAMETERS", "zr", self.lineEdt_RootZoneThicknessZr.text())

        # Initial Soil Conditions
        self.config.set(
            "INITIAL SOIL CONDITIONS",
            "ftur_ini",
            str(self.doubleSpinBox_InitialSoilMoisture.value()),
        )
        self.config.set(
            "INITIAL SOIL CONDITIONS",
            "eb_ini",
            str(self.doubleSpinBox_BaseFlowInitial.value()),
        )
        self.config.set(
            "INITIAL SOIL CONDITIONS",
            "eb_lim",
            str(self.doubleSpinBox_BaseFlowLimit.value()),
        )
        self.config.set(
            "INITIAL SOIL CONDITIONS",
            "tus_ini",
            str(self.doubleSpinBox_TusInitial.value()),
        )

        # Land Use tab
        # Land Use Series
        tmpPath, tmpPrefix = self.splitDirFilePrefix(self.lineEdt_LandUseSeries.text())
        self.config.set("FILES", "landuse", tmpPath)
        self.config.set("FILES", "landuseFilePrefix", tmpPrefix)

        tmpPath, tmpPrefix = self.splitDirFilePrefix(self.lineEdt_NDVISeries.text())
        self.config.set("FILES", "ndvi", tmpPath)
        self.config.set("FILES", "ndviFilePrefix", tmpPrefix)

        self.config.set("FILES", "ndvimax", self.lineEdt_NDVIMax.text())
        self.config.set("FILES", "ndvimin", self.lineEdt_NDVIMin.text())

        # a
        self.config.set("PARAMETERS", "a_i", self.lineEdt_a_i.text())
        self.config.set("PARAMETERS", "a_o", self.lineEdt_a_o.text())
        self.config.set("PARAMETERS", "a_s", self.lineEdt_a_s.text())
        self.config.set("PARAMETERS", "a_v", self.lineEdt_a_v.text())

        # Manning
        self.config.set("PARAMETERS", "manning", self.lineEdt_Manning.text())

        # Kc
        self.config.set("PARAMETERS", "kcmax", self.lineEdt_KcMax.text())
        self.config.set("PARAMETERS", "kcmin", self.lineEdt_KcMin.text())

        # Fpar
        self.config.set("CONSTANT", "fpar_max", str(self.doubleSpinBox_FparMax.value()))
        self.config.set("CONSTANT", "fpar_min", str(self.doubleSpinBox_FparMin.value()))

        # Interception
        self.config.set(
            "CONSTANT", "i_imp", str(self.doubleSpinBox_Interception.value())
        )

        # Leaf Area Index
        self.config.set(
            "CONSTANT", "lai_max", str(self.doubleSpinBox_LeafAreaIndexMax.value())
        )

        # Climate tab
        tmpPath, tmpPrefix = self.splitDirFilePrefix(self.lineEdt_Precipitation.text())
        self.config.set("FILES", "prec", tmpPath)
        self.config.set("FILES", "precFilePrefix", tmpPrefix)

        tmpPath, tmpPrefix = self.splitDirFilePrefix(
            self.lineEdt_EvapoTranspiration.text()
        )
        self.config.set("FILES", "etp", tmpPath)
        self.config.set("FILES", "etpFilePrefix", tmpPrefix)

        tmpPath, tmpPrefix = self.splitDirFilePrefix(
            self.lineEdt_PanCoefficientKp.text()
        )
        self.config.set("FILES", "kp", tmpPath)
        self.config.set("FILES", "kpFilePrefix", tmpPrefix)

        self.config.set("PARAMETERS", "rainydays", self.lineEdt_RainyDays.text())

        # Parameters tab
        # Model Parameters
        self.config.set("CALIBRATION", "b", str(self.doubleSpinBox_ExponentCh.value()))
        self.config.set("CALIBRATION", "x", str(self.doubleSpinBox_DelayFactor.value()))

        self.config.set(
            "CALIBRATION",
            "rcd",
            str(self.doubleSpinBox_RegionalConsecutiveDrynessLevel.value()),
        )
        self.config.set(
            "CALIBRATION",
            "alfa_gw",
            str(self.doubleSpinBox_DelayCoefficientBaseFlow.value()),
        )
        self.config.set(
            "CALIBRATION",
            "f",
            str(self.doubleSpinBox_PartitioningCoefficientRelatedSoil.value()),
        )
        self.config.set(
            "CALIBRATION",
            "alfa",
            str(self.doubleSpinBox_InterceptionCalibrationAlpha.value()),
        )

        # Weight Factors
        self.config.set(
            "CALIBRATION",
            "w1",
            str(self.doubleSpinBox_ManningRelatedWeightFactor.value()),
        )
        self.config.set(
            "CALIBRATION", "w2", str(self.doubleSpinBox_SoilRelatedWeightFactor.value())
        )
        self.config.set(
            "CALIBRATION",
            "w3",
            str(self.doubleSpinBox_SlopeRelatedWeightFactor.value()),
        )

        # Run tab
        # Geneate Files
        self.config.set(
            "GENERATE_FILE", "Int", str(self.checkBox_InterceptionInt.isChecked())
        )
        self.config.set(
            "GENERATE_FILE", "bflow", str(self.checkBox_InterceptionEb.isChecked())
        )
        self.config.set(
            "GENERATE_FILE", "etp", str(self.checkBox_EvapotranspirationEvp.isChecked())
        )
        self.config.set(
            "GENERATE_FILE", "Rec", str(self.checkBox_RechargeRec.isChecked())
        )
        self.config.set(
            "GENERATE_FILE", "ssat", str(self.checkBox_SoilMoistureTur.isChecked())
        )
        self.config.set(
            "GENERATE_FILE", "Lf", str(self.checkBox_LateralFlowLf.isChecked())
        )
        self.config.set(
            "GENERATE_FILE", "sfrun", str(self.checkBox_RunoffEsd.isChecked())
        )
        self.config.set(
            "GENERATE_FILE", "runoff", str(self.checkBox_RunoffVazao.isChecked())
        )

        self.textBrowser_log.append("Configuration updated with current values")

    def loadConfigFromFile(self, configFilePath):
        """Read the configuration file argument and sets the values of the\n
        GUI's data entry objects to those contained in the file.

        :param configFilePath: Valid path to the configuration file.
        :type configFilePath: String
        """
        self.textBrowser_log.append(
            "Loading configurations from file " + configFilePath + " ..."
        )

        with open(configFilePath, "r") as configfile:
            self.config.read_file(configfile)
            configfile.close()

        self.updateGUIFromConfig()
        self.textBrowser_log.append("Configurations loaded")

    def updateGUIFromConfig(self):
        """[summary]."""
        # Project Folder
        self.lineEdit_InputFolder.setText(self.config.get("FILES", "input"))
        self.lineEdit_OutputFolder.setText(self.config.get("FILES", "output"))

        # Tab widget
        # Settings tab
        # Model General Settings
        self.lineEdt_Dem.setText(self.config.get("FILES", "dem"))
        self.lineEdt_DemTif.setText(self.config.get("FILES", "demtif"))
        self.lineEdt_Clone.setText(self.config.get("FILES", "clone"))

        self.checkBox_Sample.setChecked(
            self.config.getboolean("GENERATE_FILE", "genTss")
        )
        self.lineEdt_Sample.setText(self.config.get("FILES", "samples"))

        self.doubleSpinBox_GridSize.setValue(self.config.getfloat("GRID", "grid"))
        self.dtEdt_StartSim.setDate(
            QDate.fromString(self.config.get("SIM_TIME", "start"), "dd/MM/yyyy")
        )
        self.dtEdt_EndSim.setDate(
            QDate.fromString(self.config.get("SIM_TIME", "end"), "dd/MM/yyyy")
        )

        # Soil tab
        # Soil Parameters
        self.lineEdt_SoilMap.setText(self.config.get("FILES", "solo"))
        self.lineEdt_DensityDg.setText(self.config.get("PARAMETERS", "dg"))
        self.lineEdt_HydraulicConductivityKr.setText(
            self.config.get("PARAMETERS", "kr")
        )
        self.lineEdt_FieldCapacityCC.setText(self.config.get("PARAMETERS", "capCampo"))
        self.lineEdt_WiltingPointWP.setText(
            self.config.get("PARAMETERS", "pontomurcha")
        )
        self.lineEdt_Saturation.setText(self.config.get("PARAMETERS", "saturacao"))
        self.lineEdt_RootZoneThicknessZr.setText(self.config.get("PARAMETERS", "zr"))

        # Initial Soil Conditions
        self.doubleSpinBox_InitialSoilMoisture.setValue(
            self.config.getfloat("INITIAL SOIL CONDITIONS", "ftur_ini")
        )
        self.doubleSpinBox_BaseFlowInitial.setValue(
            self.config.getfloat("INITIAL SOIL CONDITIONS", "eb_ini")
        )
        self.doubleSpinBox_BaseFlowLimit.setValue(
            self.config.getfloat("INITIAL SOIL CONDITIONS", "eb_lim")
        )
        self.doubleSpinBox_TusInitial.setValue(
            self.config.getfloat("INITIAL SOIL CONDITIONS", "tus_ini")
        )

        # Land Use tab
        # Land Use Series
        if os.path.isdir(self.config.get("FILES", "landuse")):
            tmpPath = self.getFirstFileNameMapSeries(
                self.config.get("FILES", "landuse")
            )
            self.lineEdt_LandUseSeries.setText(os.path.normpath(tmpPath))
        else:
            self.lineEdt_LandUseSeries.setText(self.config.get("FILES", "landuse"))

        # NDVI
        if os.path.isdir(self.config.get("FILES", "ndvi")):
            tmpPath = self.getFirstFileNameMapSeries(self.config.get("FILES", "ndvi"))
            self.lineEdt_NDVISeries.setText(tmpPath)
        else:
            self.lineEdt_NDVISeries.setText(self.config.get("FILES", "ndvi"))

        self.lineEdt_NDVIMax.setText(self.config.get("FILES", "ndvimax"))
        self.lineEdt_NDVIMin.setText(self.config.get("FILES", "ndvimin"))

        # a
        self.lineEdt_a_i.setText(self.config.get("PARAMETERS", "a_i"))
        self.lineEdt_a_o.setText(self.config.get("PARAMETERS", "a_o"))
        self.lineEdt_a_s.setText(self.config.get("PARAMETERS", "a_s"))
        self.lineEdt_a_v.setText(self.config.get("PARAMETERS", "a_v"))

        # Manning
        self.lineEdt_Manning.setText(self.config.get("PARAMETERS", "manning"))

        # Kc
        self.lineEdt_KcMax.setText(self.config.get("PARAMETERS", "kcmax"))
        self.lineEdt_KcMin.setText(self.config.get("PARAMETERS", "kcmin"))

        # Fpar
        self.doubleSpinBox_FparMax.setValue(
            self.config.getfloat("CONSTANT", "fpar_max")
        )
        self.doubleSpinBox_FparMin.setValue(
            self.config.getfloat("CONSTANT", "fpar_min")
        )

        # Interception
        self.doubleSpinBox_Interception.setValue(
            self.config.getfloat("CONSTANT", "i_imp")
        )

        # Leaf Area Index
        self.doubleSpinBox_LeafAreaIndexMax.setValue(
            self.config.getfloat("CONSTANT", "lai_max")
        )

        # Climate tab
        if os.path.isdir(self.config.get("FILES", "prec")):
            tmpPath = self.getFirstFileNameMapSeries(self.config.get("FILES", "prec"))
            self.lineEdt_Precipitation.setText(tmpPath)
        else:
            self.lineEdt_Precipitation.setText(self.config.get("FILES", "prec"))

        if os.path.isdir(self.config.get("FILES", "etp")):
            tmpPath = self.getFirstFileNameMapSeries(self.config.get("FILES", "etp"))
            self.lineEdt_EvapoTranspiration.setText(tmpPath)
        else:
            self.lineEdt_EvapoTranspiration.setText(self.config.get("FILES", "etp"))

        if os.path.isdir(self.config.get("FILES", "kp")):
            tmpPath = self.getFirstFileNameMapSeries(self.config.get("FILES", "kp"))
            self.lineEdt_PanCoefficientKp.setText(tmpPath)
        else:
            self.lineEdt_PanCoefficientKp.setText(self.config.get("FILES", "kp"))

        self.lineEdt_RainyDays.setText(self.config.get("PARAMETERS", "rainydays"))

        # Parameters tab
        # Model Parameters
        self.doubleSpinBox_ExponentCh.setValue(self.config.getfloat("CALIBRATION", "b"))

        self.doubleSpinBox_DelayFactor.setValue(
            self.config.getfloat("CALIBRATION", "x")
        )
        self.doubleSpinBox_RegionalConsecutiveDrynessLevel.setValue(
            self.config.getfloat("CALIBRATION", "rcd")
        )
        self.doubleSpinBox_DelayCoefficientBaseFlow.setValue(
            self.config.getfloat("CALIBRATION", "alfa_gw")
        )
        self.doubleSpinBox_PartitioningCoefficientRelatedSoil.setValue(
            self.config.getfloat("CALIBRATION", "f")
        )
        self.doubleSpinBox_InterceptionCalibrationAlpha.setValue(
            self.config.getfloat("CALIBRATION", "alfa")
        )

        # Weight Factors
        self.doubleSpinBox_ManningRelatedWeightFactor.setValue(
            self.config.getfloat("CALIBRATION", "w1")
        )
        self.doubleSpinBox_SoilRelatedWeightFactor.setValue(
            self.config.getfloat("CALIBRATION", "w2")
        )
        self.doubleSpinBox_SlopeRelatedWeightFactor.setValue(
            self.config.getfloat("CALIBRATION", "w3")
        )

        # Run tab
        # Generate Files
        self.checkBox_InterceptionInt.setChecked(
            self.config.getboolean("GENERATE_FILE", "Int")
        )
        self.checkBox_InterceptionEb.setChecked(
            self.config.getboolean("GENERATE_FILE", "bflow")
        )
        self.checkBox_EvapotranspirationEvp.setChecked(
            self.config.getboolean("GENERATE_FILE", "etp")
        )
        self.checkBox_RechargeRec.setChecked(
            self.config.getboolean("GENERATE_FILE", "Rec")
        )
        self.checkBox_SoilMoistureTur.setChecked(
            self.config.getboolean("GENERATE_FILE", "ssat")
        )
        self.checkBox_LateralFlowLf.setChecked(
            self.config.getboolean("GENERATE_FILE", "Lf")
        )
        self.checkBox_RunoffEsd.setChecked(
            self.config.getboolean("GENERATE_FILE", "sfrun")
        )
        self.checkBox_RunoffVazao.setChecked(
            self.config.getboolean("GENERATE_FILE", "runoff")
        )

    # TODO: docstring
    def getUserRetSaveCurProj(self):
        """[summary].

        :return: [description]
        :rtype: [type]
        """
        response = QMessageBox.warning(
            self,
            "RUBEM Hydrological",
            "Do you want to save the current project?\n\n"
            "Your changes will be lost if you don't save them.",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )
        return response

    def getUserRetQGISCurProj(self):
        """[summary].

        :return: [description]
        :rtype: [type]
        """
        response = QMessageBox.warning(
            self,
            "RUBEM Hydrological",
            "Do you want to proceed without saving the current QGIS project?\n\n"
            "Your changes will be lost if you don't save them.",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Ok,
        )
        return response

    def getUserRetDirNotEmpty(self):
        """[summary].

        :return: [description]
        :rtype: [type]
        """
        response = QMessageBox.warning(
            self,
            "RUBEM Hydrological",
            "The selected output directory is not empty. Do you want to proceed using this output directory?\n\n"
            "Files in this directory may be removed and/or altered.",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Ok,
        )
        return response

    # TODO: docstring
    def updateWindowTitle(self, projectTitle=None):
        if not projectTitle:
            _, file = os.path.split(self.projectFilePath)
            projectName, _ = os.path.splitext(file)
            self.setWindowTitle(projectName + " — RUBEM Hydrological")
        else:
            self.setWindowTitle(projectTitle + " — RUBEM Hydrological")

    def newProject(self):
        """[summary].

        :Slot signal: clicked
        :Signal sender: pushButton_NewProject

        :return: [description]
        :rtype: [type]
        """

        # TODO: docstring
        def setupNewProject():
            """[summary]."""

            self.qgisProject = QgsProject.instance()
            if self.qgisProject.isDirty():
                response = self.getUserRetQGISCurProj()
                if response == QMessageBox.Ok:
                    # self.qgisProject.clear()
                    self.iface.newProject()
                else:
                    return None

            self.textBrowser_log.clear()
            self.config.read_dict(defaultConfigSchema)
            self.updateGUIFromConfig()
            self.projectFilePath = None
            self.updateWindowTitle("Untitled project")
            self.saveAsProject(isNewProject=True)
            self.pushButton_SaveProject.setEnabled(True)
            self.pushButton_SaveAsProject.setEnabled(True)
            self.tabWidget.setEnabled(True)

        # Check if there is already a current project and it has been
        # modified then ask to save it
        if self.hasCurrentProject and self.hasProjectBeenModified:
            response = self.getUserRetSaveCurProj()
            # Save project before creating a new one
            if response == QMessageBox.Save:
                self.saveProject()
                setupNewProject()
            # Don't save project before creating a new one
            elif response == QMessageBox.Discard:
                setupNewProject()
            elif response == QMessageBox.Cancel:
                # User canceled saving the current project
                # and the creation of a new one
                return None
        # If there is no open projet create a new one
        else:
            setupNewProject()

    def openProject(self):
        """[summary].

        :Slot signal: clicked
        :Signal sender: pushButton_OpenProject

        :return: [description].
        :rtype: [type]
        """
        # TODO: docstring
        def setupOpenedProject():
            """[summary]."""
            filePath, _ = QFileDialog.getOpenFileName(
                self,
                caption="Open Project",
                directory=self.lastOpenedDirectory,
                filter="Project (*.ini)",
            )
            if filePath:

                self.qgisProject = QgsProject.instance()
                if self.qgisProject.isDirty():
                    response = self.getUserRetQGISCurProj()
                    if response == QMessageBox.Ok:
                        # self.qgisProject.clear()
                        self.iface.newProject()
                    else:
                        return None

                self.textBrowser_log.clear()
                self.projectFilePath = filePath
                self.hasCurrentProject = True
                self.loadConfigFromFile(self.projectFilePath)
                self.updateGUIFromConfig()
                self.pushButton_SaveProject.setEnabled(True)
                self.pushButton_SaveAsProject.setEnabled(True)
                self.tabWidget.setEnabled(True)

                if os.path.exists(self.config.get("FILES", "output")) and os.listdir(
                    self.config.get("FILES", "output")
                ):
                    self.tab_Results.setEnabled(True)
                    self.populateMapSeriesTree()
                    self.populateTimeSeriesTree()

                # TODO: Check if QGIS project file exist
                self.qgisProject.read(
                    os.path.splitext(self.projectFilePath)[0] + ".qgs"
                )
                self.updateWindowTitle()

        # Check if there is already a current project and it has been
        # modified then ask to save it
        if self.hasCurrentProject and self.hasProjectBeenModified:
            response = self.getUserRetSaveCurProj()
            # Save project before opening a project file
            if response == QMessageBox.Save:
                self.saveProject()
                setupOpenedProject()
            # Don't save project before opening a project file
            elif response == QMessageBox.Discard:
                setupOpenedProject()
            elif response == QMessageBox.Cancel:
                # User canceled saving the current project
                # and opening another project file
                return None
        # If there is no open projet select a project file
        else:
            setupOpenedProject()

    def saveProject(self, filePath=None, caption=None):
        """Save the values present in the configuration dictionary to a\n
         specified file.

        :Slot signal: clicked
        :Signal sender: pushButton_SaveProject

        :param filePath: Valid path to the configuration file, defaults
        to None (slot).
        :type filePath: String, optional (slot)

        :return: [description].
        :rtype: [type]
        """

        # TODO: docstring
        def setupFileDialog():
            """[summary].

            :return: [description].
            :rtype: [type]
            """
            if caption:
                tmpFilePath, _ = QFileDialog.getSaveFileName(
                    self,
                    caption=caption,
                    directory=self.lastOpenedDirectory,
                    filter="Project (*.ini)",
                )
            else:
                tmpFilePath, _ = QFileDialog.getSaveFileName(
                    self,
                    caption="Save project",
                    directory=self.lastOpenedDirectory,
                    filter="Project (*.ini)",
                )
            return tmpFilePath

        # TODO: docstring
        def setupProjectFileWrite(selectedFilePath):
            """[summary].

            :param selectedFilePath: [description].
            :type selectedFilePath: [type]
            """
            with open(selectedFilePath, "w") as configfile:
                self.config.write(configfile)
                configfile.close()

            self.qgisProject = QgsProject.instance()
            self.qgisProject.write(os.path.splitext(selectedFilePath)[0] + ".qgs")

            self.textBrowser_log.append("Project file saved in " + selectedFilePath)

            self.hasCurrentProject = True
            self.hasProjectBeenModified = False
            self.projectFilePath = selectedFilePath
            self.updateWindowTitle()

        # Ask user for project file path
        # --> Call this function without any arguments
        # --> Clicking 'Save' in the GUI without a current project
        # --> Clicking 'New' in the GUI without a current project
        if not filePath and not self.projectFilePath:
            retFilePath = setupFileDialog()
            # Check if the user has selected a path to the project file
            if retFilePath:
                setupProjectFileWrite(retFilePath)
                self.projectFilePath = retFilePath
            # If the user cancels the save exit without doing anything
            return

        # Save project with project file path already defined in object
        # instance
        # --> Clicking 'Save' in the GUI with a current project
        elif not filePath and self.projectFilePath and not caption:
            setupProjectFileWrite(self.projectFilePath)

        # Ask the user where to save the project file as...
        # Only the saveAsProject() function sets the caption argument
        # when calling this function.
        # --> Clicking 'Save As..' in the GUI with a current project
        # --> Clicking 'New' in the GUI with a current project
        elif not filePath and self.projectFilePath and caption:
            retFilePath = setupFileDialog()
            # Check if the user has selected a path to the project file
            if retFilePath:
                setupProjectFileWrite(retFilePath)
            # If the user cancels the save exit without doing anything
            return

        # Save the project using the filePath argument as the project file
        # path.
        # In this case it doesn't matter if self.projectFilePath is set or not
        # --> Call this function with filePath argument
        else:
            setupProjectFileWrite(filePath)

    def saveAsProject(self, isNewProject=False):
        """[summary].

        :param isNewProject: [description], defaults to False.
        :type isNewProject: bool, optional
        """
        if isNewProject:
            self.saveProject(caption="Save new project as")
        else:
            self.saveProject(caption="Save project as")

    def showConfig(self):
        """Go through the settings dictionary and print the respective\n
        sections, options and values in the textBrowser_log (in the\n
         'Run' tab)."""
        self.textBrowser_log.append("Showing current configuration:")
        for section in self.config.sections():
            self.textBrowser_log.append("[" + section + "]")
            for option in self.config.options(section):
                self.textBrowser_log.append(
                    self.tr("\t" + option + " = " + self.config.get(section, option))
                )

    # TODO: Capture execution log fom RainfallRunoff.exe without freezing GUI
    def setRunState(self):
        """Invoke the model's standalone executable including the configuration file generated from user input as an argument in the CLI."""
        # Use the standalone executable file of the model present in the plugin's root directory
        self.modelFilePath = os.path.join(self.plugin_dir, "rubem", "rubem.exe")

        if self.hasFilledAllFields():
            self.updateConfigFromGUI()
            self.saveProject(self.projectFilePath)
            # self.showConfig()

            # Make command list available to execution thread
            self.command = [self.modelFilePath, "--configfile", self.projectFilePath]

            # Empty output directory
            if not os.listdir(self.config.get("FILES", "output")):
                self.textBrowser_log.append("\n# RUBEM execution started...")
                self.runLongTask()
            # Output directory contains files, ask user before proceeding
            else:
                response = self.getUserRetDirNotEmpty()
                # User decided to proceed
                if response == QMessageBox.Ok:
                    self.textBrowser_log.append("\n# RUBEM execution started...")
                    self.runLongTask()
                # User decided to cancel
                # elif response == QMessageBox.Cancel:
                #   return None

    def reportExecutionLog(self, outputLog):
        """Update textBrowser_log with output captured from execution.s"""
        self.textBrowser_log.append(outputLog.strip())
        self.tab_Results.setEnabled(True)
        self.populateMapSeriesTree()
        self.populateTimeSeriesTree()

    def reportProgress(self, n):
        """Update progressBar with int representing overall progress of exec\n
        thread.

        :Slot signal: emit(int)
        :Signal sender: pyqtSignal(int)
        """
        self.progressBar.setValue(n)

    def runLongTask(self):
        """Configure QThread."""
        # Create a QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = RUBEMStandaloneWorker(self.command)
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.btn_Cancel.clicked.connect(self.worker.kill)
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
        self.thread.finished.connect(lambda: self.btn_Run.setEnabled(True))
        self.thread.finished.connect(lambda: self.progressBar.setValue(0))
