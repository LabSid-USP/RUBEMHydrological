import os

from qgis.core import Qgis, QgsMessageLog
from qgis.PyQt.QtWidgets import QMessageBox

try:
    from ..utils.workers import RUBEMStandaloneWorker
except ImportError:
    from utils.workers import RUBEMStandaloneWorker

def setRunState(self):
    """Invoke the model's standalone executable including the configuration file generated from user input as an argument in the CLI."""
    # Use the standalone executable file of the model present in the plugin's root directory
    self.modelFilePath = os.path.join(
        self.plugin_dir, os.pardir, os.pardir, "rubem", "rubem.exe")
    
    if self.modelFilePath is None or not os.path.isfile(self.modelFilePath):
        QgsMessageLog.logMessage(
            "Could not find the model's standalone executable file.", "RUBEM Hydrological", level=Qgis.Critical)
        raise FileNotFoundError("Could not find the model's standalone executable file.")

    if self.hasFilledAllFields():
        self.updateConfigFromGUI()
        self.saveProject(self.projectFilePath)

        # Make command list available to execution thread
        self.command = [self.modelFilePath, "--configfile", self.projectFilePath]

        # Output directory contains files, ask user before proceeding
        if os.listdir(self.config.get("DIRECTORIES", "output")):
            if self.getUserRetDirNotEmpty() != QMessageBox.Ok:
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
    if exit_code == 0:
        self.textBrowser_log.append("\n# RUBEM execution finished successfully!")
        self.tab_Results.setEnabled(True)
        self.populateMapSeriesTree()
        self.populateTimeSeriesTree()
        QgsMessageLog.logMessage("RUBEM execution finished successfully!", "RUBEM Hydrological", level=Qgis.Success)        
    else:
        self.textBrowser_log.append("\n# RUBEM execution finished with errors.")
        self.textBrowser_log.append("\n# Check the log for more details.")
        self.textBrowser_log.append("\n# If you need help, visit http://rubem-hydrological.rtfd.io/")
        QgsMessageLog.logMessage("RUBEM execution finished with errors.", "RUBEM Hydrological", level=Qgis.Critical)

def runLongTask(self):
    """Configure QProcess."""
    self.progressBar.setRange(0, 100)
    self.worker = RUBEMStandaloneWorker(self.command)
    self.worker.logUpdated.connect(self.reportExecutionLog)
    self.worker.errorUpdated.connect(self.reportExecutionLog)
    self.worker.finished.connect(self.worker.deleteLater)
    self.worker.progress.connect(self.reportProgress)   
    self.worker.finished.connect(lambda: self.btn_Run.setEnabled(True))
    self.btn_Cancel.clicked.connect(lambda: self.progressBar.setValue(0))
    self.btn_Cancel.clicked.connect(lambda: self.textBrowser_log.clear())
    self.btn_Cancel.clicked.connect(self.worker.kill)
    self.btn_Run.setEnabled(False)
    self.worker.run()