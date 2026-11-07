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

"""RUBEM Hydrological plugin dialog window."""

import configparser
import os

from qgis.gui import QgsMessageBar
from qgis.PyQt.QtCore import QFile, QResource, Qt
from qgis.PyQt.QtGui import QStandardItemModel
from qgis.PyQt.QtWidgets import QDialog, QSizePolicy

try:
    from ..gui.generated.core_ui import Ui_RUBEMHydrological
    from ..validation.schemas import defaultConfigSchema
    from ..validation.validators import *
except ImportError:
    from gui.generated.core_ui import Ui_RUBEMHydrological
    from validation.schemas import defaultConfigSchema
    from validation.validators import *


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
        resource = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "gui", "generated", "resources.rcc"
            )
        )
        # initGui already registers this .rcc before the toolbar icon.
        # Register again only when the binary path is still invisible, so
        # unload does not need an unbounded refcount drain for every open.
        if not QFile(":/imgBase/images/icon.png").exists():
            if not QResource.registerResource(resource):
                raise RuntimeError(f"Could not register Qt resources: {resource}")
            self._dialog_registered_resources = resource
        self.setupUi(self)
        self.iface = iface

        self.bar = QgsMessageBar(self)
        self.bar.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        # Index 1 sits under the project toolbar and above the tab widget;
        # the dialog footer (progress + button_box) stays last in the layout.
        self.layout().insertWidget(
            1,
            self.bar,
            0,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignJustify,
        )

        self.lastOpenedFile = None
        self.lastOpenedDirectory = None
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.modelFilePath = None
        self.projectFilePath = None
        self.config = configparser.ConfigParser()
        self.config.read_dict(defaultConfigSchema)

        # Chrome needs setRunState / helpHandler, which are bound on the class
        # body below; instance construction runs after that body finishes.
        from ._chrome import setup_hig_chrome

        setup_hig_chrome(self)
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
    from ._form_validation import hasFilledAllFields, setupUserInputValidators
    from ._graph_plot import plotTimeSeriesData, plotWrapper
    from ._help_info import aboutHandler, helpHandler
    from ._map_canvas import canvasHandler
    from ._message_boxes import (
        getUserRetDirNotEmpty,
        getUserRetQGISCurProj,
        getUserRetSaveCurProj,
    )
    from ._project import (
        loadConfigFromFile,
        newProject,
        openProject,
        saveAsProject,
        saveProject,
        setProjectModified,
        showConfig,
        updateConfigFromGUI,
        updateGUIFromConfig,
    )
    from ._tab_climate import (
        setEvapotranspirationSeriesFilePath,
        setKpSeriesFilePath,
        setPrecipitationSeriesFilePath,
        setRainyDaysSeriesFilePath,
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
    from ._tab_results import populateMapSeriesTree, populateTimeSeriesTree
    from ._tab_run import (
        setAccumulatedRunoffArnGenerateFile,
        setEvapotranspirationGenerateFile,
        setInterceptionEbGenerateFile,
        setInterceptionGenerateFile,
        setLateralFLowGenerateFile,
        setRechargeGenerateFile,
        setRunoffEsdGenerateFile,
        setRunoffVazaoGenerateFile,
        setSoilMoistureGenerateFile,
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
    from ._window import closeEvent, initialGuiState, reject, updateWindowTitle
    from ._worker import (
        handleFinished,
        reportExecutionLog,
        reportProgress,
        runLongTask,
        setRunState,
    )
