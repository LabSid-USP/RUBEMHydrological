import os

try:
    from qgis.PyQt.QtCore import QThread
    from qgis.PyQt.QtWidgets import QMessageBox
except ImportError:
    from PyQt5.QtCore import QThread
    from PyQt5.QtWidgets import QMessageBox

try:
    from ..utils.workers import RUBEMStandaloneWorker
except ImportError:
    from utils.workers import RUBEMStandaloneWorker

# TODO: Capture execution log fom RainfallRunoff.exe without freezing GUI
def setRunState(self):
    """Invoke the model's standalone executable including the configuration file generated from user input as an argument in the CLI."""
    # Use the standalone executable file of the model present in the plugin's root directory
    self.modelFilePath = os.path.join(
        self.plugin_dir, os.pardir, os.pardir, "rubem", "rubem.exe"
    )
    # raise Exception(self.modelFilePath)

    if self.hasFilledAllFields():
        self.updateConfigFromGUI()
        self.saveProject(self.projectFilePath)
        # self.showConfig()

        # Make command list available to execution thread
        self.command = [self.modelFilePath, "--configfile", self.projectFilePath]

        # Empty output directory
        if not os.listdir(self.config.get("DIRECTORIES", "output")):
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
