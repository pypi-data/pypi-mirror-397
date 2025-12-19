from typing import Any
import numpy as np
import pyqtgraph
import pyqtgraph.opengl
from pyqtgraph.GraphicsScene import exportDialog

from .__prelude__ import (
    Qt, color_icon, PointData, ProfileData, linmap, ProfileScene,
    Container, Leaf,
    ItemChooser,
    ComputedProgressBar,
    IconLabel,
    GLWidget,
    SELF,
    BoldLabel, icon_with_label
)

class ProfileDataItem2D(pyqtgraph.PlotItem):
    def __init__(self, profile_data):
        super().__init__()
        self.__profile_data = profile_data
        self.__scatter_item = pyqtgraph.PlotDataItem(symbolSize=5)
        # self.scatter_item.scatter.setData(hoverable=True)
        self.addItem(self.scatter_item)

        self.__spatial_std_curve_low = pyqtgraph.PlotCurveItem(connect='finite', pen=self.__profile_data.color)
        self.__spatial_std_curve_high = pyqtgraph.PlotCurveItem(connect='finite', pen=self.__profile_data.color)
        self.__spatial_error_item = pyqtgraph.FillBetweenItem(self.__spatial_std_curve_low, self.__spatial_std_curve_high)
        self.spatial_error_item.setZValue(-1.0)
        self.addItem(self.spatial_error_item)

        self.__temporal_std_curve_low = pyqtgraph.PlotCurveItem(connect='finite', pen=self.__profile_data.color)
        self.__temporal_std_curve_high = pyqtgraph.PlotCurveItem(connect='finite', pen=self.__profile_data.color)
        self.__temporal_error_item = pyqtgraph.FillBetweenItem(self.__temporal_std_curve_low, self.__temporal_std_curve_high)
        self.temporal_error_item.setZValue(-1.0)
        self.addItem(self.temporal_error_item)

        self.__focus_line = pyqtgraph.InfiniteLine(angle=90, movable=True, pen=self.__profile_data.color)
        self.__focus_line.sigDragged.connect(self.__on_focus_dragged)
        self.addItem(self.__focus_line)

        self.__profile_data.dynamic_attribute("values_and_variance_2d").drive(self.__update_plot)
        self.__profile_data.dynamic_attribute("values_2d_temporal").drive(self.__update_temporal_plot)
        self.__profile_data.dynamic_attribute("color").drive(self.__set_color)
        self.__profile_data.dynamic_attribute("show_spatial_variance").drive(self.__set_show_spatial_variance)
        self.__profile_data.dynamic_attribute("show_temporal_variance").drive(self.__set_show_temporal_variance)
        self.__profile_data.dynamic_attribute("focus_point").drive(self.__set_focus_line_pos)

    @property
    def computed_values(self):
        return self.__profile_data.computed_values

    @property
    def scatter_item(self):
        return self.__scatter_item
    @property
    def spatial_error_item(self):
        return self.__spatial_error_item
    @property
    def temporal_error_item(self):
        return self.__temporal_error_item

    @Qt.Slot()
    def __on_focus_dragged(self):
        values = self.__profile_data.values_2d
        if values is None:
            return
        xs, _ = values
        i = int(self.__focus_line.getPos()[0])
        self.__profile_data.focus_point = max(0.0, min(1.0, i / (len(xs)-1)))

    @Qt.Slot()
    def __set_color(self, color):
        self.scatter_item.setPen(color)
        self.scatter_item.setSymbolPen(color)
        self.scatter_item.setBrush(color)
        self.scatter_item.setSymbolBrush(color)
        muted_color = Qt.QColor(color)
        muted_color.setAlpha(96)
        self.spatial_error_item.setBrush(muted_color)
        self.temporal_error_item.setBrush(muted_color)
        self.__focus_line.setPen(color)

    @Qt.Slot()
    def __set_show_spatial_variance(self, show_variance):
        self.spatial_error_item.setVisible(show_variance)
    @Qt.Slot()
    def __set_show_temporal_variance(self, show_variance):
        self.temporal_error_item.setVisible(show_variance)

    @Qt.Slot()
    def __set_focus_line_pos(self, focus_point):
        values = self.__profile_data.values_2d
        if values is None:
            return
        xs, _ = values
        index = int(focus_point * (len(xs)-1))
        self.__focus_line.setPos(index)

    @Qt.Slot()
    def __update_temporal_plot(self, values):
        if values is not None:
            xs, ys, temp_var = values
            temp_stddev = np.sqrt(temp_var)
            self.__temporal_std_curve_low.setData(xs, ys - temp_stddev)
            self.__temporal_std_curve_high.setData(xs, ys + temp_stddev)

    @Qt.Slot()
    def __update_plot(self, values):
        if values is not None:
            xs, ys, spatial_var = values
            self.scatter_item.setData(x = xs, y = ys)
            spatial_std_dev = np.sqrt(spatial_var)
            self.__spatial_std_curve_low.setData(xs, ys - spatial_std_dev)
            self.__spatial_std_curve_high.setData(xs, ys + spatial_std_dev)

