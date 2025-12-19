import pyqtgraph
import datetime

from .__prelude__ import Qt

class SelectedBandLine(pyqtgraph.InfiniteLine):
    def __init__(self, dynamic_dataset, dynamic_band_number):
        super().__init__(angle=90, movable=True)
        self._dynamic_dataset = dynamic_dataset
        self._dynamic_band_number = dynamic_band_number
        self._dynamic_band_number.value_changed.connect(self._set_band_number)
        self._set_band_number()

    @property
    def dataset(self):
        return self._dynamic_dataset.value
    @property
    def band_number(self):
        return self._dynamic_band_number.value

    @Qt.Slot()
    def _set_band_number(self):
        if self.band_number is None:
            self.setVisible(False)
            return
        else:
            self.setVisible(True)
        timestamp = self.dataset.band_timestamps[self.band_number]
        self.setPos(timestamp)
        tooltip = f"Band #{self.band_number+1}"
        if self.dataset.has_band_dates:
            date = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
            tooltip = f"{tooltip} (at {date})"
        self.setToolTip(tooltip)
