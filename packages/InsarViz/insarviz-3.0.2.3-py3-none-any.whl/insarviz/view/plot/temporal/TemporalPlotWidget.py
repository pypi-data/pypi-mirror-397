from typing import Any
import pyqtgraph
import numpy as np
import datetime
from pyqtgraph.GraphicsScene import exportDialog

from .__prelude__       import ( Qt, Container, Leaf, SchemaView, ListSchema, MapPoint, FocusPoint, ItemChooser, IconLabel, icon_with_label, SELF )
from .PointSchema       import point_schema, focus_point_schema
from .FitCurveItem      import FitCurveItem
from .PointDataItem     import PointDataItem, PointData
from .SelectedBandLine  import SelectedBandLine

class TemporalPlotWidget(Qt.QWidget):
    class ChildrenOfInterest:
        def __init__(self):
            self.plot_widget: pyqtgraph.PlotWidget
            self.schema_view: SchemaView
            self.cursor_view: SchemaView
            self.lock_axes_checkbox: Qt.QCheckBox
            self.reference_chooser: ItemChooser
            self.export_button: Qt.QPushButton

    def __init__(self, selected_band, points, profiles):
        super().__init__()
        self.__points = points
        self.__focus_points = profiles.map(FocusPoint)
        self.__selected_band = selected_band
        self.__selected_band.fieldChanged.connect(self.__on_band_change)

        self.__cursor_point = MapPoint("Cursor",0,0,0,Qt.QColor('red'))
        self.__cursor_point.show_in_plot = False
        self.__reference_data = PointData(self.__selected_band, None)

        skel = Container(Qt.QHBoxLayout, (), [
            (Leaf(pyqtgraph.PlotWidget, (), id="plot_widget"), {"stretch": 1}),
            Container(Qt.QVBoxLayout, (), [
                Leaf(Qt.QCheckBox, ("Lock Axes",), id="lock_axes_checkbox"),

                    icon_with_label("insarviz:ref.png", "Reference Point"),
                    Leaf(ItemChooser, (self.__points,), id="reference_chooser"),


                    icon_with_label("insarviz:points.png", "Points"),
                    (Leaf(SchemaView, (ListSchema("points", point_schema), self.__points), id="schema_view"),
                     {"stretch": 1}),

                    icon_with_label("insarviz:profile.png", "Focus Points"),
                    (Leaf(SchemaView, (ListSchema("points", focus_point_schema), self.__focus_points), id="profile_schema_view"),
                     {"stretch": 1}),

                    icon_with_label("insarviz:cursor.png", "Cursor Point"),
                    (Leaf(SchemaView, (point_schema, self.__cursor_point), id="cursor_view"),
                     {"stretch": 0}),
                    (Leaf(Qt.QWidget, ()), {"stretch": 2}),

                    Leaf(Qt.QPushButton, ("Export...",), id="export_button"),
            ])
        ])
        self.widgets = self.ChildrenOfInterest()
        skel.create_in(self, self.widgets)

        self.make_point_item(self.__cursor_point)
        self.__point_items = self.__points.map(self.make_point_item, self.delete_point_item)
        self.__focus_point_items = self.__focus_points.map(self.make_point_item, self.delete_point_item)

        self.__selected_band_line = SelectedBandLine(self.__selected_band.dynamic_attribute("dataset"), self.__selected_band.dynamic_attribute("band_number"))
        self.__selected_band_line.sigDragged.connect(self.__on_band_dragged)
        self.__reference_band_line = SelectedBandLine(self.__selected_band.dynamic_attribute("dataset"), self.__selected_band.dynamic_attribute("reference_band_number"))
        self.__reference_band_line.sigDragged.connect(self.__on_reference_dragged)
        self.__dynamic_units = SELF.dataset.value_units[self.__selected_band]
        self.__dynamic_units.drive(lambda units: self.widgets.plot_widget.setLabel('left', f"LOS displacement ({units})" if units is not None else "No units"))
        self.widgets.plot_widget.addItem(self.__selected_band_line)
        self.widgets.plot_widget.addItem(self.__reference_band_line)
        self.widgets.plot_widget.setMouseEnabled(x=False, y=True)
        self.widgets.plot_widget.setBackground('w')
        self.widgets.plot_widget.setForegroundBrush(Qt.Qt.GlobalColor.transparent)
        self.widgets.reference_chooser.currentIndexChanged.connect(self.__on_reference_selected)
        self.widgets.export_button.clicked.connect(self.__export)
        self.widgets.lock_axes_checkbox.checkStateChanged.connect(self.__on_lock_axes)


    @Qt.Slot()
    def __export(self):
        self.__export_dialog = exportDialog.ExportDialog(self.widgets.plot_widget.plotItem.scene())
        self.__export_dialog.show(self.widgets.plot_widget)

    @Qt.Slot(Any)
    def __on_lock_axes(self, checked):
        if checked == Qt.Qt.CheckState.Checked:
            self.widgets.plot_widget.disableAutoRange()
        else:
            self.widgets.plot_widget.enableAutoRange()

    @Qt.Slot(Any)
    def __on_band_dragged(self, band):
        nearest = self.__selected_band.dataset.nearest_band_to_timestamp(band.getPos()[0])
        self.__selected_band.band_number = int(nearest)
    @Qt.Slot(Any)
    def __on_reference_dragged(self, band):
        nearest = self.__selected_band.dataset.nearest_band_to_timestamp(band.getPos()[0])
        self.__selected_band.reference_band_number = int(nearest)

    @Qt.Slot(str)
    def __on_band_change(self, field, old_value):
        if field == "dataset":
            if self.__selected_band.dataset.has_band_dates:
                self.widgets.plot_widget.setAxisItems({"bottom": pyqtgraph.DateAxisItem(text='Date', units='yyyy-mm-dd')})
        if field == "band_number":
            self.__selected_band_line.setPos(self.__selected_band.timestamp)

    @Qt.Slot(int)
    def __on_reference_selected(self, index):
        ref_index = self.widgets.reference_chooser.itemData(index)
        old_point = self.__reference_data.point
        if old_point is not None:
            old_point.is_reference = False
        if ref_index is None or ref_index == -1:
            self.__reference_data.set_point(None)
        else:
            self.__reference_data.set_point(self.__points[ref_index])
            self.__points[ref_index].is_reference = True

    def set_cursor_coords(self, px):
        if px is None:
            self.__cursor_point.show_in_plot = False
        else:
            self.__cursor_point.x, self.__cursor_point.y = px
            self.__cursor_point.show_in_plot = True

    def make_point_item(self, p):
        ret = PointDataItem(PointData(self.__selected_band, p), self.__reference_data)
        def on_points_hovered(_a, points, _b):
            def point_text(p):
                date = datetime.datetime.fromtimestamp(p.pos().x()).strftime("%Y-%m-%d")
                index = p.index()
                return f"Point at {date} (band {index}) : {ret.point_data.point_ys[0][p.index()]}"
            self.widgets.plot_widget.plotItem.getViewBox().setToolTip(
                "\n".join([point_text(p) for p in points]))
        ret.sigPointsHovered.connect(on_points_hovered)
        ret.visibleChanged.connect(lambda: self.widgets.plot_widget.autoRange())
        for item in ret.items:
            self.widgets.plot_widget.addItem(item)
        return ret

    def delete_point_item(self, i, item):
        for item in item.items:
            self.widgets.plot_widget.removeItem(item)
