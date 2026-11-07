"""Time-series plotter unit tests with synthetic CSV input."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_plot_time_series_data_builds_figure(tmp_path: Path, monkeypatch) -> None:
    """``plotTimeSeriesData`` builds a figure from a small station CSV."""
    matplotlib = pytest.importorskip("matplotlib")
    pytest.importorskip("pandas")
    monkeypatch.setenv("MPLBACKEND", "Agg")
    monkeypatch.setattr(matplotlib, "use", lambda *args, **kwargs: None)

    csv_path = tmp_path / "station.csv"
    # Separator and row count must match the plotter's ``;`` + monthly range.
    csv_path.write_text("idx;s1\n0;1.0\n1;1.5\n", encoding="utf-8")

    import matplotlib.pyplot as plt

    monkeypatch.setattr(plt, "show", lambda *args, **kwargs: None)

    from plugin.report.plotter import plotTimeSeriesData

    plot_dict = {"title": "Test", "x_label": "Date", "y_label": "mm"}
    # Must not raise; QtAgg is forced off via monkeypatch above.
    plotTimeSeriesData(str(csv_path), plot_dict, "01/01/2020", "01/02/2020")
