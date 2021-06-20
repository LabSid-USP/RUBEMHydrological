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