import os

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsLayerTreeLayer,
    QgsProject,
    QgsRasterLayer,
)
from qgis.PyQt.QtCore import QModelIndex, Qt

try:
    from ._project import resolve_project_path
except ImportError:
    from _project import resolve_project_path


# TODO: Add docstring information and comments
def canvasHandler(self, index: QModelIndex):
    if index.flags() & Qt.ItemFlag.ItemIsSelectable:
        output = resolve_project_path(self, self.config.get("DIRECTORIES", "output"))
        rasterPath = os.path.join(output, index.data())
        legend = index.data()
        rlayer = QgsRasterLayer(rasterPath, legend)
        rlayer.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        if not rlayer.isValid():
            # TODO: Move this message to plugin message bar
            self.iface.messageBar().pushMessage(
                "Error", "Layer failed to load!", level=Qgis.Critical
            )
        elif QgsProject.instance().mapLayersByName(legend):
            # TODO: Move this message to plugin message bar
            self.iface.messageBar().pushMessage(
                "Error",
                "This raster has already been added to the current project in QGIS.",
                level=Qgis.Critical,
            )
        else:
            QgsProject.instance().addMapLayer(rlayer, False)
            layerTree = self.iface.layerTreeCanvasBridge().rootGroup()
            layerTree.insertChildNode(-1, QgsLayerTreeLayer(rlayer))


# TODO: Add docstring information and comments
#! Obsolete and/or used for testing method only
def displayPoint(self, pointTool):
    output = resolve_project_path(self, self.config.get("DIRECTORIES", "output"))
    value = self.getValue(
        os.path.join(output, self.iface.activeLayer().name()),
        pointTool[0],
        pointTool[1],
    )
    self.textBrowser_log.append(f"{pointTool[0]}, {pointTool[1]} => {value}")
