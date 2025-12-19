import numpy as np
from typing import Any, Optional, override
import pyqtgraph

from .__prelude__ import (Qt, colormaps, Leaf, Container)
from .Schema import Schema

def make_colormap(name, values, mode):
    formatted_values = np.rint(np.array(values)*255).astype(int)
    ticks = np.linspace(0., 1., len(formatted_values))
    return pyqtgraph.ColorMap(ticks, formatted_values, name=name, mapping=mode)
pg_colormaps = { name: make_colormap(name, values, pyqtgraph.ColorMap.CLIP) for name, values in colormaps.items() }
pg_colormaps.update({ 'cyclic '+name: make_colormap('cyclic '+name, values, pyqtgraph.ColorMap.REPEAT) for name, values in colormaps.items() })

class ColormapEditor(pyqtgraph.HistogramLUTWidget):
    def __init__(self, colormap):
        super().__init__()
        self._colormap = colormap
        self.setBackground('w')
        self.setForegroundBrush(Qt.Qt.GlobalColor.transparent)

        self._hist_graph: pyqtgraph.BarGraphItem = pyqtgraph.BarGraphItem(x0=[],x1=[],y0=[],y1=[])
        self._hist_graph.setRotation(90)
        self._hist_graph.setOpts(brush = Qt.QColor(220,20,20,100), pen=None)
        hist, bins = colormap.image_histogram
        self._hist_graph.setOpts(x0 = bins[:-1], x1 = bins[1:], y0 = 0, y1 = hist)
        self.vb.addItem(self._hist_graph)

        self._init_colormap_menu()
        self._set_histogram_levels()
        self.setLevels(self._colormap.xzero, self._colormap.xone)
        self.setHistogramRange(self._colormap.xzero, self._colormap.xone, padding=0.1)
        self.sigLevelsChanged.connect(self._on_levels_changed)

    def _set_histogram_levels(self, set_levels = False):
        hist, bins = self._colormap.image_histogram
        hist_norm = hist/np.sum(hist)
        hist_cum = np.cumsum(hist_norm)
        lower, upper = np.array(bins)[np.searchsorted(hist_cum, [0.1, 0.9])]
        self.vb.setLimits(yMin=bins[0], yMax=bins[-1])
        self.setHistogramRange(lower,upper, padding=0.1)
        if set_levels:
            self.setLevels(min=lower, max=upper)

    @Qt.Slot(Any) #type: ignore
    def _on_levels_changed(self, item):
        xmin, xmax = item.getLevels()
        self._colormap.xzero = xmin
        self._colormap.xone = xmax

    def sizeHint(self):
        return Qt.QSize(200, 600)

    def auto_range(self):
        self._set_histogram_levels(True)

    def _init_colormap_menu(self):
        grad = self.gradient

        grad.menu = pyqtgraph.ColorMapMenu(
            userList=[
                pg_colormaps[name] for name in colormaps.keys()
            ] + [
                pg_colormaps['cyclic '+name] for name in colormaps.keys()
            ])
        grad.menu.removeAction(grad.menu.actions()[0]) # Remove the default "None" colormap
        grad.menu.sigColorMapTriggered.connect(grad.colorMapMenuClicked)
        grad.menu.sigColorMapTriggered.connect(self._on_colormap_selected)
        grad.colorMapMenuClicked(pg_colormaps[self._colormap.name])

    def _on_colormap_selected(self, colormap):
        self._colormap.name = colormap.name
        self._colormap.image = colormap.getLookupTable(nPts=1024)
        self._colormap.is_cyclic = colormap.mapping_mode == pyqtgraph.ColorMap.REPEAT

class ColorMapSchema(Schema):
    class ColorMapNode(Schema.Node):
        def __init__(self, item_model: Qt.QAbstractItemModel, schema: "ColorMapSchema", model):
            super().__init__(item_model, schema)
            model.fieldChanged.connect(self._on_colormap_changed)
            self.set_model(model)

        @Qt.Slot(str)
        def _on_colormap_changed(self, field):
            if field == "image":
                self.dataChanged.emit([Qt.Qt.ItemDataRole.DisplayRole])

        def flags(self):
            return Qt.Qt.ItemFlag.ItemIsEnabled | Qt.Qt.ItemFlag.ItemIsEditable | super().flags()
        def data(self, role):
            if role == Qt.Qt.ItemDataRole.SizeHintRole:
                return Qt.QSize(100, 20)
            if role == Qt.Qt.ItemDataRole.DisplayRole:
                return ""
            return None

        def createEditor(self, parent):
            self._dialog = Qt.QDialog(parent)
            self._dialog.setWindowFlags(self._dialog.windowFlags() | Qt.Qt.WindowStaysOnTopHint)
            self._dialog.setWindowTitle(f"Colormap : {self.model.name}")
            widgets = type('', (object,), {})()

            wtree = Container(Qt.QVBoxLayout, (), [
                (Leaf(ColormapEditor, (self.model, ), id="colormap_editor"), {"stretch":1}),
                Leaf(Qt.QPushButton, ("Autorange", ), id="autorange_button"),
            ])

            wtree.create_in(self._dialog, widgets)
            widgets.autorange_button.clicked.connect(lambda: widgets.colormap_editor.auto_range())

            self._dialog.show()
            return self._dialog
        def destroyEditor(self):
            self._dialog.close()
            self._dialog = None
            return False

        def paint(self, painter, option):
            rect = option.rect.adjusted(5,3,-5,-3)
            line = Qt.QImage((np.tile(self.model.interpolated(rect.width()), (rect.height(), 1))).astype(np.uint8),
                          rect.width(), rect.height(), rect.width()*3, Qt.QImage.Format.Format_RGB888)
            painter.drawImage(rect.x(), rect.y(), line)
            return True

    def __init__(self, name):
        self.name = name

    def make_node(self, item_model: Qt.QAbstractItemModel, model: Any) -> "Schema.Node":
        return self.ColorMapNode(item_model, self, model)
