import os


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


def closeEvent(self, event):
    """Ignore close while a model worker thread is running.

    The worker is not killed. Also ignore while a deferred Pydantic install
    is in progress, so New/Close cannot replace ``self.config`` before the
    retry writes the snapshot. Otherwise this still calls
    ``newProject(supressed=True)`` and accepts the close only when that
    leaves no project file.

    :param event: Dialog close event.
    :type event: QCloseEvent
    """
    if getattr(self, "_pydantic_installing", False):
        event.ignore()
        return

    worker = getattr(self, "worker", None)
    thread = getattr(worker, "thread", None) if worker is not None else None
    is_running = getattr(thread, "isRunning", None)
    if callable(is_running) and is_running():
        event.ignore()
        return

    self.newProject(supressed=True)

    if self.projectFilePath:
        event.ignore()
    else:
        self.initialGuiState()
        event.accept()
