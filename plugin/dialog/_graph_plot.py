import os

try:
    from qgis.PyQt.QtCore import Qt, QModelIndex
except ImportError:
    from PyQt5.QtCore import Qt, QModelIndex

try:
    from ..report.plotter import plotTimeSeriesData
    from ._mappings import timeSeriesDict
except ImportError:
    from ..report.plotter import plotTimeSeriesData

# TODO: Add docstring information and comments
def plotWrapper(self, index: QModelIndex):
    if index.flags() & Qt.ItemIsSelectable:
        key = os.path.splitext(index.data())[0]
        plotTimeSeriesData(
            os.path.join(self.config.get("DIRECTORIES", "output"), index.data()),
            timeSeriesDict.get(key).get("plot"),
            self.config.get("SIM_TIME", "start"),
            self.config.get("SIM_TIME", "end"),
        )
