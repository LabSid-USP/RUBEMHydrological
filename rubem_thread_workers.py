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

"""
/***************************************************************************
 **RUBEM Hydrological
                A Rainfall rUnoff Balance Enhanced Model wizard
 **Description
                             -------------------
        begin                : **2021
        copyright            : **Laboratório de Sistemas de Suporte a 
                             :   Decisões Aplicados à Engenharia Ambiental e 
                             :   de Recursos Hídricos (LabSid) PHA-EPUSP
        email                : **rubem.hydrological@labsid.eng.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   any later version.                                                    *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'LabSid PHA EPUSP'
__email__ = "rubem.hydrological@labsid.eng.br"
__copyright__ = 'Copyright 2021, LabSid PHA EPUSP'
__license__ = "GPL"
__date__ = '2021-05-19'
__version__ = "1.3.2"

from subprocess import Popen, TimeoutExpired, PIPE

try:
    from qgis.PyQt.QtCore import QObject, pyqtSignal
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSignal

# Create RUBEM standalone worker class
class RUBEMStandaloneWorker(QObject):
    """[summary]

    :param QObject: [description]
    :type QObject: [type]
    """
    def __init__(self, command):
        """[summary]

        :param command: [description]
        :type command: [type]
        """
        QObject.__init__(self)
        self.command = command
        self.killed = False
        self.process = None

    def run(self):
        """RUBEM Long-running task
        """
        self.process = Popen(self.command, shell=True, encoding='latin-1', stdout=PIPE, stderr=PIPE)
        try:
            #TODO: Verificar se o processo parou de responder, mas nao matar se ainda estiver funcionando
            outs, errs = self.process.communicate(timeout=150)
        except TimeoutExpired:
            self.killed = True
            self.process.kill()
            outs, errs = self.process.communicate()  
        
        self.progress.emit(100)
        self.finished.emit(outs + errs)

    def kill(self):
        """[summary]
        """
        self.killed = True
        self.process.kill()

    finished = pyqtSignal(str)
    progress = pyqtSignal(int)        