import configparser
import os
import re

from qgis.core import QgsProject
from qgis.PyQt.QtCore import QDate, QThread, pyqtSignal
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox

try:
    from ..dependencies import PydanticUnavailable, ensure_pydantic
except ImportError:
    from dependencies import PydanticUnavailable, ensure_pydantic

try:
    from ..utils.series import getFirstFileNameMapSeries, splitDirFilePrefix
    from ..validation.legacy_json import read_legacy_json, write_legacy_json
    from ..validation.schemas import defaultConfigSchema
except ImportError:
    from utils.series import getFirstFileNameMapSeries, splitDirFilePrefix
    from validation.legacy_json import read_legacy_json, write_legacy_json
    from validation.schemas import defaultConfigSchema

_PROJECT_FILTER = "RUBEM project (*.json)"


def _snapshot_config(config):
    """Copy section values so a deferred write cannot see later GUI edits."""
    snapshot = configparser.ConfigParser()
    snapshot.read_dict(
        {section: dict(config.items(section)) for section in config.sections()}
    )
    return snapshot


def resolve_project_path(self, path: str) -> str:
    """Resolve a project-relative path against the open project file directory.

    Absolute paths are returned unchanged. Relative paths follow the same
    rule as RUBEM ``resolve_paths``: when a project file is open they are
    anchored on that file's directory, not on the process working directory.
    Without an open project file the path is left unchanged (CWD-relative).
    """
    if not path:
        return path
    if os.path.isabs(path):
        return path
    project = getattr(self, "projectFilePath", None) or ""
    if not project:
        return path
    return os.path.normpath(os.path.join(os.path.dirname(project), path))


def _series_field_text(self, directory_value: str, prefix_key: str = "") -> str:
    """Text for a map-series line edit from a stored directory value.

    Resolves relative directories against the project file. When the directory
    exists, prefer a map whose alphabetic prefix matches the stored
    ``FILENAME_PREFIXES`` entry so Save cannot replace that prefix with
    another series that happens to sort first. If no matching map exists,
    keep the stored directory string (never ``os.path.normpath("")`` → ``.``).
    """
    if not directory_value:
        return ""
    resolved = resolve_project_path(self, directory_value)
    if os.path.isdir(resolved):
        prefix = ""
        if prefix_key:
            prefix = self.config.get("FILENAME_PREFIXES", prefix_key, fallback="")
        first = getFirstFileNameMapSeries(resolved, prefix=prefix)
        if not first:
            return directory_value
        # Keep a relative stored dir portable: show
        # ``data/prec/rain00000.001`` rather than an absolute map path that
        # ``_apply_series`` would then persist as an absolute DIRECTORIES.
        if not os.path.isabs(directory_value):
            return os.path.join(directory_value, os.path.basename(first))
        return first
    return directory_value


def _spin_text(self, spin, section, option):
    """Keep a stored decimal when the widget only repeats its own rounding."""
    shown = spin.value()
    try:
        stored_value = self.config.getfloat(section, option)
        stored_text = self.config.get(section, option)
    except Exception:
        return repr(shown)
    tolerance = 0.5 * (10 ** (-spin.decimals()))
    if abs(stored_value - shown) <= tolerance:
        return stored_text
    return repr(shown)


