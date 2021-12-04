import os
from glob import glob

try:
    from qgis.PyQt.QtCore import Qt, QModelIndex
except ImportError:
    from PyQt5.QtCore import Qt, QModelIndex

try:
    from ..report.item import StandardItem
    from ._mappings import mapSeriesDictFileNames, timeSeriesDictFileNames
except ImportError:
    from report.item import StandardItem
    from _mappings import mapSeriesDictFileNames, timeSeriesDictFileNames


# TODO: Add docstring information and comments
def populateMapSeriesTree(self):
    self.mapSeriesTreeModel.clear()
    mapSeriesRootNode = self.mapSeriesTreeModel.invisibleRootItem()
    for key, fileName in mapSeriesDictFileNames.items():
        tmpOutMapFileList = glob(
            os.path.join(self.config.get("DIRECTORIES", "output") + fileName)
            + "*.[0-9]*"
        )
        if tmpOutMapFileList:
            tmpOutMapSeries = StandardItem(key)
            tmpOutMapSeries.setSelectable(False)
            tmpOutMapSeries.appendRows(
                [StandardItem(item, isPath=True) for item in tmpOutMapFileList]
            )
            mapSeriesRootNode.appendRow(tmpOutMapSeries)
            self.treeView_MapSeriesData.setModel(self.mapSeriesTreeModel)


# TODO: Add docstring information and comments
def populateTimeSeriesTree(self):
    self.timeSeriesTreeModel.clear()
    timeSeriesRootNode = self.timeSeriesTreeModel.invisibleRootItem()
    for key, fileName in timeSeriesDictFileNames.items():
        tmpTimeSeriesFile = (
            os.path.join(self.config.get("DIRECTORIES", "output") + fileName) + ".csv"
        )
        if os.path.exists(tmpTimeSeriesFile):
            tmpOutTimeSeries = StandardItem(key)
            tmpOutTimeSeries.setSelectable(False)
            tmpOutTimeSeries.appendRow(StandardItem(tmpTimeSeriesFile, isPath=True))
            timeSeriesRootNode.appendRow(tmpOutTimeSeries)
            self.treeView_TimeSeriesData.setModel(self.timeSeriesTreeModel)
