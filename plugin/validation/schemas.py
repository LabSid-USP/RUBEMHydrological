# coding=utf-8
# RUBEM Hydrological is a QGIS plugin that assists in setup the RUBEM model:
# Copyright (C) 2021-2022 LabSid PHA EPUSP

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
    "SIM_TIME": {"start": "01/01/1900", "end": "01/02/1900"},
    "DIRECTORIES": {
        "input": "",
        "output": "",
        "etp": "",
        "prec": "",
        "ndvi": "",
        "Kp": "",
        "landuse": "",
    },
    "FILENAME_PREFIXES": {
        "etp_prefix": "",
        "prec_prefix": "",
        "ndvi_prefix": "",
        "kp_prefix": "",
        "landuse_prefix": "",
    },
    "RASTERS": {
        "dem": "",
        "demtif": "",
        "clone": "",
        "ndvi_max": "",
        "ndvi_min": "",
        "soil": "",
        "samples": "",
    },
    "TABLES": {
        "rainydays": "",
        "a_i": "",
        "a_o": "",
        "a_s": "",
        "a_v": "",
        "manning": "",
        "bulk_density": "",
        "K_sat": "",
        "T_fcap": "",
        "T_sat": "",
        "T_wp": "",
        "rootzone_depth": "",
        "K_c_min": "",
        "K_c_max": "",
    },
    "GRID": {"grid": "500.00"},
    "CALIBRATION": {
        "alpha": "4.500",
        "b": "0.500",
        "w_1": "0.333",
        "w_2": "0.333",
        "w_3": "0.334",
        "rcd": "5.000",
        "f": "0.500",
        "alpha_gw": "0.500",
        "x": "0.500",
    },
    "INITIAL_SOIL_CONDITIONS": {
        "T_ini": "1.000",
        "bfw_ini": "0.100",
        "bfw_lim": "1.000",
        "S_sat_ini": "1.000",
    },
    "CONSTANTS": {
        "fpar_max": "0.950",
        "fpar_min": "0.001",
        "lai_max": "12.000",
        "i_imp": "2.500",
    },
    "GENERATE_FILE": {
        "itp": "True",
        "bfw": "False",
        "srn": "False",
        "eta": "False",
        "lfw": "False",
        "rec": "False",
        "smc": "False",
        "rnf": "False",
        "tss": "False",
    },
    "RASTER_FILE_FORMAT": {"map_raster_series": "True", "tiff_raster_series": "True"},
}
