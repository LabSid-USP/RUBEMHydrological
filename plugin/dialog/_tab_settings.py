import os

try:
    from qgis.PyQt.QtWidgets import QMessageBox
except ImportError:
    from PyQt5.QtWidgets import QMessageBox

# Settings tab
# Project Folder
def setInputDirectoryPath(self, userInputDir=None):
    """Define the directory containing the project's input data.

    :Slot signal: clicked
    :Signal sender: toolButton_InputFolder
    """
    directoryPath = self.getDirectoryPath(caption="Select Input Directory")
    if directoryPath:
        self.config.set("DIRECTORIES", "input", directoryPath)
        self.lineEdit_InputFolder.setText(directoryPath)


def setOutputDirectoryPath(self):
    """Define the directory containing the project's output data.

    :Slot signal: clicked
    :Signal sender: toolButton_OutputFolder
    """
    directoryPath = self.getDirectoryPath(caption="Select Output Directory")
    if directoryPath:
        # Folder is empty
        if not os.listdir(directoryPath):
            self.config.set("DIRECTORIES", "output", directoryPath)
            self.lineEdit_OutputFolder.setText(directoryPath)
        else:
            response = self.getUserRetDirNotEmpty()
            if response == QMessageBox.Ok:
                self.config.set("DIRECTORIES", "output", directoryPath)
                self.lineEdit_OutputFolder.setText(directoryPath)


# Model General Settings
def setDEMFilePath(self):
    """Define the project's DEM map file.

    Also updates the lineEdt_Dem field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_Dem
    """
    filePath = self.getFilePath(caption="Select DEM map File", filter="*.map")
    if filePath:
        self.config.set("RASTERS", "dem", filePath)
        self.lineEdt_Dem.setText(filePath)


def setDEMTifFilePath(self):
    """Define the project's DEM TIFF file.

    Also updates the lineEdt_DemTif field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_DemTif
    """
    filePath = self.getFilePath(caption="Select DEM TIFF File", filter="*.tif")
    if filePath:
        self.config.set("RASTERS", "demtif", filePath)
        self.lineEdt_DemTif.setText(filePath)


def setCloneFilePath(self):
    """Define the project's Clone file.

    Also updates the lineEdt_Clone field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_Clone
    """
    filePath = self.getFilePath(caption="Select Clone File", filter="*.map")
    if filePath:
        self.config.set("RASTERS", "clone", filePath)
        self.lineEdt_Clone.setText(filePath)


def setExportSampleLocations(self):
    """Define as enabled the fields related to the Sample file.

    Fields: lineEdt_Sample, btn_Sample and label_SelectSample.

    :Slot signal: checked
    :Signal sender: checkBox_Sample
    """
    self.config.set("GENERATE_FILE", "tss", str(self.checkBox_Sample.isChecked()))

    if self.checkBox_Sample.isChecked():
        self.lineEdt_Sample.setEnabled(True)
        self.btn_Sample.setEnabled(True)
        self.label_SelectSample.setEnabled(True)
    else:
        self.lineEdt_Sample.clear()
        self.lineEdt_Sample.setEnabled(False)
        self.btn_Sample.setEnabled(False)
        self.label_SelectSample.setEnabled(False)


def setSampleFilePath(self):
    """Define the project's Sample file.

    Also updates the lineEdt_Sample field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_Sample
    """
    filePath = self.getFilePath(caption="Select Sample Stations File", filter="*.map")
    if filePath:
        self.config.set("RASTERS", "samples", filePath)
        self.lineEdt_Sample.setText(filePath)


def setGridSize(self):
    """Define the project's Grid size.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_GridSize
    """
    self.config.set("GRID", "grid", str(self.doubleSpinBox_GridSize.value()))


# Simulation Period
def setStartSimulationPeriod(self):
    """Define the start date of the model simulation period.

    Follows the format 'dd/MM/yyyy'.

    :Slot signal: editingFinished
    :Signal sender: dtEdt_StartSim
    """
    self.config.set(
        "SIM_TIME", "start", self.dtEdt_StartSim.date().toString("dd/MM/yyyy")
    )


def setEndSimulationPeriod(self):
    """Define the end date of the model simulation period.

    Follows the format 'dd/MM/yyyy'.

    :Slot signal: editingFinished
    :Signal sender: dtEdt_EndSim
    """
    self.config.set("SIM_TIME", "end", self.dtEdt_EndSim.date().toString("dd/MM/yyyy"))