def _apply_series(self, text, directory_key, prefix_key):
    """Update a series directory without erasing a prefix the widget does not show.

    The climate/land-use line edits show either a selected series file
    (``rain00000.001``) or only the directory when no map is found yet.
    ``splitDirFilePrefix`` must not treat a bare directory such as
    ``data/prec`` as parent ``data/`` plus prefix ``prec``.
    """
    text = (text or "").strip()
    stored = self.config.get("FILENAME_PREFIXES", prefix_key, fallback="")
    if not text:
        self.config.set("DIRECTORIES", directory_key, "")
        self.config.set("FILENAME_PREFIXES", prefix_key, stored)
        return

    resolved = resolve_project_path(self, text)
    basename = os.path.basename(text.rstrip("/\\"))
    _, extension = os.path.splitext(basename)
    # Map-series picks look like ``rain00000.001`` / ``kp000000.001``.
    # A non-existent dotted path (``data/prec.v2``) is still a directory value.
    looks_like_map = bool(re.fullmatch(r"[A-Za-z]+\d+\.\d+", basename))
    directory_only = (
        text.endswith(("/", "\\"))
        or os.path.isdir(resolved)
        or extension == ""
        or (
            not looks_like_map
            and not os.path.isfile(resolved)
            and not os.path.isfile(text)
        )
    )
    if directory_only:
        self.config.set("DIRECTORIES", directory_key, text)
        self.config.set("FILENAME_PREFIXES", prefix_key, stored)
        return

    # Prefer the typed path when it is still relative so Open+Save stays
    # portable: ``data/prec/rain…`` keeps ``data/prec/``, and a bare
    # ``rain00000.001`` splits to ``./`` then recovers the stored relative
    # dir (never the absolute project-resolved parent).
    keep_relative = not os.path.isabs(text) and bool(os.path.dirname(text))
    bare_relative = not os.path.isabs(text) and not os.path.dirname(text)
    split_source = (
        resolved
        if os.path.isfile(resolved) and not keep_relative and not bare_relative
        else text
    )
    tmp_path, tmp_prefix = splitDirFilePrefix(split_source)
    if tmp_path in ("/", "./") or tmp_path.strip("/\\") == "":
        stored_dir = self.config.get("DIRECTORIES", directory_key, fallback="")
        if stored_dir:
            tmp_path = (
                stored_dir
                if stored_dir.endswith(("/", "\\"))
                else f"{stored_dir.rstrip('/\\')}/"
            )
        else:
            tmp_path = "./"
    if tmp_prefix == "" and stored:
        tmp_prefix = stored
    self.config.set("DIRECTORIES", directory_key, tmp_path)
    self.config.set("FILENAME_PREFIXES", prefix_key, tmp_prefix)


class _PydanticInstallThread(QThread):
    """Install Pydantic off the GUI thread."""

    succeeded = pyqtSignal()
    failed = pyqtSignal(str)

    def run(self):
        try:
            ensure_pydantic(install=True)
        except Exception as exc:
            self.failed.emit(str(exc))
        else:
            self.succeeded.emit()


def _prompt_pydantic_install(self, exc, retry):
    """Ask once, then install off the GUI thread and call ``retry``."""
    if getattr(self, "_pydantic_installing", False):
        return None
    answer = QMessageBox.question(
        self,
        "RUBEM Hydrological",
        str(exc) + "\n\nInstall it into an isolated environment?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes,
    )
    if answer != QMessageBox.StandardButton.Yes:
        self.textBrowser_log.append(str(exc))
        return None
    self._pydantic_installing = True
    worker = _PydanticInstallThread()

    def finished_ok():
        self._pydantic_installing = False
        self.textBrowser_log.append("Pydantic is available.")
        retry()

    def finished_badly(message):
        self._pydantic_installing = False
        self.textBrowser_log.append(message)

    worker.succeeded.connect(finished_ok)
    worker.failed.connect(finished_badly)
    worker.finished.connect(worker.deleteLater)
    self._pydantic_worker = worker
    worker.start()
    return None


def _write_project(self, selected_file_path, after=None):
    """Validate and write the project with the submodule's pydantic model.

    :return: True when the JSON file was written in this call, False when
        the write failed, or None when it waits on a Pydantic install.
    :rtype: bool or None
    """

    def write(config):
        try:
            write_legacy_json(config, selected_file_path)
        except (ValueError, OSError) as exc:
            self.textBrowser_log.append(str(exc))
            return False
        return True

    try:
        return write(self.config)
    except PydanticUnavailable as exc:
        # Capture values now. New/Open/Close or GUI edits must not change
        # what the deferred retry writes over the user's project file.
        snapshot = _snapshot_config(self.config)

        def retry():
            if write(snapshot) and after is not None:
                after()

        return _prompt_pydantic_install(self, exc, retry)


def _read_project(self, config_file_path, after=None):
    """Read a project and validate it with the submodule's pydantic model."""

    def read():
        return read_legacy_json(config_file_path)

    try:
        return read()
    except PydanticUnavailable as exc:

        def retry():
            loaded = read()
            if loaded is not None and after is not None:
                after(loaded)

        return _prompt_pydantic_install(self, exc, retry)


