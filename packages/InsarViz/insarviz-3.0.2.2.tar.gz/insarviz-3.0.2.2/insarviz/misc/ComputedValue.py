"""
TODO_DOC
"""

from .__prelude__ import logger
from .Threads import GLOBAL_THREAD_POOL, Runnable
from . import Qt

class ComputedValue(Qt.QObject):
    progressed = Qt.Signal()
    ready = Qt.Signal()

    class ReadyRunner:
        def __init__(self, result, value):
            self._result = result
            self._value = value
        def set_next(self, runner):
            self._result.set_runner(runner(self._value))
        def progress(self):
            return 1.0
        def value(self):
            return self._value
        def start(self):
            self._result.progressed.emit()
        def stop(self):
            pass
        def abort(self):
            pass
    class ComputeRunner(Runnable):
        def __init__(self, result, value, compute):
            super().__init__()
            self.setAutoDelete(True)
            self._result = result
            self._value = value
            self._progress = 0.0
            self._compute = compute
            self._next_runner = lambda value: ComputedValue.ReadyRunner(self._result, value)
            self._stop = False
            self._abort = False

        def set_next(self, runner):
            self._next_runner = runner
            self.stop()
        def progress(self):
            return self._progress
        def value(self):
            return self._value
        def run(self):
            progress_gen = self._compute()
            self._result.progressed.emit()
            try:
                while True:
                    self._progress = next(progress_gen)
                    self._result.progressed.emit()
                    if self._stop or self._abort:
                        value = self._value
                        break
            except StopIteration as e:
                value = e.value
            except RuntimeError as e:
                logger.debug("Runner ended without a result. This must mean the application exited early")
                return
            if not self._abort:
                next_runner = self._next_runner(value)
                self._result.set_runner(next_runner)
            else:
                logger.debug("Thread aborted")
        def start(self):
            GLOBAL_THREAD_POOL.start(self)
        def stop(self):
            self._stop = True
        def abort(self):
            logger.debug("Aborting runner")
            self._abort = True
            self.stop()

    def __init__(self, value):
        super().__init__()
        self._current_runner = self.ReadyRunner(self, value)

    def latest(self):
        return self._current_runner.value()
    def progress(self):
        return self._current_runner.progress()
    def set_runner(self, runner):
        old_runner = self._current_runner
        self._current_runner = runner
        runner.start()
        self.ready.emit()
    def set_value(self, value):
        self._current_runner.set_next(lambda _: self.ReadyRunner(self, value))
    def recompute(self, compute):
        self._current_runner.set_next(lambda value: self.ComputeRunner(self, value, compute))
