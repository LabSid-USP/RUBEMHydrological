import os
from pathlib import Path

try:
    from qgis.PyQt.QtCore import QUrl
    from qgis.PyQt.QtWidgets import QMessageBox
    from qgis.PyQt.QtGui import QDesktopServices
except:
    from PyQt5.QtCore import QUrl
    from PyQt5.QtWidgets import QMessageBox
    from PyQt5.QtGui import QDesktopServices


# TODO: Add docstring information and comments
def helpHandler(self):
    QDesktopServices.openUrl(QUrl("https://rubem-hydrological.readthedocs.io/"))


# TODO: Add docstring information and comments
def aboutHandler(self):
    helpAboutPath = os.path.join(Path(__file__).resolve().parents[2], "doc/about.html")
    with open(helpAboutPath, "r") as aboutContent:
        QMessageBox.about(self, "About RUBEM Hydrological", aboutContent.read())