def newProject(self, supressed=False):
    """[summary].

    :Slot signal: clicked
    :Signal sender: pushButton_NewProject

    :return: [description]
    :rtype: [type]
    """
    if getattr(self, "_pydantic_installing", False):
        self.textBrowser_log.append(
            "Wait for the dependency installation to finish before creating a new project."
        )
        return None

    # TODO: docstring
    def setupNewProject():
        """[summary]."""

        self.qgisProject = QgsProject.instance()
        if self.qgisProject.isDirty():
            response = self.getUserRetQGISCurProj()
            if response == QMessageBox.StandardButton.Ok:
                # self.qgisProject.clear()
                self.iface.newProject()
            else:
                return None

        self.textBrowser_log.clear()
        # Fresh parser: read_dict only overlays keys and would keep optional
        # fields (ldd, alignment, …) loaded from a previous Open.
        self.config = configparser.ConfigParser()
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
        if response == QMessageBox.StandardButton.Save:
            if not self.saveProject(after=setupNewProject):
                return None
            setupNewProject()
        # Don't save project before creating a new one
        elif response == QMessageBox.StandardButton.Discard:
            setupNewProject()
        elif response == QMessageBox.StandardButton.Cancel:
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
    if getattr(self, "_pydantic_installing", False):
        self.textBrowser_log.append(
            "Wait for the dependency installation to finish before opening a project."
        )
        return None

    # TODO: docstring
    def setupOpenedProject():
        """[summary]."""
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            caption="Open Project",
            directory=self.lastOpenedDirectory,
            filter=_PROJECT_FILTER,
        )
        if filePath:

            def apply_loaded(loaded):
                """Apply a project that was already read from JSON.

                The QGIS project is cleared only after that read succeeded
                and, when it is dirty, the user agreed to replace it.
                """
                self.qgisProject = QgsProject.instance()
                if self.qgisProject.isDirty():
                    response = self.getUserRetQGISCurProj()
                    if response != QMessageBox.StandardButton.Ok:
                        return None
                    # self.qgisProject.clear()
                    self.iface.newProject()

                self.textBrowser_log.clear()
                self.config = loaded
                self.projectFilePath = filePath
                self.hasCurrentProject = True
                self.updateGUIFromConfig()
                self.pushButton_SaveProject.setEnabled(True)
                self.pushButton_SaveAsProject.setEnabled(True)
                self.tabWidget.setEnabled(True)
                output = resolve_project_path(
                    self, self.config.get("DIRECTORIES", "output")
                )
                if os.path.exists(output) and os.listdir(output):
                    self.tab_Results.setEnabled(True)
                    self.populateMapSeriesTree()
                    self.populateTimeSeriesTree()
                self.qgisProject.read(os.path.splitext(filePath)[0] + ".qgs")
                self.updateWindowTitle()

            try:
                loaded = _read_project(self, filePath, after=apply_loaded)
            except (OSError, ValueError, RuntimeError) as exc:
                self.textBrowser_log.append(str(exc))
                return
            if loaded is None:
                return
            apply_loaded(loaded)

    # Check if there is already a current project and it has been
    # modified then ask to save it
    if self.hasCurrentProject and self.hasProjectBeenModified:
        response = self.getUserRetSaveCurProj()
        # Save project before opening a project file
        if response == QMessageBox.StandardButton.Save:
            if not self.saveProject(after=setupOpenedProject):
                return None
            setupOpenedProject()
        # Don't save project before opening a project file
        elif response == QMessageBox.StandardButton.Discard:
            setupOpenedProject()
        elif response == QMessageBox.StandardButton.Cancel:
            # User canceled saving the current project
            # and opening another project file
            return None
    # If there is no open projet select a project file
    else:
        setupOpenedProject()