class ProfilePlotWidget2D(pyqtgraph.PlotWidget):
    def __init__(self):
        super().__init__()
        self.__item = None
    def set_item(self, item):
        self.clear()
        self.__item = item
        if item is not None:
            for sub_item in item.items:
                self.addItem(sub_item)

def ProfileDataItem3D(profile_data):
    return profile_data
class ProfilePlotWidget3D(GLWidget):
    def __init__(self):
        super().__init__(ProfileScene(None))

    def set_item(self, item):
        self.scene.profile_data = item

class SpatialPlotWidget(Qt.QWidget):
    class ChildrenOfInterest:
        def __init__(self):
            self.plot_widget: pyqtgraph.PlotWidget
            self.profile_chooser: ItemChooser
            self.lock_axes_checkbox: Qt.QCheckBox
            self.export_button: Qt.QPushButton
            self.show_spatial_stddev_checkbox: Qt.QCheckBox
            self.show_temporal_stddev_checkbox: Qt.QCheckBox
            self.compute_progress: ComputedProgressBar
            self.reference_chooser: ItemChooser
            self.view_mode: Qt.QCheckBox
            self.plot_container: Qt.QWidget

    def __init__(self, selected_band, points, profiles):
        super().__init__()
        self.__selected_band = selected_band
        self.__points = points
        self.__profiles = profiles
        self.__profiles.endInsertRange.connect(self.__on_insert_profiles)
        self.__profiles.endRemoveRange.connect(self.__on_remove_profiles)
        self.__profiles.endReplaceRange.connect(self.__on_replace_profiles)
        self.__reference_data = PointData(self.__selected_band, None)
        self.__lock_axes = False
        self.__profile_data = [self.__make_profile_data(p) for p in self.__profiles]
        self._current_profile_data = None
        self.ProfileDataItem = ProfileDataItem2D
        self.widgets = self.ChildrenOfInterest()

        skel = Container(Qt.QVBoxLayout, (), [
            Container(Qt.QHBoxLayout, (), [
                Container(Qt.QStackedLayout, (), [
                    Leaf(ProfilePlotWidget2D, (), id="plot_widget_2d"),
                    Leaf(ProfilePlotWidget3D, (), id="plot_widget_3d")
                ], id="plot_container"),
                Container(Qt.QVBoxLayout, (), [
                    Leaf(Qt.QCheckBox, ("Lock Axes", ), id="lock_axes_checkbox"),
                    icon_with_label("insarviz:profile.png", "Profile"),
                    (Leaf(ItemChooser, (self.__profiles,), id="profile_chooser"), {"stretch": 1}),
                    Leaf(Qt.QCheckBox, ("Show spatial deviation", ), id="show_spatial_stddev_checkbox"),
                    Leaf(Qt.QCheckBox, ("Show temporal deviation", ), id="show_temporal_stddev_checkbox"),
                    icon_with_label("insarviz:points.png", "Reference"),
                    Leaf(ItemChooser, (self.__points,), id="reference_chooser"),
                    icon_with_label("insarviz:logo_insarviz.png", "View Mode"),
                    Leaf(Qt.QCheckBox, ("3D View (experimental)",), id="view_mode"),
                    Leaf(Qt.QSpinBox, (), id="smoothing_factor"),
                    (Leaf(Qt.QWidget, ()), {"stretch": 1}),
                    Leaf(Qt.QPushButton, ("Export...",), id="export_button"),
                ]),

            ]),
            Leaf(ComputedProgressBar, (), id="compute_progress")
        ])
        skel.create_in(self, self.widgets)

        self.widgets.smoothing_factor.valueChanged.connect(self.__on_smoothing_changed)
        self.widgets.smoothing_factor.setEnabled(False)
        self.widgets.view_mode.setChecked(False)
        self.widgets.view_mode.checkStateChanged.connect(self.__set_view_mode)
        self.widgets.profile_chooser.current_item_changed.connect(self.__on_profile_selected)
        self.widgets.lock_axes_checkbox.checkStateChanged.connect(self.__on_lock_axes)
        self.widgets.export_button.clicked.connect(self.__export)
        self.widgets.show_spatial_stddev_checkbox.checkStateChanged.connect(self.__on_show_spatial_error)
        self.widgets.show_temporal_stddev_checkbox.checkStateChanged.connect(self.__on_show_temporal_error)
        self.widgets.reference_chooser.current_item_changed.connect(self.__on_reference_selected)
        self.widgets.plot_widget = self.widgets.plot_widget_2d
        self.__dynamic_units = SELF.dataset.value_units[self.__selected_band]
        self.__dynamic_units.drive(lambda units: self.widgets.plot_widget_2d.setLabel('left', f"LOS displacement ({units})" if units is not None else "No units"))
        self.widgets.plot_widget_2d.setLabel('bottom', "Distance along profile (px)")
        self.widgets.plot_widget_2d.setBackground('w')
        self.widgets.plot_widget_2d.setForegroundBrush(Qt.Qt.GlobalColor.transparent)

        self.__auto_range()

    def __auto_range(self):
        self.widgets.plot_widget.autoRange()
        if self.__lock_axes:
            self.widgets.plot_widget.disableAutoRange()
        else:
            self.widgets.plot_widget.enableAutoRange()

    @Qt.Slot()
    def __export(self):
        self.__export_dialog = exportDialog.ExportDialog(self.widgets.plot_widget_2d.plotItem.scene())
        self.__export_dialog.show(self.widgets.plot_widget_2d)

    def __make_profile_data(self, profile):
        return ProfileData(self.__selected_band, profile, self.__reference_data)

    @Qt.Slot(Any)
    def __on_show_spatial_error(self, checked):
        show_bars = checked == Qt.Qt.Checked
        if show_bars:
            self.widgets.show_temporal_stddev_checkbox.setChecked(False)
        p_data = self._current_profile_data
        if p_data is not None:
            p_data.show_spatial_variance = show_bars
            self.__auto_range()
    @Qt.Slot(Any)
    def __on_show_temporal_error(self, checked):
        show_bars = checked == Qt.Qt.Checked
        if show_bars:
            self.widgets.show_spatial_stddev_checkbox.setChecked(False)
        p_data = self._current_profile_data
        if p_data is not None:
            p_data.show_temporal_variance = show_bars
            self.__auto_range()
    @Qt.Slot()
    def __on_smoothing_changed(self):
        if self._current_profile_data is not None:
            self._current_profile_data.smoothing_factor = self.widgets.smoothing_factor.value()
    @Qt.Slot()
    def __set_view_mode(self):
        if self.widgets.view_mode.isChecked():
            self.ProfileDataItem = ProfileDataItem3D
            self.widgets.plot_widget = self.widgets.plot_widget_3d
        else:
            self.ProfileDataItem = ProfileDataItem2D
            self.widgets.plot_widget = self.widgets.plot_widget_2d

        self.widgets.plot_container.layout().setCurrentWidget(self.widgets.plot_widget)
        self.__update_profile_widget()

    @Qt.Slot(Any)
    def __on_lock_axes(self, checked):
        self.__lock_axes = checked == Qt.Qt.Checked
        self.__auto_range()

    @Qt.Slot(int, int)
    def __on_insert_profiles(self, start, length):
        self.__profile_data[start:start] = [
            self.__make_profile_data(p)
            for p in self.__profiles[start:start+length]
        ]
    @Qt.Slot(int,int)
    def __on_remove_profiles(self, start, end):
        self.__profile_data[start:end] = []
    @Qt.Slot(int,int)
    def __on_replace_profiles(self, start, end):
        self.__profile_data[start:end] = [
            self.__make_profile_data(p)
            for p in self.__profiles[start:end]
        ]

    @Qt.Slot(int, Any)
    def __on_reference_selected(self, _, ref_point):
        self.__reference_data.set_point(ref_point)

    def __update_profile_widget(self):
        if self._current_profile_data is not None:
            profile_item = self.ProfileDataItem(self._current_profile_data)
            self.widgets.plot_widget.set_item(profile_item)
            self.widgets.compute_progress.set_computed_value(profile_item.computed_values)
        else:
            self.widgets.plot_widget.set_item(None)

    @Qt.Slot(int, Any)
    def __on_profile_selected(self, profile_index, profile):
        if profile is None:
            self._current_profile_data = None
            self.widgets.compute_progress.set_computed_value(None)
            self.widgets.smoothing_factor.setEnabled(False)
        else:
            self._current_profile_data = self.__profile_data[profile_index]
            self.widgets.smoothing_factor.setEnabled(True)
            self.widgets.smoothing_factor.setValue(self._current_profile_data.smoothing_factor)
            self.widgets.show_spatial_stddev_checkbox.setChecked(profile.show_spatial_variance)
            self.widgets.show_temporal_stddev_checkbox.setChecked(profile.show_temporal_variance)
        self.__update_profile_widget()
