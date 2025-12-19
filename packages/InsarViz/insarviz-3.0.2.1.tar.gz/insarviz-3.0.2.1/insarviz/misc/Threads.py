from .__prelude__ import logger
from . import Qt

class Runnable(Qt.QRunnable):
    def abort(self):
        pass

class Cancellable(Qt.QRunnable):
    def __init__(self, pool, runnable):
        super().__init__(self)
        self._pool = pool
        self._runnable = runnable

    def __hash__(self):
        return id(self)
    def __eq__(self, other):
        return id(self) == id(other)

    def run(self):
        try:
            return self._runnable.run()
        finally:
            self._pool.remove(self)
    def abort(self):
        self._runnable.abort()

class ThreadPool:
    def __init__(self, global_instance):
        self._global_instance = global_instance
        self._threads = {}

    def start(self, runnable):
        cancellable = Cancellable(self, runnable)
        self._threads[cancellable] = cancellable
        self._global_instance.start(cancellable)

    def remove(self, cancellable):
        del self._threads[cancellable]

    def abort_all(self):
        all_threads = [*self._threads.keys()]
        for cancellable in all_threads:
            cancellable.abort()
        self._global_instance.waitForDone(1000)

GLOBAL_THREAD_POOL = ThreadPool(Qt.QThreadPool.globalInstance())
