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


# TODO: Add docstring information and comments
def closeEvent(self, event):

    self.newProject(supressed=True)

    if self.projectFilePath:
        event.ignore()
    else:
        self.initialGuiState()
        event.accept()
