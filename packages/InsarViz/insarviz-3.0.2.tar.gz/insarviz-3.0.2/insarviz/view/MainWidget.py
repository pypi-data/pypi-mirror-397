from typing import Any, Optional
import numpy as np
import pyqtgraph
import datetime
from pyqtgraph.widgets.ColorMapMenu import buildMenuEntryAction

from .__prelude__ import Qt, Matrix, colormaps, logger
from .GLWidget import GLWidget
from .WidgetTree import Container, Leaf
from .ComputedProgressBar import ComputedProgressBar

class BandLine(pyqtgraph.InfiniteLine):
    hovered = Qt.Signal()

    def hoverEvent(self, ev):
        self.hovered.emit()

class BandSlider(pyqtgraph.PlotWidget):
    LINE_PEN = Qt.QColor('black')
    HOVER_LINE_PEN = pyqtgraph.functions.mkPen('red', width=3)
    SELECTED_LINE_PEN = pyqtgraph.functions.mkPen('blue', width=3)
    REFERENCE_LINE_PEN = pyqtgraph.functions.mkPen('purple', width=3)
    DRAGGED_LINE_PEN = pyqtgraph.functions.mkPen('cyan', width=3)

    def __init__(self, selected_band):
        super().__init__()
        # Autorange makes adding lines very slow, and is useless in the band slider
        self.setBackground('w')
        self.setForegroundBrush(Qt.Qt.GlobalColor.transparent)

        self.plotItem.disableAutoRange()
        self.setMaximumHeight(50)
        self.setMouseEnabled(x=False, y=False)
        self.hideAxis('left')
        self._selected_band = selected_band
        self._selected_band.fieldChanged.connect(self._on_band_change)
        self._selected_band_line = pyqtgraph.InfiniteLine(pen=self.SELECTED_LINE_PEN, pos=self._selected_band.timestamp, movable=True)
        self._selected_band_line.addMarker('<|>')
        self._selected_band_line.sigDragged.connect(self._on_drag_selected_band)
        self._selected_band_line.sigPositionChangeFinished.connect(lambda: self._selected_band_line.setPen(self.SELECTED_LINE_PEN))
        self._reference_band_line = pyqtgraph.InfiniteLine(pen=self.REFERENCE_LINE_PEN)
        self._reference_band_line.addMarker('<|>')
        self.__set_reference_pos()
        self._band_lines = []
        self._set_timestamps()

        self._temp_hovered = None

    def __set_reference_pos(self):
        if self._selected_band.reference_timestamp is None:
            self._reference_band_line.setVisible(False)
        else:
            self._reference_band_line.setPos(self._selected_band.reference_timestamp)
            self._reference_band_line.setVisible(True)

    @Qt.Slot(Any)
    def _on_drag_selected_band(self, band):
        timestamp = band.getPos()[0]
        self._selected_band_line.setPen(self.DRAGGED_LINE_PEN)
        self._selected_band.band_number = int(self._selected_band.dataset.nearest_band_to_timestamp(timestamp))
    @Qt.Slot(str)
    def _on_band_change(self, field):
        if field == "band_number":
            self._selected_band_line.setPos(self._selected_band.timestamp)
        if field == "reference_timestamp":
            self.__set_reference_pos()
        if field == "dataset":
            self._set_timestamps()

    def _set_timestamps(self):
        logger.debug("Setting timestamps")
        xs = self._selected_band.dataset.band_timestamps
        for line in self._band_lines:
            self.plotItem.removeItem(line)
        logger.debug("Removed lines")
        self.plotItem.removeItem(self._selected_band_line)
        self.plotItem.removeItem(self._reference_band_line)
        self._band_lines = []
        for i,x in enumerate(xs):
            line = BandLine(pos=x, pen=self.LINE_PEN, angle=90)
            line.hovered.connect(self.__on_band_hovered(i, x))
            self._band_lines.append(line)
        logger.debug("Created new lines")

        for line in self._band_lines:
            self.plotItem.addItem(line)
        logger.debug("Added %d new lines", len(self._band_lines))
        self.plotItem.addItem(self._selected_band_line)
        self.plotItem.addItem(self._reference_band_line)
        self.setXRange(xs[0], xs[-1], padding=0.1)
        if self._selected_band.dataset.has_band_dates:
            self.setAxisItems({'bottom': pyqtgraph.DateAxisItem(units='yyyy-mm-dd') })
        logger.debug("Done setting timestamps")

    def __on_band_hovered(self, i, x):
        return lambda: self.setToolTip(f"Band #{i+1} : {self.__timestamp_date(x)}")

    def __timestamp_date(self, timestamp):
        if self._selected_band.dataset.has_band_dates:
            return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        else:
            return str(timestamp)


    def _set_hovered(self, hovered):
        if self._temp_hovered is not None:
            self._temp_hovered.setPen(self.LINE_PEN)
        self._temp_hovered = hovered
        if self._temp_hovered is not None:
            self._temp_hovered.setPen(self.HOVER_LINE_PEN)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        timestamp = self.getViewBox().mapSceneToView(event.pos()).x()
        nearest = self._selected_band.dataset.nearest_band_to_timestamp(timestamp)
        self._set_hovered(self._band_lines[nearest])
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        timestamp = self.getViewBox().mapSceneToView(event.pos()).x()
        nearest = self._selected_band.dataset.nearest_band_to_timestamp(timestamp)
        self._selected_band.band_number = int(nearest)

    def leaveEvent(self, event):
        self._set_hovered(None)

