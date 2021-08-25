# coding=utf-8
# RUBEM Hydrological is a QGIS plugin that assists in setup the RUBEM model:
# Copyright (C) 2021 LabSid PHA EPUSP

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact: rubem.hydrological@labsid.eng.br

"""RUBEM Hydrological plugin graph plot code."""

__author__ = "LabSid PHA EPUSP"
__email__ = "rubem.hydrological@labsid.eng.br"
__copyright__ = "Copyright 2021, LabSid PHA EPUSP"
__license__ = "GPL"
__date__ = "2021-05-19"
__version__ = "1.3.2"

import matplotlib.pyplot as plt
from cycler import cycler
import pandas as pd
import datetime

font = {"weight": "normal", "size": 16}

color_cycle = cycler(c=["r", "g", "b", "c", "k"])
ls_cycle = cycler(ls=["-", "--", "-.", ":", "-"])
lw_cycle = cycler(lw=[1, 2, 1, 2, 1])
# mk_cycle = cycler(marker=['.', ',', 'o', 'v','^'])
sty_cycle = ls_cycle + color_cycle + lw_cycle

# TODO: Add docstring information and comments
def plotTimeSeriesData(sourceFile, plotDict, startDate, endDate):

    df = pd.read_csv(sourceFile, index_col=0)

    dateList = pd.date_range(
        datetime.datetime.strptime(startDate, "%d/%m/%Y"),
        datetime.datetime.strptime(endDate, "%d/%m/%Y"),
        freq="MS",
    ).to_pydatetime()[:-1]
    df["Dates"] = dateList
    df.set_index("Dates")

    fig = plt.figure()
    windowTitle = str(plotDict.get("title")) + " — RUBEM Hydrological"
    fig.canvas.manager.set_window_title(windowTitle)

    ax = fig.add_subplot(111)
    ax.set_prop_cycle(sty_cycle)

    for col in df.columns.difference(["Dates"]):
        ax.plot(df["Dates"], df[col], label=col)

    ax.xaxis.set_tick_params(which="major", size=10, width=2, direction="in", top="on")
    ax.xaxis.set_tick_params(which="minor", size=7, width=2, direction="in", top="on")
    ax.yaxis.set_tick_params(
        which="major", size=10, width=2, direction="in", right="on"
    )
    ax.yaxis.set_tick_params(which="minor", size=7, width=2, direction="in", right="on")
    plt.xticks(rotation=45)
    plt.grid(True, which="both")

    plt.title(plotDict.get("title"), fontdict=font)
    ax.set_xlabel(plotDict.get("x_label"), fontsize=12, labelpad=10)
    ax.set_ylabel(plotDict.get("y_label"), fontsize=12, labelpad=10)
    plt.legend(title="Station ID")

    plt.tight_layout()
    plt.show()
