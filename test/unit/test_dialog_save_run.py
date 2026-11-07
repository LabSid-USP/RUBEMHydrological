"""Dialog save, open, run, and close guards that do not need a QGIS GUI."""

from __future__ import annotations

import ast
import configparser
import sys
import tempfile
import traceback
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

try:
    import pytest
except ImportError:  # pragma: no cover - local run without the test extra

    class _Mark:
        def unit(self, fn):
            return fn

    class pytest:  # noqa: N801 - stand-in for the real module
        mark = _Mark()


ROOT = Path(__file__).resolve().parents[2]


def _ensure_qgis_importable() -> None:
    """Install stand-ins so dialog modules import without the QGIS GUI."""
    try:
        import qgis.PyQt.QtWidgets  # noqa: F401

        return
    except ImportError:
        pass

    def module(name: str) -> types.ModuleType:
        created = types.ModuleType(name)
        sys.modules[name] = created
        return created

    qgis = module("qgis")
    core = module("qgis.core")
    pyqt = module("qgis.PyQt")
    qt_core = module("qgis.PyQt.QtCore")
    qt_widgets = module("qgis.PyQt.QtWidgets")
    module("qgis.PyQt.QtGui")
    module("qgis.gui")
    qgis.core = core
    qgis.PyQt = pyqt
    pyqt.QtCore = qt_core
    pyqt.QtWidgets = qt_widgets

    class Qgis:
        Critical = 2
        Success = 3

    class QgsMessageLog:
        @staticmethod
        def logMessage(*_args, **_kwargs):
            return None

    class QgsProject:
        @staticmethod
        def instance():
            return MagicMock()

    class StandardButton:
        Ok = "Ok"
        Yes = "Yes"
        No = "No"
        Save = "Save"
        Discard = "Discard"
        Cancel = "Cancel"

    class QMessageBox:
        @staticmethod
        def question(*_args, **_kwargs):
            return StandardButton.No

    QMessageBox.StandardButton = StandardButton

    class QFileDialog:
        @staticmethod
        def getOpenFileName(*_args, **_kwargs):
            return "", ""

        @staticmethod
        def getSaveFileName(*_args, **_kwargs):
            return "", ""

    class QThread:
        def start(self):
            return None

        def isRunning(self):
            return False

    class QObject:
        def __init__(self, *_args, **_kwargs):
            return None

        def moveToThread(self, _thread):
            return None

    class _Signal:
        def connect(self, *_args, **_kwargs):
            return None

        def emit(self, *_args, **_kwargs):
            return None

    def pyqtSignal(*_args):
        return _Signal()

    core.Qgis = Qgis
    core.QgsMessageLog = QgsMessageLog
    core.QgsProject = QgsProject
    qt_widgets.QMessageBox = QMessageBox
    qt_widgets.QFileDialog = QFileDialog
    qt_core.QThread = QThread
    qt_core.QObject = QObject
    qt_core.QDate = object
    qt_core.pyqtSignal = pyqtSignal
    qt_core.Qt = SimpleNamespace()


def _load_dialog_modules():
    """Import the dialog helpers without executing ``plugin/dialog/__init__.py``.

    The stub ``plugin.dialog`` package is recorded so ``teardown_module`` can
    drop it and avoid contaminating a later GUI/integration collection in the
    same interpreter (unit and GUI jobs still run in separate processes).
    """
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    _ensure_qgis_importable()
    created_stub = False
    if "plugin.dialog" not in sys.modules:
        package = types.ModuleType("plugin.dialog")
        package.__path__ = [str(ROOT / "plugin" / "dialog")]
        package.__package__ = "plugin.dialog"
        package.__file__ = str(ROOT / "plugin" / "dialog" / "__init__.py")
        sys.modules["plugin.dialog"] = package
        created_stub = True
    import plugin.dialog._project as project
    import plugin.dialog._window as window
    import plugin.dialog._worker as worker

    return project, window, worker, created_stub