def saveProject(self, filePath=None, caption=None, after=None):
    """Save the values present in the configuration dictionary to a\n
        specified file.

    :Slot signal: clicked
    :Signal sender: pushButton_SaveProject

    :param filePath: Valid path to the configuration file, defaults
    to None (slot).
    :type filePath: String, optional (slot)

    :param after: Called only after a deferred Pydantic install writes
        the JSON and ``finish_save`` runs. An immediate write does not
        call it.
    :type after: callable, optional

    :return: True only after the JSON file was written and the project
        state was updated in this call. False when the user cancels, the
        write is deferred, or the write fails.
    :rtype: bool
    """
    # Line edits only mark the project dirty via textChanged. Pull widget
    # values into ``self.config`` before any write so Save cannot discard
    # typed paths while clearing the modified flag.
    self.updateConfigFromGUI()

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
                filter=_PROJECT_FILTER,
            )
        else:
            tmpFilePath, _ = QFileDialog.getSaveFileName(
                self,
                caption="Save project",
                directory=self.lastOpenedDirectory,
                filter=_PROJECT_FILTER,
            )
        return tmpFilePath

    # TODO: docstring
    def setupProjectFileWrite(selectedFilePath):
        """[summary].

        :param selectedFilePath: [description].
        :type selectedFilePath: [type]
        """
        if not selectedFilePath.lower().endswith(".json"):
            selectedFilePath += ".json"

        def finish_save():
            self.qgisProject = QgsProject.instance()
            self.qgisProject.write(os.path.splitext(selectedFilePath)[0] + ".qgs")
            self.textBrowser_log.append("Project file saved in " + selectedFilePath)
            self.hasCurrentProject = True
            self.hasProjectBeenModified = False
            self.projectFilePath = selectedFilePath
            self.updateWindowTitle()

        def deferred_after():
            finish_save()
            if after is not None:
                after()

        written = _write_project(self, selectedFilePath, after=deferred_after)
        if not written:
            return False
        finish_save()
        return True

    # Ask user for project file path
    # --> Call this function without any arguments
    # --> Clicking 'Save' in the GUI without a current project
    # --> Clicking 'New' in the GUI without a current project
    if not filePath and not self.projectFilePath:
        retFilePath = setupFileDialog()
        # Check if the user has selected a path to the project file
        if not retFilePath:
            return False
        return setupProjectFileWrite(retFilePath)

    # Save project with project file path already defined in object
    # instance
    # --> Clicking 'Save' in the GUI with a current project
    elif not filePath and self.projectFilePath and not caption:
        return setupProjectFileWrite(self.projectFilePath)

    # Ask the user where to save the project file as...
    # Only the saveAsProject() function sets the caption argument
    # when calling this function.
    # --> Clicking 'Save As..' in the GUI with a current project
    # --> Clicking 'New' in the GUI with a current project
    elif not filePath and self.projectFilePath and caption:
        retFilePath = setupFileDialog()
        # Check if the user has selected a path to the project file
        if not retFilePath:
            return False
        return setupProjectFileWrite(retFilePath)

    # Save the project using the filePath argument as the project file
    # path.
    # In this case it doesn't matter if self.projectFilePath is set or not
    # --> Call this function with filePath argument
    else:
        return setupProjectFileWrite(filePath)


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
    self.config.set(
        "GRID", "grid", _spin_text(self, self.doubleSpinBox_GridSize, "GRID", "grid")
    )

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
        _spin_text(
            self,
            self.doubleSpinBox_InitialSoilMoisture,
            "INITIAL_SOIL_CONDITIONS",
            "T_ini",
        ),
    )
    self.config.set(
        "INITIAL_SOIL_CONDITIONS",
        "bfw_ini",
        _spin_text(
            self,
            self.doubleSpinBox_BaseFlowInitial,
            "INITIAL_SOIL_CONDITIONS",
            "bfw_ini",
        ),
    )
    self.config.set(
        "INITIAL_SOIL_CONDITIONS",
        "bfw_lim",
        _spin_text(
            self, self.doubleSpinBox_BaseFlowLimit, "INITIAL_SOIL_CONDITIONS", "bfw_lim"
        ),
    )
    self.config.set(
        "INITIAL_SOIL_CONDITIONS",
        "S_sat_ini",
        _spin_text(
            self, self.doubleSpinBox_TusInitial, "INITIAL_SOIL_CONDITIONS", "S_sat_ini"
        ),
    )

    # Land Use tab
    # Land Use Series
    _apply_series(self, self.lineEdt_LandUseSeries.text(), "landuse", "landuse_prefix")
    _apply_series(self, self.lineEdt_NDVISeries.text(), "ndvi", "ndvi_prefix")

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
    self.config.set(
        "CONSTANTS",
        "fpar_max",
        _spin_text(self, self.doubleSpinBox_FparMax, "CONSTANTS", "fpar_max"),
    )
    self.config.set(
        "CONSTANTS",
        "fpar_min",
        _spin_text(self, self.doubleSpinBox_FparMin, "CONSTANTS", "fpar_min"),
    )

    # Interception
    self.config.set(
        "CONSTANTS",
        "i_imp",
        _spin_text(self, self.doubleSpinBox_Interception, "CONSTANTS", "i_imp"),
    )

    # Leaf Area Index
    self.config.set(
        "CONSTANTS",
        "lai_max",
        _spin_text(self, self.doubleSpinBox_LeafAreaIndexMax, "CONSTANTS", "lai_max"),
    )

    # Climate tab
    _apply_series(self, self.lineEdt_Precipitation.text(), "prec", "prec_prefix")
    _apply_series(self, self.lineEdt_EvapoTranspiration.text(), "etp", "etp_prefix")
    _apply_series(self, self.lineEdt_PanCoefficientKp.text(), "kp", "kp_prefix")

    self.config.set("TABLES", "rainydays", self.lineEdt_RainyDays.text())

    # Parameters tab
    # Model Parameters
    self.config.set(
        "CALIBRATION",
        "b",
        _spin_text(self, self.doubleSpinBox_ExponentCh, "CALIBRATION", "b"),
    )
    self.config.set(
        "CALIBRATION",
        "x",
        _spin_text(self, self.doubleSpinBox_DelayFactor, "CALIBRATION", "x"),
    )

    self.config.set(
        "CALIBRATION",
        "rcd",
        _spin_text(
            self,
            self.doubleSpinBox_RegionalConsecutiveDrynessLevel,
            "CALIBRATION",
            "rcd",
        ),
    )
    self.config.set(
        "CALIBRATION",
        "alpha_gw",
        _spin_text(
            self, self.doubleSpinBox_DelayCoefficientBaseFlow, "CALIBRATION", "alpha_gw"
        ),
    )
    self.config.set(
        "CALIBRATION",
        "f",
        _spin_text(
            self,
            self.doubleSpinBox_PartitioningCoefficientRelatedSoil,
            "CALIBRATION",
            "f",
        ),
    )
    self.config.set(
        "CALIBRATION",
        "alpha",
        _spin_text(
            self,
            self.doubleSpinBox_InterceptionCalibrationAlpha,
            "CALIBRATION",
            "alpha",
        ),
    )

    # Weight Factors
    self.config.set(
        "CALIBRATION",
        "w_1",
        _spin_text(
            self, self.doubleSpinBox_ManningRelatedWeightFactor, "CALIBRATION", "w_1"
        ),
    )
    self.config.set(
        "CALIBRATION",
        "w_2",
        _spin_text(
            self, self.doubleSpinBox_SoilRelatedWeightFactor, "CALIBRATION", "w_2"
        ),
    )
    self.config.set(
        "CALIBRATION",
        "w_3",
        _spin_text(
            self, self.doubleSpinBox_SlopeRelatedWeightFactor, "CALIBRATION", "w_3"
        ),
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
    self.config.set(
        "GENERATE_FILE", "arn", str(self.checkBox_AccumulatedRunoffArn.isChecked())
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

    if not str(configFilePath).lower().endswith(".json"):
        self.textBrowser_log.append("Project files are the JSON RUBEM reads.")
        return

    self.config = _read_project(self, configFilePath)

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
    self.lineEdt_LandUseSeries.setText(
        _series_field_text(
            self, self.config.get("DIRECTORIES", "landuse"), "landuse_prefix"
        )
    )

    # NDVI
    self.lineEdt_NDVISeries.setText(
        _series_field_text(self, self.config.get("DIRECTORIES", "ndvi"), "ndvi_prefix")
    )

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
    self.lineEdt_Precipitation.setText(
        _series_field_text(self, self.config.get("DIRECTORIES", "prec"), "prec_prefix")
    )
    self.lineEdt_EvapoTranspiration.setText(
        _series_field_text(self, self.config.get("DIRECTORIES", "etp"), "etp_prefix")
    )
    self.lineEdt_PanCoefficientKp.setText(
        _series_field_text(self, self.config.get("DIRECTORIES", "kp"), "kp_prefix")
    )

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
    for spin, option in (
        (self.doubleSpinBox_ManningRelatedWeightFactor, "w_1"),
        (self.doubleSpinBox_SoilRelatedWeightFactor, "w_2"),
        (self.doubleSpinBox_SlopeRelatedWeightFactor, "w_3"),
    ):
        spin.setDecimals(10)
        spin.setValue(self.config.getfloat("CALIBRATION", option))

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
    self.checkBox_AccumulatedRunoffArn.setChecked(
        self.config.getboolean("GENERATE_FILE", "arn")
    )
