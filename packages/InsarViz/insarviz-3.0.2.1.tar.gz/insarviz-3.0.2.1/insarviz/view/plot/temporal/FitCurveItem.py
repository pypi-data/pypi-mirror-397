from typing import Any
import pyqtgraph
import numpy as np
import time

from .__prelude__ import (
    logger, Qt, CurveEstimate, linmap, Runnable, GLOBAL_THREAD_POOL
)

class FitCurveItem(pyqtgraph.PlotDataItem):
    class RunnerSignals(Qt.QObject):
        updated_estimate = Qt.Signal()
        finished_estimate = Qt.Signal()
    class Runner(Runnable):
        def __init__(self, estimate):
            super().__init__()
            self.stop = False
            self.estimate = estimate
            self._signals = FitCurveItem.RunnerSignals()
        @property
        def updated_estimate(self):
            return self._signals.updated_estimate
        @property
        def finished_estimate(self):
            return self._signals.finished_estimate

        def abort(self):
            self.stop = True

        def run(self):
            i = 0
            start_time = time.perf_counter()
            try:
                while not self.stop:
                    if not self.estimate.improve():
                        logger.debug("Cannot improve estimate further after %d iterations", i)
                        break
                    current_time = time.perf_counter()
                    if current_time - start_time >= 0.1:
                        self.updated_estimate.emit()
                        start_time = current_time
                    i += 1
                self.updated_estimate.emit()
                self.finished_estimate.emit()
            except RuntimeError as e:
                logger.debug("Error while improving curve. Maybe the application exited early")

    finished_estimate = Qt.Signal(Any)
    def __init__(self, curve):
        super().__init__()
        self._curve = curve
        self._runner = None

    def set_fit_points(self, x, y):
        if self._runner is not None:
            self.stop_fit()

        self.from_x, self.to_x = linmap(x[0], x[-1])
        self.from_y, self.to_y = linmap(np.nanmin(y), np.nanmax(y))
        self._x_mapped = self.from_x(x)
        self._y_mapped = self.from_y(y)

    def set_curve(self, curve):
        self.stop_fit()
        self._curve = curve

    @Qt.Slot(str)
    def _on_estimate_change(self):
        x_inp = np.linspace(-1.0, 1.0, num=256)
        xs = self.to_x(x_inp)
        y_out = self._curve.func(x_inp, *self._estimate.current_guess)
        ys = self.to_y(y_out)
        self.setData(x = xs, y = ys)

    def start_fit(self):
        if self._runner is not None:
            self.stop_fit()
        curve = self._curve
        est = CurveEstimate(curve, self._x_mapped, self._y_mapped)
        self._estimate = est
        self._runner = self.Runner(self._estimate)
        self._runner.updated_estimate.connect(self._on_estimate_change)
        def on_finished():
            self.finished_estimate.emit(est)
        self._runner.finished_estimate.connect(on_finished)
        GLOBAL_THREAD_POOL.start(self._runner)

    def stop_fit(self):
        if self._runner is None:
            return
        self._runner.stop = True
        self._runner = None