project, window, worker, _DIALOG_STUB_CREATED = _load_dialog_modules()


def teardown_module(_module=None) -> None:
    """Remove the stub dialog package inserted for helper-module imports."""
    if not _DIALOG_STUB_CREATED:
        return
    for name in list(sys.modules):
        if name == "plugin.dialog" or name.startswith("plugin.dialog."):
            del sys.modules[name]


class _Log:
    """Capture ``textBrowser_log`` lines."""

    def __init__(self) -> None:
        self.lines: list[str] = []

    def append(self, text: str) -> None:
        self.lines.append(str(text))

    def clear(self) -> None:
        self.lines.clear()


def _dialog() -> SimpleNamespace:
    """Return a dialog-shaped object the free functions can use."""
    dialog = SimpleNamespace(
        textBrowser_log=_Log(),
        projectFilePath=None,
        hasCurrentProject=False,
        hasProjectBeenModified=False,
        lastOpenedDirectory="/tmp",
        config=configparser.ConfigParser(),
        iface=MagicMock(),
        qgisProject=MagicMock(),
        updateWindowTitle=MagicMock(),
        updateGUIFromConfig=MagicMock(),
        pushButton_SaveProject=MagicMock(),
        pushButton_SaveAsProject=MagicMock(),
        tabWidget=MagicMock(),
        tab_Results=MagicMock(),
        populateMapSeriesTree=MagicMock(),
        populateTimeSeriesTree=MagicMock(),
        getUserRetQGISCurProj=MagicMock(),
        getUserRetDirNotEmpty=MagicMock(),
        getUserRetSaveCurProj=MagicMock(),
        progressBar=MagicMock(),
        btn_Run=MagicMock(),
        btn_Cancel=MagicMock(),
        setWindowTitle=MagicMock(),
    )
    dialog.hasFilledAllFields = lambda: True
    dialog.updateConfigFromGUI = lambda: None
    dialog.saveProject = lambda *args, **kwargs: project.saveProject(
        dialog, *args, **kwargs
    )
    return dialog


def _qgis_project(*, dirty: bool) -> MagicMock:
    qgis_project = MagicMock()
    qgis_project.isDirty.return_value = dirty
    return qgis_project


def _loaded_config(output: str) -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    parser["DIRECTORIES"] = {"output": output}
    return parser


@pytest.mark.unit
def test_dialog_class_does_not_import_explain_cancel() -> None:
    """Fake Cancel was retired; Close uses ``reject`` / ``_may_leave_dialog``."""
    source = (ROOT / "plugin" / "dialog" / "__init__.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    found = False
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "_worker"
            and node.level == 1
        ):
            names = [alias.name for alias in node.names]
            assert "explainCancel" not in names
            assert "runLongTask" in names
            found = True
    assert found
    worker_src = (ROOT / "plugin" / "dialog" / "_worker.py").read_text(encoding="utf-8")
    assert "def explainCancel" not in worker_src
    assert "self.projectFilePath = retFilePath" not in (
        ROOT / "plugin" / "dialog" / "_project.py"
    ).read_text(encoding="utf-8")


@pytest.mark.unit
def test_dialog_class_imports_accumulated_runoff_arn_slot() -> None:
    """ARN generate-file slot is bound so setupUi can connect the checkbox."""
    source = (ROOT / "plugin" / "dialog" / "__init__.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    found = False
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "_tab_run"
            and node.level == 1
        ):
            names = [alias.name for alias in node.names]
            assert "setAccumulatedRunoffArnGenerateFile" in names
            assert "setRunoffVazaoGenerateFile" in names
            found = True
    assert found
    tab_run = (ROOT / "plugin" / "dialog" / "_tab_run.py").read_text(encoding="utf-8")
    assert "def setAccumulatedRunoffArnGenerateFile(self):" in tab_run


