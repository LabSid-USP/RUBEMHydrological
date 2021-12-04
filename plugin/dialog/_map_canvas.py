import os

from qgis.core import (
    Qgis,
    QgsProject,
    QgsRasterLayer,
    QgsLayerTreeLayer,
    QgsCoordinateReferenceSystem,
)

try:
    from qgis.PyQt.QtCore import Qt, QModelIndex
except ImportError:
    from PyQt5.QtCore import Qt, QModelIndex

# TODO: Add docstring information and comments
def canvasHandler(self, index: QModelIndex):
    if index.flags() & Qt.ItemIsSelectable:
        rasterPath = os.path.join(
            self.config.get("DIRECTORIES", "output"), index.data()
        )
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
    value = self.getValue(
        os.path.join(
            self.config.get("DIRECTORIES", "output"),
            self.iface.activeLayer().name(),
        ),
        pointTool[0],
        pointTool[1],
    )
    self.textBrowser_log.append(f"{pointTool[0]}, {pointTool[1]} => {value}")
