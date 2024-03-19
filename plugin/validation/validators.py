# coding=utf-8
# RUBEM Hydrological is a QGIS plugin that assists in setup the RUBEM model:
# Copyright (C) 2021-2024 LabSid PHA EPUSP

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

"""RUBEM Hydrological plugin user input validation code."""

from os.path import isdir, isfile

try:
    from qgis.PyQt.QtGui import QValidator
except ImportError:
    from PyQt5.QtGui import QValidator

DEFAULT_STYLESHEET = ""

INVALID_LINEEDIT_STYLESHEET = "border: 1px solid red; color: red;"
# ACCEPTABLE_LINEEDIT_STYLESHEET = "border: 1px solid green; color: green;"
ACCEPTABLE_LINEEDIT_STYLESHEET = DEFAULT_STYLESHEET
# INTERMEDIATE_LINEEDIT_STYLESHEET = "border: 1px solid gold; color: gold;"
INTERMEDIATE_LINEEDIT_STYLESHEET = INVALID_LINEEDIT_STYLESHEET

INVALID_LABEL_STYLESHEET = "color: red;"
# ACCEPTABLE_LABEL_STYLESHEET = "color: green;"
ACCEPTABLE_LABEL_STYLESHEET = DEFAULT_STYLESHEET
# INTERMEDIATE_LABEL_STYLESHEET = "color: gold;"
INTERMEDIATE_LABEL_STYLESHEET = INVALID_LABEL_STYLESHEET


class DirectoryPathValidator(QValidator):
    def __init__(self, parent=None, parentLabel=None):
        self.lineEdit = parent
        self.label = parentLabel
        super().__init__()

    def validate(self, input: str, pos: int):

        if not input:
            self.lineEdit.setStyleSheet(ACCEPTABLE_LINEEDIT_STYLESHEET)
            return QValidator.Acceptable, input, pos
        # elif not exists(input):
        #     self.lineEdit.setStyleSheet(INVALID_STYLESHEET)
        #     return QValidator.Invalid, input, pos
        elif isfile(input):
            self.lineEdit.setStyleSheet(INTERMEDIATE_LINEEDIT_STYLESHEET)
            return QValidator.Intermediate, input, pos
        elif isdir(input):
            self.lineEdit.setStyleSheet(ACCEPTABLE_LINEEDIT_STYLESHEET)
            return QValidator.Acceptable, input, pos
        elif input:
            self.lineEdit.setStyleSheet(INTERMEDIATE_LINEEDIT_STYLESHEET)
            return QValidator.Intermediate, input, pos
        else:
            self.lineEdit.setStyleSheet(INVALID_LINEEDIT_STYLESHEET)
            return QValidator.Invalid, input, pos


class FilePathValidator(QValidator):
    def __init__(self, parent=None, parentLabel=None, parentExtension=None):
        self.lineEdit = parent
        self.label = parentLabel
        self.extension = parentExtension
        super().__init__()

    def validate(self, input: str, pos: int):

        if not input:
            self.lineEdit.setStyleSheet(ACCEPTABLE_LINEEDIT_STYLESHEET)
            self.label.setStyleSheet(ACCEPTABLE_LABEL_STYLESHEET)
            return QValidator.Acceptable, input, pos
        # elif not exists(input):
        #     self.lineEdit.setStyleSheet(INVALID_STYLESHEET)
        #     return QValidator.Invalid, input, pos
        elif isfile(input) and input.lower().endswith(self.extension):
            self.lineEdit.setStyleSheet(ACCEPTABLE_LINEEDIT_STYLESHEET)
            self.label.setStyleSheet(ACCEPTABLE_LABEL_STYLESHEET)
            return QValidator.Intermediate, input, pos
        elif isdir(input):
            self.lineEdit.setStyleSheet(INTERMEDIATE_LINEEDIT_STYLESHEET)
            self.label.setStyleSheet(INTERMEDIATE_LABEL_STYLESHEET)
            return QValidator.Acceptable, input, pos
        elif input:
            self.lineEdit.setStyleSheet(INTERMEDIATE_LINEEDIT_STYLESHEET)
            self.label.setStyleSheet(INTERMEDIATE_LABEL_STYLESHEET)
            return QValidator.Intermediate, input, pos
        else:
            self.lineEdit.setStyleSheet(INVALID_LINEEDIT_STYLESHEET)
            self.label.setStyleSheet(INVALID_LABEL_STYLESHEET)
            return QValidator.Invalid, input, pos
