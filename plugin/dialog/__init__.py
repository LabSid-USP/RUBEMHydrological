# coding=utf-8
# RUBEM Hydrological is a QGIS plugin that assists in setup the RUBEM model:
# Copyright (C) 2021-2023 LabSid PHA EPUSP

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

import configparser
import os

from qgis.gui import QgsMessageBar

try:
    from qgis.PyQt.QtCore import Qt
    from qgis.PyQt.QtWidgets import QDialog, QSizePolicy
    from qgis.PyQt.QtGui import QStandardItemModel
except ImportError:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QDialog, QSizePolicy
    from PyQt5.QtGui import QStandardItemModel

try:
    from ..gui.generated.core_ui import Ui_RUBEMHydrological
    from ..validation.validators import *
    from ..validation.schemas import defaultConfigSchema
except ImportError:
    from gui.generated.core_ui import Ui_RUBEMHydrological
    from validation.validators import *
    from validation.schemas import defaultConfigSchema


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

        self.initialGuiState()

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

        self.setupUserInputValidators()

    from ._file_dir_dialogs import getDirectoryPath, getFilePath
    from ._form_validation import setupUserInputValidators, hasFilledAllFields
    from ._message_boxes import (
        getUserRetDirNotEmpty,
        getUserRetQGISCurProj,
        getUserRetSaveCurProj,
    )
    from ._project import (
        newProject,
        saveAsProject,
        saveProject,
        openProject,
        showConfig,
        setProjectModified,
        updateConfigFromGUI,
        updateGUIFromConfig,
        loadConfigFromFile,
    )
    from ._tab_climate import (
        setRainyDaysSeriesFilePath,
        setPrecipitationSeriesFilePath,
        setEvapotranspirationSeriesFilePath,
        setKpSeriesFilePath,
    )
    from ._tab_landuse import (
        setAiFilePath,
        setAoFilePath,
        setAsFilePath,
        setAvFilePath,
        setFparMaximum,
        setFparMinimum,
        setInterception,
        setKcMaximumFilePath,
        setKcMinimumFilePath,
        setLandUseSeriesFilePath,
        setLeafAreaIndexMaximum,
        setManningFilePath,
        setNDVIMaximumSeriesFilePath,
        setNDVIMinimumSeriesFilePath,
        setNDVISeriesFilePath,
    )
    from ._tab_parameters import (
        setDelayCoefficientBaseFlow,
        setDelayFactor,
        setExponentCh,
        setInterceptionCalibration,
        setManningRelatedWeightFactor,
        setPartitioningCoefficientRelated,
        setRegionalConsecutiveDrynessLevel,
        setSlopeRelatedWeightFactor,
        setSoilRelatedWeightFactor,
    )
    from ._tab_soil import (
        setBaseFlowLimit,
        setDensityFilePath,
        setFieldCapacityFilePath,
        setHydraulicConductivityFilePath,
        setInitialBaseFlow,
        setInitialSoilMoisture,
        setInitialTus,
        setRootZoneThicknessFilePath,
        setSaturationFilePath,
        setSoilMapFilePath,
        setWiltingPointFilePath,
    )
    from ._tab_settings import (
        setCloneFilePath,
        setDEMFilePath,
        setDEMTifFilePath,
        setEndSimulationPeriod,
        setExportSampleLocations,
        setGridSize,
        setInputDirectoryPath,
        setOutputDirectoryPath,
        setSampleFilePath,
        setStartSimulationPeriod,
    )
    from ._tab_run import (
        setEvapotranspirationGenerateFile,
        setInterceptionEbGenerateFile,
        setInterceptionGenerateFile,
        setLateralFLowGenerateFile,
        setRechargeGenerateFile,
        setRunoffEsdGenerateFile,
        setRunoffVazaoGenerateFile,
        setSoilMoistureGenerateFile,
    )
    from ._tab_results import populateMapSeriesTree, populateTimeSeriesTree
    from ._worker import setRunState, reportExecutionLog, reportProgress, runLongTask
    from ._graph_plot import plotTimeSeriesData, plotWrapper
    from ._map_canvas import canvasHandler
    from ._help_info import aboutHandler, helpHandler
    from ._window import initialGuiState, updateWindowTitle, closeEvent
