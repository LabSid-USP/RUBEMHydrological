import os

from qgis.PyQt.QtCore import QModelIndex, Qt

try:
    from ..report.plotter import plotTimeSeriesData
except ImportError as _exc:
    # Only fall back to the bare name when the relative import itself is
    # unavailable (no parent package, or the local module is missing).
    # An ImportError for a third-party name (e.g. matplotlib) must keep
    # its own message instead of surfacing as a missing report module.
    if _exc.name is None or not (
        _exc.name == "report" or _exc.name.endswith("report.plotter")
    ):
        raise
    from report.plotter import plotTimeSeriesData

try:
    from ._mappings import timeSeriesDict
    from ._project import resolve_project_path
except ImportError:
    from _mappings import timeSeriesDict
    from _project import resolve_project_path


# TODO: Add docstring information and comments
def plotWrapper(self, index: QModelIndex):
    if index.flags() & Qt.ItemFlag.ItemIsSelectable:
        key = os.path.splitext(index.data())[0]
        plot_meta = timeSeriesDict.get(key)
        if plot_meta is None:
            return
        output = resolve_project_path(self, self.config.get("DIRECTORIES", "output"))
        plotTimeSeriesData(
            os.path.join(output, index.data()),
            plot_meta.get("plot"),
            self.config.get("SIM_TIME", "start"),
            self.config.get("SIM_TIME", "end"),
        )
