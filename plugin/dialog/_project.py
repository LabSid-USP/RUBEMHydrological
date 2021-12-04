import os

from qgis.core import QgsProject

try:
    from qgis.PyQt.QtCore import QDate
    from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
except ImportError:
    from PyQt5.QtCore import QDate
    from PyQt5.QtWidgets import QFileDialog, QMessageBox

try:
    from ..validation.schemas import defaultConfigSchema
    from ..utils.series import getFirstFileNameMapSeries, splitDirFilePrefix
except ImportError:
    from validation.schemas import defaultConfigSchema
    from utils.series import getFirstFileNameMapSeries, splitDirFilePrefix


def newProject(self, supressed=False):
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
        if not supressed:
            self.saveAsProject(isNewProject=True)
        self.pushButton_SaveProject.setEnabled(True)
        self.pushButton_SaveAsProject.setEnabled(True)
        self.tabWidget.setEnabled(True)
        self.hasProjectBeenModified = False

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

            if os.path.exists(self.config.get("DIRECTORIES", "output")) and os.listdir(
                self.config.get("DIRECTORIES", "output")
            ):
                self.tab_Results.setEnabled(True)
                self.populateMapSeriesTree()
                self.populateTimeSeriesTree()

            # TODO: Check if QGIS project file exist
            self.qgisProject.read(os.path.splitext(self.projectFilePath)[0] + ".qgs")
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


