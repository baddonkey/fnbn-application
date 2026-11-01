from PySide6.QtCore import Property, QObject, QThread, Signal, Slot
import time

from fnbn_backend.backend import Backend

class SuggestTaskWorker(QThread):

    progressChanged = Signal(int)

    def __init__(self, backend: Backend, rows, parent=None):
        super().__init__(parent)
        self.error = None
        self.cancelled = False
        self._backend = backend
        self._rows = rows

    def run(self):

        try:
            total_steps = len(self._rows)

            i = 0

            for row in sorted({int(row) for row in self._rows}):
                self._backend.suggestFilename(row)

                if self.isInterruptionRequested():
                    self.cancelled = True
                    return

                progress = int((i + 1) / total_steps * 100)
                i = i + 1

                self.progressChanged.emit(progress)
        except Exception as exc:
            print(f'Error: {exc}')
            self.error = str(exc)




class SuggestTaskController(QObject):

    progressChanged = Signal()
    runningChanged = Signal()
    statusChanged = Signal()

    def __init__(self, parent = None):
        super().__init__(parent)

        self._progress = 0
        self._running = False
        self._status = ""

        self._worker = None

    @Property(int, notify=progressChanged)
    def progress(self):
        return self._progress

    @Property(bool, notify=runningChanged)
    def running(self):
        return self._running

    @Property(str, notify=statusChanged)
    def status(self):
        return self._status

    def _set_status(self, status):
        self._status = status
        self.statusChanged.emit()

    @Slot(QObject, "QVariantList")
    def startTask(self, backend: Backend, row):
        if self._running:
            return 

        self._progress = 0
        self.progressChanged.emit()

        self._set_status("Processing ...")

        self._worker = SuggestTaskWorker(backend, row)

        self._worker.progressChanged.connect(self._update_progress)

        self._worker.finished.connect(self._task_finished)

        self._running = True
        self.runningChanged.emit()

        self._worker.start()

    @Slot()
    def cancelTask(self):
        if self._worker and self._running:
            self._set_status("Cancelling ...")
            self._worker.requestInterruption()

    @Slot()
    def _update_progress(self, value):
        self._progress = value
        self.progressChanged.emit()

    @Slot()
    def _task_finished(self):
        worker = self._worker

        if worker.error:
            self._set_status(f"Error : {worker.error}")
        elif worker.cancelled:
            self._set_status("Task cancelled")
        else:
            self._set_status("Task completed successfully")

        self._worker = None
        worker.deleteLater()

        self._running = False
        self.runningChanged.emit()


        