def make_colormap(name, values, mode):
    formatted_values = np.rint(np.array(values)*255).astype(int)
    ticks = np.linspace(0., 1., len(formatted_values))
    return pyqtgraph.ColorMap(ticks, formatted_values, name=name, mapping=mode)

pg_colormaps = { name: make_colormap(name, values, pyqtgraph.ColorMap.CLIP) for name, values in colormaps.items() }
pg_colormaps.update({ 'cyclic '+name: make_colormap('cyclic '+name, values, pyqtgraph.ColorMap.REPEAT) for name, values in colormaps.items() })

class MainWidget(Qt.QSplitter):
    class ChildrenOfInterest:
        def __init__(self):
            self.main_map: GLWidget
            self.position_label: Qt.QLabel
            self.histogram_widget: pyqtgraph.HistogramLUTWidget
            self.legend_widget: pyqtgraph.GraphicsView
            self.autorange_button: Qt.QPushButton
            self.autorange_all_button: Qt.QPushButton
            self.band_slider: BandSlider
            self.full_histogram_progress: ComputedProgressBar

    # Public interface
    pixel_hovered = Qt.Signal(tuple)

    def __init__(self, window_state):
        super().__init__()
        self._state = window_state

        map_skel = Container(Qt.QVBoxLayout, (), [
            Leaf(BandSlider, (self._state.current_band(),), id="band_slider"),
            (Leaf(GLWidget, (self._state.map_scene,), id = "main_map"), {"stretch": 1}),
        ])
        hist_skel = Container(Qt.QVBoxLayout, (), [
            Leaf(Qt.QPushButton, ("Autorange current band",), id="autorange_button"),
            Leaf(Qt.QPushButton, ("Autorange all bands",), id="autorange_all_button"),
            (Leaf(pyqtgraph.HistogramLUTWidget, (), id="histogram_widget"), {"stretch": 1}),
            Leaf(pyqtgraph.GraphicsView, (), id="legend_widget"),
            Leaf(ComputedProgressBar, (), id="full_histogram_progress")
        ])
        self.widgets = self.ChildrenOfInterest()
        self.setChildrenCollapsible(False)
        self.addWidget(map_skel.create(self.widgets))
        hist_side_widget = hist_skel.create(self.widgets)
        hist_side_widget.setMaximumWidth(200)
        self.addWidget(hist_side_widget)
        self.setCollapsible(1, True)

        self._autorange_shortcut = Qt.QShortcut(Qt.QKeySequence('Ctrl+A'), self.widgets.main_map)
        self._autorange_shortcut.activated.connect(self._on_autorange)
        self._autorange_all_shortcut = Qt.QShortcut(Qt.QKeySequence('Ctrl+Shift+A'), self.widgets.main_map)
        self._autorange_all_shortcut.activated.connect(self._on_autorange_all)

        self.widgets.main_map.positionChanged.connect(self._set_cursor_position)
        self._selected_band = self._state.current_band()
        self._selected_band.fieldChanged.connect(self._on_band_changed)
        self._band_colormap = self._state.band_colormap
        self._band_colormap.fieldChanged.connect(self._on_colormap_changed)
        self._setting_levels = False

        self.widgets.autorange_button.clicked.connect(self._on_autorange)
        self.widgets.autorange_all_button.setEnabled(False)
        self.widgets.autorange_all_button.clicked.connect(self._on_autorange_all)

        self._hist_graph: pyqtgraph.BarGraphItem = pyqtgraph.BarGraphItem(x0=[],x1=[],y0=[],y1=[])
        self._hist_graph.setRotation(90)
        self._hist_graph.setOpts(brush = Qt.QColor(220,20,20,100), pen=None)
        self._full_hist_graph: pyqtgraph.BarGraphItem = pyqtgraph.BarGraphItem(x0=[],x1=[],y0=[],y1=[])
        self._full_hist_graph.setRotation(90)
        self._full_hist_graph.setOpts(brush = Qt.QColor(20,20,220,100), pen=None)

        legend_item = pyqtgraph.LegendItem(size=None)
        legend_item.addItem(self._hist_graph, "current band")
        legend_item.addItem(self._full_hist_graph, "all bands")
        self.widgets.legend_widget.setFixedHeight(legend_item.height())
        self.widgets.legend_widget.setMaximumWidth(200)
        self.widgets.legend_widget.setCentralWidget(legend_item)

        self.widgets.histogram_widget.setBackground('w')
        self.widgets.histogram_widget.setForegroundBrush(Qt.Qt.GlobalColor.transparent)
        self.widgets.histogram_widget.vb.addItem(self._full_hist_graph)
        self.widgets.histogram_widget.vb.addItem(self._hist_graph)

        self._init_colormap_menu()

        self.widgets.histogram_widget.sigLevelsChanged.connect(self._on_levels_changed)

    @property
    def resized_viewport(self):
        return self.widgets.main_map.resized_viewport
    @property
    def world_to_clip(self):
        return self.widgets.main_map.world_to_clip

    # Qt events
    def leaveEvent(self, event):
        self.pixel_hovered.emit(None)
    def closeEvent(self, event):
        self.widgets.main_map.close()
        event.accept()

    # Private methods and properties
    def _init_colormap_menu(self):
        grad = self.widgets.histogram_widget.gradient

        grad.menu = pyqtgraph.ColorMapMenu(
            userList=[
                pg_colormaps[name] for name in colormaps.keys()
            ] + [
                pg_colormaps['cyclic '+name] for name in colormaps.keys()
            ])
        grad.menu.removeAction(grad.menu.actions()[0]) # Remove the default "None" colormap
        grad.menu.sigColorMapTriggered.connect(grad.colorMapMenuClicked)
        grad.menu.sigColorMapTriggered.connect(self._on_colormap_selected)

    @Qt.Slot(str)
    def _on_band_changed(self, field):
        if field == "dataset":
            self._compute_histograms(set_levels = True)
            self._selected_band.dataset.full_histograms.ready.connect(self._set_full_histograms)
            self.widgets.full_histogram_progress.set_computed_value(self._selected_band.dataset.full_histograms)
        if field == "image":
            self._compute_histograms()

    @Qt.Slot()
    def _set_full_histograms(self):
        hist, bins = self._selected_band.dataset.full_histograms.latest()
        self.widgets.autorange_all_button.setEnabled(True)
        self._full_hist_graph.setOpts(x0 = bins[:-1], x1 = bins[1:], y0 = 0, y1 = hist)

    @Qt.Slot(str)
    def _on_colormap_changed(self, field, old_value):
        colormap = self._band_colormap
        if field == "name" and colormap.name != old_value:
            self.widgets.histogram_widget.gradient.menu.sigColorMapTriggered.emit(pg_colormaps[colormap.name])
        if field in ("xzero", "xone") and getattr(colormap, field) != old_value:
            if not self._setting_levels:
                vb = self.widgets.histogram_widget.vb
                lim_min, lim_max = vb.state['limits']['yLimits']
                amplitude = colormap.xone-colormap.xzero
                lower, upper = colormap.xzero-0.1*amplitude, colormap.xone+0.1*amplitude
                set_range = False
                if lim_min > lower:
                    vb.setLimits(yMin=min(lower, lim_min))
                    set_range = True
                if lim_max < upper:
                    vb.setLimits(yMax=max(upper, lim_max))
                    set_range = True
                if set_range:
                    self.widgets.histogram_widget.setHistogramRange(lower, upper)
            self.widgets.histogram_widget.setLevels(min=colormap.xzero, max=colormap.xone)

    @Qt.Slot(Any) #type: ignore
    def _on_colormap_selected(self, colormap):
        self._state.band_colormap.name = colormap.name.removeprefix('cyclic ')
        self._state.band_colormap.image = colormap.getLookupTable(nPts=1024)
        self._state.band_colormap.is_cyclic = colormap.mapping_mode == pyqtgraph.ColorMap.REPEAT

    @Qt.Slot(Any) #type: ignore
    def _on_levels_changed(self, item):
        xmin, xmax = item.getLevels()
        self._setting_levels = True
        self._state.band_colormap.xzero = xmin
        self._state.band_colormap.xone = xmax
        self._setting_levels = False

    @Qt.Slot()
    def _on_autorange(self):
        self._set_histogram_levels(*self._selected_band.histogram)
    @Qt.Slot()
    def _on_autorange_all(self):
        self._set_histogram_levels(*self._selected_band.dataset.full_histograms.latest())

    def _set_histogram_levels(self, hist, bins, set_levels=True):
        hist_norm = hist/np.sum(hist)
        hist_cum = np.cumsum(hist_norm)
        lower, upper = np.array(bins)[np.searchsorted(hist_cum, [0.02, 0.98])]
        self.widgets.histogram_widget.vb.setLimits(yMin=bins[0], yMax=bins[-1])
        self.widgets.histogram_widget.setHistogramRange(lower,upper, padding=0.1)
        if set_levels:
            self.widgets.histogram_widget.setLevels(min=lower, max=upper)

    @Qt.Slot(float, float)
    def _set_cursor_position(self, x_model, y_model):
        self._state.hovered_model = (x_model, y_model)

    def _compute_histograms(self, set_levels = False):
        hist, bins = self._selected_band.histogram
        if set_levels:
            self._set_histogram_levels(hist, bins)
        self._hist_graph.setOpts(x0 = bins[:-1], x1 = bins[1:], y0 = 0, y1 = hist)
