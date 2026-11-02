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

"""RUBEM Hydrological plugin thread workers code."""

from qgis.PyQt.QtCore import QObject, QProcess, QProcessEnvironment, pyqtSignal

try:
    from ..engine import child_environment
except ImportError:
    from engine import child_environment


class RUBEMStandaloneWorker(QObject):
    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)

    def run(self):
        environment = QProcessEnvironment()
        for key, value in child_environment().items():
            environment.insert(key, value)
        self.process.setProcessEnvironment(environment)
        self.process.start(self.command[0], self.command[1:])

    def handle_stdout(self):
        while self.process.canReadLine():
            data = self.process.readLine().data().decode().strip()

            if data:
                self.logUpdated.emit(data)

                if "##" in data:
                    parts = data.split(" ")
                    try:
                        current_cycle = int(parts[-3])
                        total_cycles = int(parts[-1])
                    except (ValueError, IndexError):
                        continue
                    if total_cycles:
                        self.progress.emit(int((current_cycle / total_cycles) * 100))

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode().strip()
        if data:
            self.errorUpdated.emit(data)

    def handle_finished(self, exit_code, exit_status):
        """Emit ``0`` only when the process exits normally with code zero."""
        normal = exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0
        self.finished.emit(0 if normal else exit_code or 1)

    def kill(self):
        self.process.kill()

    logUpdated = pyqtSignal(str)
    errorUpdated = pyqtSignal(str)
    finished = pyqtSignal(int)
    progress = pyqtSignal(int)
