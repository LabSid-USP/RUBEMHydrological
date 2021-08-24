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

"""RUBEM Hydrological plugin raster utilities code."""

__author__ = "LabSid PHA EPUSP"
__email__ = "rubem.hydrological@labsid.eng.br"
__copyright__ = "Copyright 2021, LabSid PHA EPUSP"
__license__ = "GPL"
__date__ = "2021-05-19"
__version__ = "1.3.2"

from osgeo import gdal

# TODO: Add docstring information and comments
def getValueFromRaster(rasterFile, x, y):

    gdal.AllRegister()
    # open the image
    ds = gdal.Open(rasterFile)

    if ds:
        # get image size
        rows = ds.RasterYSize
        cols = ds.RasterXSize
        bands = ds.RasterCount
        # get georeference info
        transform = ds.GetGeoTransform()
        xOrigin = transform[0]
        yOrigin = transform[3]
        pixelWidth = transform[1]
        pixelHeight = transform[5]

        xOffset = int((x - xOrigin) / pixelWidth)
        yOffset = int((y - yOrigin) / pixelHeight)

        band = ds.GetRasterBand(1)  # 1-based index
        data = band.ReadAsArray(xOffset, yOffset, 1, 1)
        return data[0][0]


# TODO: Add docstring information and comments
def getValuesFromRasterSeries(rasterFileList, x, y):
    values = []
    for rasterFile in rasterFileList:
        values.append(getValueFromRaster(rasterFile, x, y))
    return values


# TODO: Add docstring information and comments
def raster2vector(rasterFile):

    gdal.AllRegister()
    # open the image
    ds = gdal.Open(rasterFile)

    if ds:
        band = ds.GetRasterBand(1)  # 1-based index
        return band.ReadAsArray()
