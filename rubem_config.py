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

"""RUBEM Hydrological plugin settings schemas."""

defaultConfigSchema = {
    "SIM_TIME": {"start": "01/01/2000", "end": "01/02/2000"},
    "FILES": {
        "input": "",
        "output": "",
        "dem": "",
        "demtif": "",
        "clone": "",
        "etp": "",
        "prec": "",
        "ndvi": "",
        "ndvimax": "",
        "ndvimin": "",
        "kp": "",
        "landuse": "",
        "solo": "",
        "samples": "",
        "etpFilePrefix": "",
        "precFilePrefix": "",
        "ndviFilePrefix": "",
        "kpFilePrefix": "",
        "landuseFilePrefix": "",
    },
    "PARAMETERS": {
        "rainydays": "",
        "a_i": "",
        "a_o": "",
        "a_s": "",
        "a_v": "",
        "manning": "",
        "dg": "",
        "kr": "",
        "capCampo": "",
        "saturacao": "",
        "pontomurcha": "",
        "zr": "",
        "kcmin": "",
        "kcmax": "",
    },
    "GRID": {"grid": "500.00"},
    "CALIBRATION": {
        "alfa": "4.500",
        "b": "0.500",
        "w1": "0.333",
        "w2": "0.333",
        "w3": "0.334",
        "rcd": "5.000",
        "f": "0.500",
        "alfa_gw": "0.500",
        "x": "0.500",
    },
    "INITIAL SOIL CONDITIONS": {
        "ftur_ini": "1.000",
        "eb_ini": "0.100",
        "eb_lim": "1.000",
        "tus_ini": "1.000",
    },
    "CONSTANT": {
        "fpar_max": "0.950",
        "fpar_min": "0.001",
        "lai_max": "12.000",
        "i_imp": "2.500",
    },
    "GENERATE_FILE": {
        "Int": "True",
        "bflow": "False",
        "sfrun": "False",
        "etp": "False",
        "Lf": "False",
        "Rec": "False",
        "ssat": "False",
        "runoff": "False",
        "auxQtot": "False",
        "auxRec": "False",
        "genTss": "False",
    },
    "GENERATE_FILE_FORMAT": {"enableMapSeries": "True", "enableTiff": "True"},
}

maxValuesDic = {
    "GRID": {"grid": "500.00"},
    "CALIBRATION": {
        "alfa": "4.500",
        "b": "0.500",
        "w1": "0.333",
        "w2": "0.333",
        "w3": "0.334",
        "rcd": "5.000",
        "f": "0.500",
        "alfa_gw": "0.500",
        "x": "0.500",
    },
    "INITIAL SOIL CONDITIONS": {
        "ftur_ini": "1.000",
        "eb_ini": "0.100",
        "eb_lim": "1.000",
        "tus_ini": "1.000",
    },
    "CONSTANT": {
        "fpar_max": "0.950",
        "fpar_min": "0.001",
        "lai_max": "12.000",
        "i_imp": "2.500",
    },
}

minValuesDic = {
    "GRID": {"grid": "500.00"},
    "CALIBRATION": {
        "alfa": "4.500",
        "b": "0.500",
        "w1": "0.333",
        "w2": "0.333",
        "w3": "0.334",
        "rcd": "5.000",
        "f": "0.500",
        "alfa_gw": "0.500",
        "x": "0.500",
    },
    "INITIAL SOIL CONDITIONS": {
        "ftur_ini": "1.000",
        "eb_ini": "0.100",
        "eb_lim": "1.000",
        "tus_ini": "1.000",
    },
    "CONSTANT": {
        "fpar_max": "0.950",
        "fpar_min": "0.001",
        "lai_max": "12.000",
        "i_imp": "2.500",
    },
}
