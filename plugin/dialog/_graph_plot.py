import os

from qgis.PyQt.QtCore import Qt, QModelIndex

try:
    from ..report.plotter import plotTimeSeriesData
    from ._mappings import timeSeriesDict
except ImportError:
    from report.plotter import plotTimeSeriesData
    from _mappings import timeSeriesDict

# TODO: Add docstring information and comments
def plotWrapper(self, index: QModelIndex):
    if index.flags() & Qt.ItemFlag.ItemIsSelectable:
        key = os.path.splitext(index.data())[0]
        plotTimeSeriesData(
            os.path.join(self.config.get("DIRECTORIES", "output"), index.data()),
            timeSeriesDict.get(key).get("plot"),
            self.config.get("SIM_TIME", "start"),
            self.config.get("SIM_TIME", "end"),
        )