def updateConfigFromGUI(self):
    """Update the configuration dictionary with the values present in the GUI's data entry objects."""
    self.textBrowser_log.append("Updating configuration with current values...")

    # Project Folder
    self.config.set("DIRECTORIES", "input", self.lineEdit_InputFolder.text())
    self.config.set("DIRECTORIES", "output", self.lineEdit_OutputFolder.text())

    # Tab widget
    # Settings tab
    # Model General Settings
    self.config.set("RASTERS", "dem", self.lineEdt_Dem.text())
    self.config.set("RASTERS", "demtif", self.lineEdt_DemTif.text())
    self.config.set("RASTERS", "clone", self.lineEdt_Clone.text())

    self.config.set("GENERATE_FILE", "tss", str(self.checkBox_Sample.isChecked()))
    if self.checkBox_Sample.isChecked():
        self.config.set("RASTERS", "samples", self.lineEdt_Sample.text())

    # Grid Size
    self.config.set("GRID", "grid", str(self.doubleSpinBox_GridSize.value()))

    # Simulation Period
    self.config.set(
        "SIM_TIME", "start", self.dtEdt_StartSim.date().toString("dd/MM/yyyy")
    )
    self.config.set("SIM_TIME", "end", self.dtEdt_EndSim.date().toString("dd/MM/yyyy"))

    # Soil tab
    # Soil Parameters
    self.config.set("RASTERS", "soil", self.lineEdt_SoilMap.text())
    self.config.set("TABLES", "bulk_density", self.lineEdt_DensityDg.text())
    self.config.set("TABLES", "K_sat", self.lineEdt_HydraulicConductivityKr.text())

    self.config.set("TABLES", "T_fcap", self.lineEdt_FieldCapacityCC.text())
    self.config.set("TABLES", "T_wp", self.lineEdt_WiltingPointWP.text())
    self.config.set("TABLES", "T_sat", self.lineEdt_Saturation.text())
    self.config.set("TABLES", "rootzone_depth", self.lineEdt_RootZoneThicknessZr.text())

    # Initial Soil Conditions
    self.config.set(
        "INITIAL_SOIL_CONDITIONS",
        "T_ini",
        str(self.doubleSpinBox_InitialSoilMoisture.value()),
    )
    self.config.set(
        "INITIAL_SOIL_CONDITIONS",
        "bfw_ini",
        str(self.doubleSpinBox_BaseFlowInitial.value()),
    )
    self.config.set(
        "INITIAL_SOIL_CONDITIONS",
        "bfw_lim",
        str(self.doubleSpinBox_BaseFlowLimit.value()),
    )
    self.config.set(
        "INITIAL_SOIL_CONDITIONS",
        "S_sat_ini",
        str(self.doubleSpinBox_TusInitial.value()),
    )

    # Land Use tab
    # Land Use Series
    tmpPath, tmpPrefix = splitDirFilePrefix(self.lineEdt_LandUseSeries.text())
    self.config.set("DIRECTORIES", "landuse", tmpPath)
    self.config.set("FILENAME_PREFIXES", "landuse_prefix", tmpPrefix)

    tmpPath, tmpPrefix = splitDirFilePrefix(self.lineEdt_NDVISeries.text())
    self.config.set("DIRECTORIES", "ndvi", tmpPath)
    self.config.set("FILENAME_PREFIXES", "ndvi_prefix", tmpPrefix)

    self.config.set("RASTERS", "ndvi_max", self.lineEdt_NDVIMax.text())
    self.config.set("RASTERS", "ndvi_min", self.lineEdt_NDVIMin.text())

    # a
    self.config.set("TABLES", "a_i", self.lineEdt_a_i.text())
    self.config.set("TABLES", "a_o", self.lineEdt_a_o.text())
    self.config.set("TABLES", "a_s", self.lineEdt_a_s.text())
    self.config.set("TABLES", "a_v", self.lineEdt_a_v.text())

    # Manning
    self.config.set("TABLES", "manning", self.lineEdt_Manning.text())

    # Kc
    self.config.set("TABLES", "K_c_max", self.lineEdt_KcMax.text())
    self.config.set("TABLES", "K_c_min", self.lineEdt_KcMin.text())

    # Fpar
    self.config.set("CONSTANTS", "fpar_max", str(self.doubleSpinBox_FparMax.value()))
    self.config.set("CONSTANTS", "fpar_min", str(self.doubleSpinBox_FparMin.value()))

    # Interception
    self.config.set("CONSTANTS", "i_imp", str(self.doubleSpinBox_Interception.value()))

    # Leaf Area Index
    self.config.set(
        "CONSTANTS", "lai_max", str(self.doubleSpinBox_LeafAreaIndexMax.value())
    )

    # Climate tab
    tmpPath, tmpPrefix = splitDirFilePrefix(self.lineEdt_Precipitation.text())
    self.config.set("DIRECTORIES", "prec", tmpPath)
    self.config.set("FILENAME_PREFIXES", "prec_prefix", tmpPrefix)

    tmpPath, tmpPrefix = splitDirFilePrefix(self.lineEdt_EvapoTranspiration.text())
    self.config.set("DIRECTORIES", "etp", tmpPath)
    self.config.set("FILENAME_PREFIXES", "etp_prefix", tmpPrefix)

    tmpPath, tmpPrefix = splitDirFilePrefix(self.lineEdt_PanCoefficientKp.text())
    self.config.set("DIRECTORIES", "kp", tmpPath)
    self.config.set("FILENAME_PREFIXES", "kp_prefix", tmpPrefix)

    self.config.set("TABLES", "rainydays", self.lineEdt_RainyDays.text())

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
        "alpha_gw",
        str(self.doubleSpinBox_DelayCoefficientBaseFlow.value()),
    )
    self.config.set(
        "CALIBRATION",
        "f",
        str(self.doubleSpinBox_PartitioningCoefficientRelatedSoil.value()),
    )
    self.config.set(
        "CALIBRATION",
        "alpha",
        str(self.doubleSpinBox_InterceptionCalibrationAlpha.value()),
    )

    # Weight Factors
    self.config.set(
        "CALIBRATION",
        "w_1",
        str(self.doubleSpinBox_ManningRelatedWeightFactor.value()),
    )
    self.config.set(
        "CALIBRATION",
        "w_2",
        str(self.doubleSpinBox_SoilRelatedWeightFactor.value()),
    )
    self.config.set(
        "CALIBRATION",
        "w_3",
        str(self.doubleSpinBox_SlopeRelatedWeightFactor.value()),
    )

    # Run tab
    # Geneate Files
    self.config.set(
        "GENERATE_FILE", "itp", str(self.checkBox_InterceptionInt.isChecked())
    )
    self.config.set(
        "GENERATE_FILE", "bfw", str(self.checkBox_InterceptionEb.isChecked())
    )
    self.config.set(
        "GENERATE_FILE", "eta", str(self.checkBox_EvapotranspirationEvp.isChecked())
    )
    self.config.set("GENERATE_FILE", "rec", str(self.checkBox_RechargeRec.isChecked()))
    self.config.set(
        "GENERATE_FILE", "smc", str(self.checkBox_SoilMoistureTur.isChecked())
    )
    self.config.set(
        "GENERATE_FILE", "lfw", str(self.checkBox_LateralFlowLf.isChecked())
    )
    self.config.set("GENERATE_FILE", "srn", str(self.checkBox_RunoffEsd.isChecked()))
    self.config.set("GENERATE_FILE", "rnf", str(self.checkBox_RunoffVazao.isChecked()))

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
    self.lineEdit_InputFolder.setText(self.config.get("DIRECTORIES", "input"))
    self.lineEdit_OutputFolder.setText(self.config.get("DIRECTORIES", "output"))

    # Tab widget
    # Settings tab
    # Model General Settings
    self.lineEdt_Dem.setText(self.config.get("RASTERS", "dem"))
    self.lineEdt_DemTif.setText(self.config.get("RASTERS", "demtif"))
    self.lineEdt_Clone.setText(self.config.get("RASTERS", "clone"))

    self.checkBox_Sample.setChecked(self.config.getboolean("GENERATE_FILE", "tss"))
    self.lineEdt_Sample.setText(self.config.get("RASTERS", "samples"))

    self.doubleSpinBox_GridSize.setValue(self.config.getfloat("GRID", "grid"))
    self.dtEdt_StartSim.setDate(
        QDate.fromString(self.config.get("SIM_TIME", "start"), "dd/MM/yyyy")
    )
    self.dtEdt_EndSim.setDate(
        QDate.fromString(self.config.get("SIM_TIME", "end"), "dd/MM/yyyy")
    )

    # Soil tab
    # Soil Parameters
    self.lineEdt_SoilMap.setText(self.config.get("RASTERS", "soil"))
    self.lineEdt_DensityDg.setText(self.config.get("TABLES", "bulk_density"))
    self.lineEdt_HydraulicConductivityKr.setText(self.config.get("TABLES", "K_sat"))
    self.lineEdt_FieldCapacityCC.setText(self.config.get("TABLES", "T_fcap"))
    self.lineEdt_WiltingPointWP.setText(self.config.get("TABLES", "T_wp"))
    self.lineEdt_Saturation.setText(self.config.get("TABLES", "T_sat"))
    self.lineEdt_RootZoneThicknessZr.setText(
        self.config.get("TABLES", "rootzone_depth")
    )

    # Initial Soil Conditions
    self.doubleSpinBox_InitialSoilMoisture.setValue(
        self.config.getfloat("INITIAL_SOIL_CONDITIONS", "T_ini")
    )
    self.doubleSpinBox_BaseFlowInitial.setValue(
        self.config.getfloat("INITIAL_SOIL_CONDITIONS", "bfw_ini")
    )
    self.doubleSpinBox_BaseFlowLimit.setValue(
        self.config.getfloat("INITIAL_SOIL_CONDITIONS", "bfw_lim")
    )
    self.doubleSpinBox_TusInitial.setValue(
        self.config.getfloat("INITIAL_SOIL_CONDITIONS", "S_sat_ini")
    )

    # Land Use tab
    # Land Use Series
    if os.path.isdir(self.config.get("DIRECTORIES", "landuse")):
        tmpPath = getFirstFileNameMapSeries(self.config.get("DIRECTORIES", "landuse"))
        self.lineEdt_LandUseSeries.setText(os.path.normpath(tmpPath))
    else:
        self.lineEdt_LandUseSeries.setText(self.config.get("DIRECTORIES", "landuse"))

    # NDVI
    if os.path.isdir(self.config.get("DIRECTORIES", "ndvi")):
        tmpPath = getFirstFileNameMapSeries(self.config.get("DIRECTORIES", "ndvi"))
        self.lineEdt_NDVISeries.setText(tmpPath)
    else:
        self.lineEdt_NDVISeries.setText(self.config.get("DIRECTORIES", "ndvi"))

    self.lineEdt_NDVIMax.setText(self.config.get("RASTERS", "ndvi_max"))
    self.lineEdt_NDVIMin.setText(self.config.get("RASTERS", "ndvi_min"))

    # a
    self.lineEdt_a_i.setText(self.config.get("TABLES", "a_i"))
    self.lineEdt_a_o.setText(self.config.get("TABLES", "a_o"))
    self.lineEdt_a_s.setText(self.config.get("TABLES", "a_s"))
    self.lineEdt_a_v.setText(self.config.get("TABLES", "a_v"))

    # Manning
    self.lineEdt_Manning.setText(self.config.get("TABLES", "manning"))

    # Kc
    self.lineEdt_KcMax.setText(self.config.get("TABLES", "K_c_max"))
    self.lineEdt_KcMin.setText(self.config.get("TABLES", "K_c_min"))

    # Fpar
    self.doubleSpinBox_FparMax.setValue(self.config.getfloat("CONSTANTS", "fpar_max"))
    self.doubleSpinBox_FparMin.setValue(self.config.getfloat("CONSTANTS", "fpar_min"))

    # Interception
    self.doubleSpinBox_Interception.setValue(self.config.getfloat("CONSTANTS", "i_imp"))

    # Leaf Area Index
    self.doubleSpinBox_LeafAreaIndexMax.setValue(
        self.config.getfloat("CONSTANTS", "lai_max")
    )

    # Climate tab
    if os.path.isdir(self.config.get("DIRECTORIES", "prec")):
        tmpPath = getFirstFileNameMapSeries(self.config.get("DIRECTORIES", "prec"))
        self.lineEdt_Precipitation.setText(tmpPath)
    else:
        self.lineEdt_Precipitation.setText(self.config.get("DIRECTORIES", "prec"))

    if os.path.isdir(self.config.get("DIRECTORIES", "etp")):
        tmpPath = getFirstFileNameMapSeries(self.config.get("DIRECTORIES", "etp"))
        self.lineEdt_EvapoTranspiration.setText(tmpPath)
    else:
        self.lineEdt_EvapoTranspiration.setText(self.config.get("DIRECTORIES", "etp"))

    if os.path.isdir(self.config.get("DIRECTORIES", "kp")):
        tmpPath = getFirstFileNameMapSeries(self.config.get("DIRECTORIES", "kp"))
        self.lineEdt_PanCoefficientKp.setText(tmpPath)
    else:
        self.lineEdt_PanCoefficientKp.setText(self.config.get("DIRECTORIES", "kp"))

    self.lineEdt_RainyDays.setText(self.config.get("TABLES", "rainydays"))

    # Parameters tab
    # Model Parameters
    self.doubleSpinBox_ExponentCh.setValue(self.config.getfloat("CALIBRATION", "b"))

    self.doubleSpinBox_DelayFactor.setValue(self.config.getfloat("CALIBRATION", "x"))
    self.doubleSpinBox_RegionalConsecutiveDrynessLevel.setValue(
        self.config.getfloat("CALIBRATION", "rcd")
    )
    self.doubleSpinBox_DelayCoefficientBaseFlow.setValue(
        self.config.getfloat("CALIBRATION", "alpha_gw")
    )
    self.doubleSpinBox_PartitioningCoefficientRelatedSoil.setValue(
        self.config.getfloat("CALIBRATION", "f")
    )
    self.doubleSpinBox_InterceptionCalibrationAlpha.setValue(
        self.config.getfloat("CALIBRATION", "alpha")
    )

    # Weight Factors
    self.doubleSpinBox_ManningRelatedWeightFactor.setValue(
        self.config.getfloat("CALIBRATION", "w_1")
    )
    self.doubleSpinBox_SoilRelatedWeightFactor.setValue(
        self.config.getfloat("CALIBRATION", "w_2")
    )
    self.doubleSpinBox_SlopeRelatedWeightFactor.setValue(
        self.config.getfloat("CALIBRATION", "w_3")
    )

    # Run tab
    # Generate Files
    self.checkBox_InterceptionInt.setChecked(
        self.config.getboolean("GENERATE_FILE", "itp")
    )
    self.checkBox_InterceptionEb.setChecked(
        self.config.getboolean("GENERATE_FILE", "bfw")
    )
    self.checkBox_EvapotranspirationEvp.setChecked(
        self.config.getboolean("GENERATE_FILE", "eta")
    )
    self.checkBox_RechargeRec.setChecked(self.config.getboolean("GENERATE_FILE", "rec"))
    self.checkBox_SoilMoistureTur.setChecked(
        self.config.getboolean("GENERATE_FILE", "smc")
    )
    self.checkBox_LateralFlowLf.setChecked(
        self.config.getboolean("GENERATE_FILE", "lfw")
    )
    self.checkBox_RunoffEsd.setChecked(self.config.getboolean("GENERATE_FILE", "srn"))
    self.checkBox_RunoffVazao.setChecked(self.config.getboolean("GENERATE_FILE", "rnf"))
