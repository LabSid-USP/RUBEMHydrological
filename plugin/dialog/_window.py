import os

from qgis.PyQt.QtWidgets import QDialog


# TODO: docstring
def updateWindowTitle(self, projectTitle=None):
    if not projectTitle:
        _, file = os.path.split(self.projectFilePath)
        projectName, _ = os.path.splitext(file)
        self.setWindowTitle(projectName + " — RUBEM Hydrological")
    else:
        self.setWindowTitle(projectTitle + " — RUBEM Hydrological")


# TODO: Add docstring information and comments
def initialGuiState(self):
    self.pushButton_SaveProject.setDisabled(True)
    self.pushButton_SaveAsProject.setDisabled(True)
    self.tabWidget.setDisabled(True)
    self.tabWidget.setCurrentIndex(0)
    self.tab_Results.setDisabled(True)
    # Run lives on the dialog-level button box, outside tabWidget, so the
    # tab disable no longer gates it — disable explicitly until a project
    # is open or created.
    if getattr(self, "btn_Run", None) is not None:
        self.btn_Run.setEnabled(False)


def _may_leave_dialog(self) -> bool:
    """Shared leave path for window close and Escape (``reject``).

    Returns True only when the dialog may dismiss. While a deferred
    Pydantic install or model worker is active, or when
    ``newProject(supressed=True)`` leaves a project file path (user
    cancelled saving), the dialog must stay open.
    """
    if getattr(self, "_pydantic_installing", False):
        self.textBrowser_log.append(
            "Wait for the dependency installation to finish before closing."
        )
        return False

    worker = getattr(self, "worker", None)
    thread = getattr(worker, "thread", None) if worker is not None else None
    is_running = getattr(thread, "isRunning", None)
    if callable(is_running) and is_running():
        self.textBrowser_log.append(
            "The model is still running. Closing is disabled until it finishes; "
            "Close does not stop the isolated process."
        )
        return False

    self.newProject(supressed=True)
    if self.projectFilePath:
        return False
    self.initialGuiState()
    return True


def closeEvent(self, event):
    """Ignore close while a model worker thread is running.

    The worker is not killed. Also ignore while a deferred Pydantic install
    is in progress, so New/Close cannot replace ``self.config`` before the
    retry writes the snapshot. Otherwise this still calls
    ``newProject(supressed=True)`` and accepts the close only when that
    leaves no project file. Escape uses :meth:`reject`, which shares
    :func:`_may_leave_dialog`.

    :param event: Dialog close event.
    :type event: QCloseEvent
    """
    if _may_leave_dialog(self):
        event.accept()
    else:
        event.ignore()


def reject(self):
    """Honor the same guards as :meth:`closeEvent` when Escape is pressed.

    QDialog maps Escape to ``reject()`` rather than ``closeEvent``.
    Without this override the installation, run-state, and unsaved-project
    checks would be skipped.
    """
    if _may_leave_dialog(self):
        QDialog.reject(self)
