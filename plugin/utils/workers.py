"""Background run of the RUBEM submodule.

The worker does not start an external program. It calls
:func:`plugin.engine.run_project`, which uses ``Model.run_isolated`` so
PCRaster's process-wide clone stays out of the QGIS process.
"""

from qgis.PyQt.QtCore import QObject, QThread, pyqtSignal

try:
    from ..engine import run_project
except ImportError:
    from engine import run_project


class RUBEMModelWorker(QObject):
    """Run one JSON project on a ``QThread`` and report through signals."""

    logUpdated = pyqtSignal(str)
    errorUpdated = pyqtSignal(str)
    runFinished = pyqtSignal(int)

    def __init__(self, config_path, runner=None):
        """Store the project path.

        :param config_path: JSON file the dialog just saved.
        :param runner: Callable used instead of :func:`run_project` in tests.
        """
        super().__init__()
        self._config_path = config_path
        self._runner = run_project if runner is None else runner
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self._execute)

    def run(self):
        """Start the thread. The call returns before the model finishes."""
        self._thread.start()

    def _execute(self):
        """Invoke the runner on the worker thread."""
        try:
            self.logUpdated.emit(str(self._runner(self._config_path)))
            self.runFinished.emit(0)
        except Exception as exc:
            self.errorUpdated.emit(str(exc))
            self.runFinished.emit(1)
        finally:
            self._thread.quit()

    def kill(self):
        """Report that an isolated run cannot be cancelled from this button.

        ``Model.run_isolated`` owns the subprocess. Terminating this thread
        would leave that process running without a parent to observe it.
        """
        self.errorUpdated.emit(
            "This run uses RUBEM's isolated process. The cancel button does not stop it."
        )

    @property
    def thread(self):
        """The thread ``run`` starts."""
        return self._thread
