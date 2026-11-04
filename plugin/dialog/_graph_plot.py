import os

from qgis.PyQt.QtCore import Qt, QModelIndex

try:
    from ..report.plotter import plotTimeSeriesData
except ImportError as _exc:
    # Only fall back to the bare name when the relative import itself is
    # unavailable (no parent package, or the local module is missing).
    # An ImportError for a third-party name (e.g. matplotlib) must keep
    # its own message instead of surfacing as a missing report module.
    if _exc.name is not None and not (
        _exc.name == "report" or _exc.name.endswith("report.plotter")
    ):
        raise
    from report.plotter import plotTimeSeriesData

try:
    from ._mappings import timeSeriesDict
except ImportError as _exc:
    if _exc.name is not None and not _exc.name.endswith("_mappings"):
        raise
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
