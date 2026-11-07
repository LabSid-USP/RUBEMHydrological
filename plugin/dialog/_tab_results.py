import os
from glob import glob

try:
    from ..report.item import StandardItem
    from ._mappings import mapSeriesDictFileNames, timeSeriesDictFileNames
    from ._project import resolve_project_path
except ImportError:
    from _mappings import mapSeriesDictFileNames, timeSeriesDictFileNames
    from _project import resolve_project_path
    from report.item import StandardItem


# TODO: Add docstring information and comments
def populateMapSeriesTree(self):
    self.mapSeriesTreeModel.clear()
    mapSeriesRootNode = self.mapSeriesTreeModel.invisibleRootItem()
    output = resolve_project_path(self, self.config.get("DIRECTORIES", "output"))
    for key, fileName in mapSeriesDictFileNames.items():
        tmpOutMapFileList = glob(os.path.join(output, fileName) + "*.[0-9]*")
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
    output = resolve_project_path(self, self.config.get("DIRECTORIES", "output"))
    for key, fileName in timeSeriesDictFileNames.items():
        tmpTimeSeriesFile = os.path.join(output, fileName) + ".csv"
        if os.path.exists(tmpTimeSeriesFile):
            tmpOutTimeSeries = StandardItem(key)
            tmpOutTimeSeries.setSelectable(False)
            tmpOutTimeSeries.appendRow(StandardItem(tmpTimeSeriesFile, isPath=True))
            timeSeriesRootNode.appendRow(tmpOutTimeSeries)
            self.treeView_TimeSeriesData.setModel(self.timeSeriesTreeModel)