@pytest.mark.unit
def test_core_ui_uses_dialog_button_box_without_legacy_run_cancel() -> None:
    """Generated UI exposes ``button_box``; Run is created in ``_chrome``."""
    ui = (ROOT / "plugin" / "gui" / "generated" / "core_ui.py").read_text(
        encoding="utf-8"
    )
    assert "self.button_box" in ui
    assert "QDialogButtonBox" in ui
    assert "self.btn_Run" not in ui
    assert "self.btn_Cancel" not in ui
    chrome = (ROOT / "plugin" / "dialog" / "_chrome.py").read_text(encoding="utf-8")
    assert "btn_Run = dialog.button_box.addButton" in chrome
    window = (ROOT / "plugin" / "dialog" / "_window.py").read_text(encoding="utf-8")
    assert "btn_Run.setEnabled(False)" in window
    project = (ROOT / "plugin" / "dialog" / "_project.py").read_text(encoding="utf-8")
    assert project.count("btn_Run.setEnabled(True)") >= 2


@pytest.mark.unit
def test_dialog_class_binds_every_core_ui_slot() -> None:
    """Every ``connect(RUBEMHydrological.X)`` name must exist on the dialog class."""
    import re

    ui = (ROOT / "plugin" / "gui" / "generated" / "core_ui.py").read_text(
        encoding="utf-8"
    )
    slots = sorted(set(re.findall(r"connect\(RUBEMHydrological\.(\w+)\)", ui)))
    assert slots, "core_ui.py must connect at least one dialog slot"

    source = (ROOT / "plugin" / "dialog" / "__init__.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    class_body = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "RUBEMHydrologicalDialog":
            class_body = node
            break
    assert class_body is not None

    bound: set[str] = set()
    for node in class_body.body:
        if isinstance(node, ast.FunctionDef):
            bound.add(node.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                bound.add(alias.asname or alias.name)

    missing = [name for name in slots if name not in bound]
    assert (
        not missing
    ), "setupUi connects slots missing from RUBEMHydrologicalDialog: " + ", ".join(
        missing
    )


@pytest.mark.unit
def test_save_project_returns_true_only_after_json_and_finish() -> None:
    """An immediate write returns True and keeps the ``.json`` path."""
    dialog = _dialog()
    with tempfile.TemporaryDirectory() as directory:
        destination = Path(directory) / "basin"
        written: list[str] = []

        def write_json(_config, path):
            written.append(str(path))

        qgis_project = _qgis_project(dirty=False)
        with (
            patch.object(project, "write_legacy_json", write_json),
            patch.object(project.QgsProject, "instance", return_value=qgis_project),
        ):
            saved = project.saveProject(
                dialog,
                filePath=str(destination),
                after=lambda: written.append("after"),
            )

        assert saved is True
        assert written == [str(destination) + ".json"]
        assert dialog.projectFilePath == str(destination) + ".json"
        assert dialog.hasCurrentProject is True
        assert dialog.hasProjectBeenModified is False
        dialog.updateWindowTitle.assert_called_once_with()
        qgis_project.write.assert_called_once_with(str(destination) + ".qgs")


@pytest.mark.unit
def test_save_project_collects_gui_before_writing_json() -> None:
    """Save must pull widget values into config before any disk write."""
    dialog = _dialog()
    order: list[str] = []
    dialog.updateConfigFromGUI = lambda: order.append("gui")

    def write_json(_config, path):
        order.append("write")

    with tempfile.TemporaryDirectory() as directory:
        destination = Path(directory) / "basin.json"
        with (
            patch.object(project, "write_legacy_json", write_json),
            patch.object(
                project.QgsProject, "instance", return_value=_qgis_project(dirty=False)
            ),
        ):
            assert project.saveProject(dialog, filePath=str(destination)) is True

    assert order == ["gui", "write"]


@pytest.mark.unit
def test_save_dialog_path_is_not_replaced_by_unsuffixed_name() -> None:
    """The file dialog's path does not overwrite the suffixed project path."""
    dialog = _dialog()
    with tempfile.TemporaryDirectory() as directory:
        selected = str(Path(directory) / "basin")
        qgis_project = _qgis_project(dirty=False)
        with (
            patch.object(
                project.QFileDialog,
                "getSaveFileName",
                return_value=(selected, ""),
            ),
            patch.object(
                project, "write_legacy_json", lambda *_args, **_kwargs: ["ok"]
            ),
            patch.object(project.QgsProject, "instance", return_value=qgis_project),
        ):
            saved = project.saveProject(dialog)

        assert saved is True
        assert dialog.projectFilePath == selected + ".json"


@pytest.mark.unit
def test_save_project_returns_false_on_cancel() -> None:
    """Cancelling the file dialog does not write."""
    dialog = _dialog()
    with (
        patch.object(project.QFileDialog, "getSaveFileName", return_value=("", "")),
        patch.object(project, "write_legacy_json") as write_json,
    ):
        assert project.saveProject(dialog) is False
    write_json.assert_not_called()
    assert dialog.projectFilePath is None


@pytest.mark.unit
def test_save_project_logs_write_errors() -> None:
    """ValueError and OSError from the JSON write are logged and return False."""
    for exc_type in (ValueError, OSError):
        dialog = _dialog()
        dialog.projectFilePath = "/tmp/previous.json"

        def fail(_config, _path, exc_type=exc_type):
            raise exc_type("cannot write project")

        with patch.object(project, "write_legacy_json", fail):
            saved = project.saveProject(dialog, filePath="/tmp/next")

        assert saved is False
        assert dialog.projectFilePath == "/tmp/previous.json"
        assert dialog.textBrowser_log.lines == ["cannot write project"]


@pytest.mark.unit
def test_deferred_save_returns_false_and_continues_from_retry() -> None:
    """A Pydantic install defers success until the retry writes the file."""
    dialog = _dialog()
    with tempfile.TemporaryDirectory() as directory:
        _deferred_save(dialog, Path(directory) / "basin.json")


@pytest.mark.unit
def test_deferred_save_writes_config_snapshot_not_live_parser() -> None:
    """Retry must write the values captured before a deferred install."""
    dialog = _dialog()
    dialog.config["DIRECTORIES"] = {"output": "/real/out"}
    written: list[str] = []
    retries: list = []
    attempts = {"n": 0}

    def write_json(config, path):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise project.PydanticUnavailable("install pydantic")
        written.append(config.get("DIRECTORIES", "output"))

    def prompt(_self, _exc, retry):
        retries.append(retry)
        return None

    with tempfile.TemporaryDirectory() as directory:
        destination = Path(directory) / "basin.json"
        qgis_project = _qgis_project(dirty=False)
        with (
            patch.object(project, "write_legacy_json", write_json),
            patch.object(project, "_prompt_pydantic_install", prompt),
            patch.object(project.QgsProject, "instance", return_value=qgis_project),
        ):
            saved = project.saveProject(dialog, filePath=str(destination))
            assert saved is False
            dialog.config.set("DIRECTORIES", "output", "")
            retries[0]()

    assert written == ["/real/out"]


@pytest.mark.unit
def test_new_and_open_blocked_while_pydantic_installing() -> None:
    """New/Open must not replace config while a deferred install is running."""
    dialog = _dialog()
    dialog._pydantic_installing = True
    dialog.hasCurrentProject = True
    assert project.newProject(dialog) is None
    assert project.openProject(dialog) is None


@pytest.mark.unit
def test_new_project_drops_optional_keys_from_previous_open() -> None:
    """New must not keep ldd/alignment (etc.) loaded by a prior Open."""
    from plugin.validation.schemas import defaultConfigSchema

    dialog = _dialog()
    dialog.saveAsProject = MagicMock()
    dialog.config.read_dict(defaultConfigSchema)
    dialog.config.set("RASTERS", "ldd", "old/basin.ldd")
    dialog.config.set("SIM_TIME", "alignment", "01/01/2000")
    dialog.config.set("TABLES", "lai_max", "tables/lai.csv")
    dialog.hasCurrentProject = False

    qgis_project = _qgis_project(dirty=False)
    with patch.object(project.QgsProject, "instance", return_value=qgis_project):
        project.newProject(dialog)

    assert not dialog.config.has_option("RASTERS", "ldd")
    assert not dialog.config.has_option("SIM_TIME", "alignment")
    assert not dialog.config.has_option("TABLES", "lai_max")
    dialog.saveAsProject.assert_called_once_with(isNewProject=True)


def _deferred_save(dialog, destination: Path) -> None:
    continued: list[str] = []
    retries: list = []
    attempts = {"n": 0}

    def write_json(_config, path):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise project.PydanticUnavailable("install pydantic")
        assert str(path) == str(destination)

    def prompt(_self, _exc, retry):
        retries.append(retry)
        return None

    qgis_project = _qgis_project(dirty=False)
    with (
        patch.object(project, "write_legacy_json", write_json),
        patch.object(project, "_prompt_pydantic_install", prompt),
        patch.object(project.QgsProject, "instance", return_value=qgis_project),
    ):
        saved = project.saveProject(
            dialog,
            filePath=str(destination),
            after=lambda: continued.append("ran"),
        )
        assert saved is False
        assert continued == []
        assert dialog.projectFilePath is None
        assert dialog.hasCurrentProject is False
        retries[0]()

    assert continued == ["ran"]
    assert dialog.projectFilePath == str(destination)
    assert dialog.hasCurrentProject is True
    qgis_project.write.assert_called_once()


@pytest.mark.unit
def test_set_run_state_aborts_until_save_succeeds() -> None:
    """Run starts once for an immediate save and only after a deferred write."""
    dialog = _dialog()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "out"
        output.mkdir()
        dialog.config["DIRECTORIES"] = {"output": str(output)}
        dialog.projectFilePath = str(root / "basin.json")
        _assert_run_waits_for_save(dialog)


def _assert_run_waits_for_save(dialog) -> None:
    runs: list[str] = []
    dialog.runLongTask = lambda: runs.append("run")
    retries: list = []
    attempts = {"n": 0}

    def write_json(_config, _path):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise project.PydanticUnavailable("install pydantic")

    def prompt(_self, _exc, retry):
        retries.append(retry)
        return None

    with (
        patch.object(worker, "assert_ready", return_value=None),
        patch.object(project, "write_legacy_json", write_json),
        patch.object(project, "_prompt_pydantic_install", prompt),
        patch.object(
            project.QgsProject, "instance", return_value=_qgis_project(dirty=False)
        ),
    ):
        worker.setRunState(dialog)
        assert runs == []
        retries[0]()
        assert runs == ["run"]

        runs.clear()
        worker.setRunState(dialog)
        assert runs == ["run"]


@pytest.mark.unit
def test_set_run_state_stops_when_output_directory_is_kept() -> None:
    """A saved project still does not run when the user keeps the output folder."""
    dialog = _dialog()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "out"
        output.mkdir()
        (output / "old.map").write_text("x", encoding="utf-8")
        dialog.config["DIRECTORIES"] = {"output": str(output)}
        dialog.projectFilePath = str(root / "basin.json")
        _assert_kept_output_does_not_run(dialog)


@pytest.mark.unit
def test_set_run_state_resolves_relative_output_against_project() -> None:
    """A project-relative output directory is not read from the process CWD."""
    dialog = _dialog()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "results"
        output.mkdir()
        (output / "old.map").write_text("x", encoding="utf-8")
        dialog.config["DIRECTORIES"] = {"output": "results"}
        dialog.projectFilePath = str(root / "basin.json")
        dialog.runLongTask = MagicMock()
        dialog.getUserRetDirNotEmpty = lambda: worker.QMessageBox.StandardButton.Cancel
        with (
            patch.object(worker, "assert_ready", return_value=None),
            patch.object(
                project, "write_legacy_json", lambda *_args, **_kwargs: ["ok"]
            ),
            patch.object(
                project.QgsProject,
                "instance",
                return_value=_qgis_project(dirty=False),
            ),
        ):
            worker.setRunState(dialog)
        dialog.runLongTask.assert_not_called()


@pytest.mark.unit
def test_resolve_project_path_anchors_on_project_not_cwd(tmp_path, monkeypatch) -> None:
    """Relative paths match RUBEM: project directory wins over a CWD hit."""
    project_dir = tmp_path / "project"
    cwd_dir = tmp_path / "cwd"
    project_dir.mkdir()
    cwd_dir.mkdir()
    (project_dir / "dem.map").write_text("project", encoding="utf-8")
    (cwd_dir / "dem.map").write_text("cwd", encoding="utf-8")
    monkeypatch.chdir(cwd_dir)
    holder = SimpleNamespace(projectFilePath=str(project_dir / "basin.json"))
    resolved = project.resolve_project_path(holder, "dem.map")
    assert Path(resolved).resolve() == (project_dir / "dem.map").resolve()
    assert Path(resolved).read_text(encoding="utf-8") == "project"


@pytest.mark.unit
def test_form_exists_rejects_cwd_only_relative_path(tmp_path, monkeypatch) -> None:
    """Validation must not accept a relative path that exists only under CWD."""
    from plugin.dialog import _form_validation as form

    project_dir = tmp_path / "project"
    cwd_dir = tmp_path / "cwd"
    project_dir.mkdir()
    cwd_dir.mkdir()
    (cwd_dir / "soil.map").write_text("cwd", encoding="utf-8")
    monkeypatch.chdir(cwd_dir)
    dialog = _dialog()
    dialog.projectFilePath = str(project_dir / "basin.json")
    assert form._path_exists_for_project(dialog, "soil.map") is False


def _assert_kept_output_does_not_run(dialog) -> None:
    dialog.runLongTask = MagicMock()
    dialog.getUserRetDirNotEmpty = lambda: worker.QMessageBox.StandardButton.Cancel
    with (
        patch.object(worker, "assert_ready", return_value=None),
        patch.object(project, "write_legacy_json", lambda *_args, **_kwargs: ["ok"]),
        patch.object(
            project.QgsProject, "instance", return_value=_qgis_project(dirty=False)
        ),
    ):
        worker.setRunState(dialog)
    dialog.runLongTask.assert_not_called()


@pytest.mark.unit
def test_open_reads_json_before_clearing_qgis() -> None:
    """``iface.newProject`` runs only after a successful read and a dirty confirm."""
    dialog = _dialog()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        chosen = str(root / "basin.json")
        order: list[str] = []

        def read_json(path):
            order.append("read")
            assert path == chosen
            return _loaded_config(str(root / "missing-output"))

        def new_project():
            order.append("newProject")

        dialog.iface.newProject = new_project
        dialog.getUserRetQGISCurProj = lambda: project.QMessageBox.StandardButton.Ok
        qgis_project = _qgis_project(dirty=True)
        with (
            patch.object(
                project.QFileDialog, "getOpenFileName", return_value=(chosen, "")
            ),
            patch.object(project, "read_legacy_json", read_json),
            patch.object(project.QgsProject, "instance", return_value=qgis_project),
        ):
            project.openProject(dialog)

        assert order == ["read", "newProject"]
        assert dialog.projectFilePath == chosen
        qgis_project.read.assert_called_once_with(str(root / "basin.qgs"))


@pytest.mark.unit
def test_open_does_not_clear_qgis_when_json_is_invalid() -> None:
    """A failed read leaves the QGIS project alone."""
    dialog = _dialog()
    dialog.getUserRetQGISCurProj = MagicMock()

    def read_json(_path):
        raise ValueError("not legacy json")

    with (
        patch.object(
            project.QFileDialog,
            "getOpenFileName",
            return_value=(str(Path(tempfile.gettempdir()) / "bad.json"), ""),
        ),
        patch.object(project, "read_legacy_json", read_json),
        patch.object(
            project.QgsProject, "instance", return_value=_qgis_project(dirty=True)
        ),
    ):
        project.openProject(dialog)

    dialog.iface.newProject.assert_not_called()
    dialog.getUserRetQGISCurProj.assert_not_called()
    assert dialog.projectFilePath is None
    assert dialog.textBrowser_log.lines == ["not legacy json"]


@pytest.mark.unit
def test_open_does_not_clear_qgis_when_user_keeps_dirty_project() -> None:
    """A valid file is not applied when the user keeps the dirty QGIS project."""
    dialog = _dialog()
    dialog.getUserRetQGISCurProj = lambda: project.QMessageBox.StandardButton.Cancel
    qgis_project = _qgis_project(dirty=True)
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        with (
            patch.object(
                project.QFileDialog,
                "getOpenFileName",
                return_value=(str(root / "basin.json"), ""),
            ),
            patch.object(
                project,
                "read_legacy_json",
                lambda _path: _loaded_config(str(root / "missing-output")),
            ),
            patch.object(project.QgsProject, "instance", return_value=qgis_project),
        ):
            project.openProject(dialog)

    dialog.iface.newProject.assert_not_called()
    qgis_project.read.assert_not_called()
    assert dialog.projectFilePath is None


@pytest.mark.unit
def test_open_deferred_read_clears_qgis_only_after_retry() -> None:
    """A deferred open does not call ``newProject`` until the read succeeds."""
    dialog = _dialog()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        chosen = str(root / "basin.json")
        order: list[str] = []
        retries: list = []
        attempts = {"n": 0}

        def read_json(_path):
            attempts["n"] += 1
            order.append("read")
            if attempts["n"] == 1:
                raise project.PydanticUnavailable("install pydantic")
            return _loaded_config(str(root / "missing-output"))

        def prompt(_self, _exc, retry):
            retries.append(retry)
            return None

        def new_project():
            order.append("newProject")

        dialog.iface.newProject = new_project
        dialog.getUserRetQGISCurProj = lambda: project.QMessageBox.StandardButton.Ok
        with (
            patch.object(
                project.QFileDialog, "getOpenFileName", return_value=(chosen, "")
            ),
            patch.object(project, "read_legacy_json", read_json),
            patch.object(project, "_prompt_pydantic_install", prompt),
            patch.object(
                project.QgsProject, "instance", return_value=_qgis_project(dirty=True)
            ),
        ):
            project.openProject(dialog)
            assert order == ["read"]
            assert dialog.projectFilePath is None
            retries[0]()

        assert order == ["read", "read", "newProject"]
        assert dialog.projectFilePath == chosen


@pytest.mark.unit
def test_deferred_read_retry_logs_validation_errors_without_raising() -> None:
    """A post-install read failure must not escape the Qt signal slot."""
    dialog = _dialog()
    retries: list = []
    attempts = {"n": 0}

    def read_json(_path):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise project.PydanticUnavailable("install pydantic")
        raise ValueError("Conflicting values for DIRECTORIES.kp")

    def prompt(_self, _exc, retry):
        retries.append(retry)
        return None

    with (
        patch.object(project, "read_legacy_json", read_json),
        patch.object(project, "_prompt_pydantic_install", prompt),
    ):
        assert project._read_project(dialog, "/tmp/basin.json") is None
        retries[0]()

    assert any("Conflicting values" in line for line in dialog.textBrowser_log.lines)


@pytest.mark.unit
def test_close_event_ignores_a_running_worker_without_killing_it() -> None:
    """A running model thread blocks close and is not killed."""
    dialog = _dialog()
    dialog.projectFilePath = "/tmp/basin.json"
    dialog.worker = SimpleNamespace(
        thread=SimpleNamespace(isRunning=lambda: True),
        kill=MagicMock(),
    )
    dialog.newProject = MagicMock()
    event = MagicMock()

    window.closeEvent(dialog, event)

    event.ignore.assert_called_once_with()
    event.accept.assert_not_called()
    dialog.newProject.assert_not_called()
    dialog.worker.kill.assert_not_called()


@pytest.mark.unit
def test_close_event_keeps_new_project_when_the_worker_is_idle() -> None:
    """With no running thread, close still uses ``newProject(supressed=True)``."""
    dialog = _dialog()
    dialog.projectFilePath = "/tmp/basin.json"
    dialog.worker = SimpleNamespace(
        thread=SimpleNamespace(isRunning=lambda: False),
        kill=MagicMock(),
    )
    seen: list[bool] = []

    def new_project(supressed=False):
        seen.append(supressed)

    dialog.newProject = new_project
    event = MagicMock()
    window.closeEvent(dialog, event)

    assert seen == [True]
    event.ignore.assert_called_once_with()
    event.accept.assert_not_called()
    dialog.worker.kill.assert_not_called()

    dialog.projectFilePath = "/tmp/basin.json"
    gui: list[str] = []
    dialog.initialGuiState = lambda: gui.append("reset")

    def clear_project(supressed=False):
        seen.append(supressed)
        dialog.projectFilePath = None

    dialog.newProject = clear_project
    event = MagicMock()
    window.closeEvent(dialog, event)
    assert seen == [True, True]
    assert gui == ["reset"]
    event.accept.assert_called_once_with()


@pytest.mark.unit
def test_reject_shares_close_guards_for_escape() -> None:
    """Escape must not dismiss the dialog while a model thread is running."""
    dialog = _dialog()
    dialog.projectFilePath = "/tmp/basin.json"
    dialog.worker = SimpleNamespace(
        thread=SimpleNamespace(isRunning=lambda: True),
    )
    dialog.newProject = MagicMock()
    with patch.object(window.QDialog, "reject") as qdialog_reject:
        window.reject(dialog)
    qdialog_reject.assert_not_called()
    dialog.newProject.assert_not_called()


@pytest.mark.unit
def test_dialog_class_binds_reject_for_escape() -> None:
    """``reject`` must be on the dialog class so Escape uses the guards."""
    source = (ROOT / "plugin" / "dialog" / "__init__.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    found = False
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "_window"
            and node.level == 1
        ):
            names = [alias.name for alias in node.names]
            assert "reject" in names
            assert "closeEvent" in names
            found = True
    assert found


@pytest.mark.unit
def test_run_long_task_disables_run_without_fake_cancel() -> None:
    """A run disables ``btn_Run`` and no longer wires a no-op Cancel handler."""
    dialog = _dialog()
    dialog.projectFilePath = "/tmp/basin.json"
    dialog.reportExecutionLog = MagicMock()
    dialog.handleFinished = MagicMock()

    class _Signal:
        def connect(self, *_args, **_kwargs):
            return None

    class _Worker:
        def __init__(self, path):
            self.path = path
            self.logUpdated = _Signal()
            self.errorUpdated = _Signal()
            self.runFinished = _Signal()
            self.thread = SimpleNamespace(finished=_Signal())

        def deleteLater(self):
            return None

        def run(self):
            return None

    with patch.object(worker, "RUBEMModelWorker", _Worker):
        worker.runLongTask(dialog)

    dialog.btn_Run.setEnabled.assert_called_with(False)
    dialog.btn_Cancel.clicked.connect.assert_not_called()


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
        except Exception:
            failed += 1
            traceback.print_exc()
            print("FAIL", name)
        else:
            print("ok", name)
    raise SystemExit(failed)
