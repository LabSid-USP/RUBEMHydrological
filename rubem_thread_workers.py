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

"""RUBEM Hydrological plugin thread workers code."""

from subprocess import PIPE, Popen, TimeoutExpired

try:
    from qgis.PyQt.QtCore import QObject, pyqtSignal
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSignal

# Create RUBEM standalone worker class


class RUBEMStandaloneWorker(QObject):
    """[summary].

    :param QObject: [description]
    :type QObject: [type]
    """

    def __init__(self, command):
        """[summary].

        :param command: [description]
        :type command: [type]
        """
        QObject.__init__(self)
        self.command = command
        self.killed = False
        self.process = None

    def run(self):
        """[summary]."""
        self.process = Popen(
            self.command, shell=True, encoding="latin-1", stdout=PIPE, stderr=PIPE
        )
        try:
            outs, errs = self.process.communicate(timeout=150)
        except TimeoutExpired:
            self.killed = True
            self.process.kill()
            outs, errs = self.process.communicate()

        self.progress.emit(100)
        self.finished.emit(outs + errs)

    def kill(self):
        """[summary]."""
        self.killed = True
        self.process.kill()

    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
