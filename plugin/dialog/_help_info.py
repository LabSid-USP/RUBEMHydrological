import os
from pathlib import Path

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QMessageBox


# TODO: Add docstring information and comments
def helpHandler(self):
    QDesktopServices.openUrl(QUrl("https://rubem-hydrological.readthedocs.io/"))


# TODO: Add docstring information and comments
def aboutHandler(self):
    helpAboutPath = os.path.join(Path(__file__).resolve().parents[2], "doc/about.html")
    with open(helpAboutPath) as aboutContent:
        QMessageBox.about(self, "About RUBEM Hydrological", aboutContent.read())
