import os
from textwrap import dedent

from qgis.core import Qgis, QgsMessageLog
from qgis.PyQt.QtWidgets import QMessageBox

try:
    from ..engine import assert_ready
    from ..utils.workers import RUBEMModelWorker
except ImportError:
    from engine import assert_ready
    from utils.workers import RUBEMModelWorker


def setRunState(self):
    """Run the saved JSON project through the RUBEM submodule."""
    try:
        assert_ready()
    except (FileNotFoundError, RuntimeError, ImportError) as exc:
        self.textBrowser_log.append(f"\n# {exc}")
        QgsMessageLog.logMessage(str(exc), "RUBEM Hydrological", level=Qgis.Critical)
        return

    if self.hasFilledAllFields():
        self.updateConfigFromGUI()
        self.saveProject(self.projectFilePath)

        # Output directory contains files, ask user before proceeding
        if os.listdir(self.config.get("DIRECTORIES", "output")):
            if self.getUserRetDirNotEmpty() != QMessageBox.StandardButton.Ok:
                return

        self.textBrowser_log.append("\n# RUBEM execution started...")
        self.runLongTask()


def reportExecutionLog(self, outputLog):
    """Update textBrowser_log with output captured from execution."""
    self.textBrowser_log.append(outputLog)


def reportProgress(self, n):
    """Update progressBar with int representing overall progress of exec\n
    thread.

    :Slot signal: emit(int)
    :Signal sender: pyqtSignal(int)
    """
    self.progressBar.setValue(n)


def handleFinished(self, exit_code):
    """Handle the exit code of the execution thread."""
    self.progressBar.setRange(0, 100)
    self.progressBar.setValue(100 if exit_code == 0 else 0)
    if exit_code == 0:
        self.textBrowser_log.append("\n# RUBEM execution finished successfully!")
        self.tab_Results.setEnabled(True)
        self.populateMapSeriesTree()
        self.populateTimeSeriesTree()
        QgsMessageLog.logMessage(
            "RUBEM execution finished successfully!",
            "RUBEM Hydrological",
            level=Qgis.Success,
        )
    else:
        self.textBrowser_log.append(dedent("""\n
            # RUBEM execution finished with errors!
            # Check the log for more details.
            # If you need help, visit http://rubem-hydrological.rtfd.io/"""))
        self.progressBar.setStyleSheet(
            "QProgressBar::chunk " "{" "background-color: red;" "}"
        )
        QgsMessageLog.logMessage(
            "RUBEM execution finished with errors.",
            "RUBEM Hydrological",
            level=Qgis.Critical,
        )


def explainCancel(self):
    """Tell the user, on the GUI thread, that this run is not cancellable."""
    self.textBrowser_log.append(
        "\n# This run cannot be cancelled. RUBEM finishes in its own process."
    )


def runLongTask(self):
    """Start the submodule run and leave the progress bar indeterminate."""
    self.progressBar.setStyleSheet("")
    self.progressBar.setRange(0, 0)
    self.worker = RUBEMModelWorker(self.projectFilePath)
    self.worker.logUpdated.connect(self.reportExecutionLog)
    self.worker.errorUpdated.connect(self.reportExecutionLog)
    self.worker.runFinished.connect(self.handleFinished)
    self.worker.runFinished.connect(lambda: self.btn_Run.setEnabled(True))
    self.worker.thread.finished.connect(self.worker.deleteLater)
    if not getattr(self, "_cancel_explained", False):
        self.btn_Cancel.clicked.connect(self.explainCancel)
        self._cancel_explained = True
    self.btn_Run.setEnabled(False)
    self.worker.run()
