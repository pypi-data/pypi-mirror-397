from .__prelude__ import Qt, logger

class ComputedProgressBar(Qt.QProgressBar):
    def __init__(self):
        super().__init__()
        self._computed_value = None
        self._set_value()

    def set_computed_value(self, computed_value):
        if self._computed_value is not None:
            self._computed_value.progressed.disconnect(self._set_value)
        self._computed_value = computed_value
        if self._computed_value is not None:
            self._computed_value.progressed.connect(self._set_value)

    @Qt.Slot()
    def _set_value(self):
        if self._computed_value is not None:
            progress = self._computed_value.progress()
            if isinstance(progress, tuple):
                label, progress = progress
                self.setFormat(label)
        else:
            progress = 1.0
        prog_percent = int(100*progress)
        if prog_percent == 100:
            self.setVisible(False)
        else:
            self.setVisible(True)
            if self.value() != prog_percent:
                self.setValue(prog_percent)
