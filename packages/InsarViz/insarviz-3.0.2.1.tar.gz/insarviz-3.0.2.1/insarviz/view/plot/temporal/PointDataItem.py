from typing import Any
import pyqtgraph
import numpy as np
import rasterio.windows
import datetime
import math

from .__prelude__ import (
    logger, Qt, PointData
)
from .FitCurveItem import FitCurveItem

def set_all_pens(item, pen):
    item.setPen(pen)
    item.setSymbolPen(pen)
    item.setBrush(pen)
    item.setSymbolBrush(pen)

class PointDataItem(pyqtgraph.PlotItem):
    def __init__(self, point_data, reference_data):
        super().__init__()
        self.__point_data = point_data
        self.__point_data.fieldChanged.connect(self.__on_point_data_changed)
        self.__point_data.dynamic_attribute("seasonal_period").value_changed.connect(self.__on_period_changed)
        self.__reference_data = reference_data
        self.__reference_data.fieldChanged.connect(self.__on_reference_data_changed)

        self.__selected_band = point_data.selected_band

        self.__fit_item = FitCurveItem(point_data.point_curve.full_curve)
        point_data.point_curve.fieldChanged.connect(self.__on_fit_changed)
        def on_finished(est):
            curve = point_data.point_curve.full_curve
            param_map = {param.name: value for param, value in zip(curve.params, est._current_params)}
            if "step" in param_map:
                step_timestamp = self.fit_item.to_x(param_map["step"])
                step_date = datetime.datetime.fromtimestamp(step_timestamp).strftime('%Y-%m-%d')
                logger.debug("Finished params. Seism at %s", step_date)
        self.fit_item.finished_estimate.connect(on_finished)

        self.__error_bar_low = pyqtgraph.PlotCurveItem(connect='finite', pen = point_data.color)
        self.__error_bar_high = pyqtgraph.PlotCurveItem(connect='finite', pen = point_data.color)
        self.__error_bar_item = pyqtgraph.FillBetweenItem(self.__error_bar_low, self.__error_bar_high, brush = point_data.color)
        self.error_bar_item.setZValue(-1.0)
        self.error_bar_item.setVisible(point_data.show_variance)

        self.__scatter_item = pyqtgraph.PlotDataItem(symbolPen = point_data.color, pen = point_data.color, symbolBrush = point_data.color, brush = point_data.color)
        self.scatter_item.scatter.setData(hoverable = True)
        self.scatter_item.sigPointsClicked.connect(self.__on_points_clicked)

        self.addItem(self.scatter_item)
        self.addItem(self.fit_item)
        self.addItem(self.error_bar_item)

        self.scatter_item.setVisible(point_data.show_in_plot)
        self.fit_item.setVisible(point_data.show_in_plot)
        self.__set_color(point_data.color)
        self.__update_plot()
        self.__on_period_changed(1.0)

    @property
    def sigPointsHovered(self):
        return self.scatter_item.sigPointsHovered

    @property
    def scatter_item(self):
        return self.__scatter_item
    @property
    def fit_item(self):
        return self.__fit_item
    @property
    def error_bar_item(self):
        return self.__error_bar_item
    @property
    def point_data(self):
        return self.__point_data

    def __set_color(self, color):
        set_all_pens(self.scatter_item, color)
        set_all_pens(self.fit_item, color)
        muted_color = Qt.QColor(color)
        muted_color.setAlpha(96)
        self.error_bar_item.setBrush(muted_color)

    def __update_plot(self):
        xs, ys = self.__point_data.point_values
        _, ys_ref = self.__reference_data.point_values
        ys_adjusted = ys-ys_ref
        if xs.shape == ys_adjusted.shape:
            self.scatter_item.setData(x = xs, y = ys_adjusted, connect='finite')
            height = np.sqrt(self.__point_data.point_variance)
            has_data = ~np.isnan(ys_adjusted)
            self.__error_bar_low.setData(xs[has_data], (ys_adjusted - height)[has_data])
            self.__error_bar_high.setData(xs[has_data], (ys_adjusted + height)[has_data])
            self.fit_item.set_fit_points(xs, ys_adjusted)
            if not self.__point_data.point.point_curve.is_empty:
                self.fit_item.start_fit()

    @Qt.Slot(str, Any)
    def __on_point_data_changed(self, field):
        if field == "show_in_plot":
            self.scatter_item.setVisible(self.__point_data.point.show_in_plot)
            self.fit_item.setVisible(self.__point_data.point.show_in_plot)
            self.error_bar_item.setVisible(self.__point_data.point.show_variance and self.__point_data.point.show_in_plot)
        if field == "show_variance":
            self.error_bar_item.setVisible(self.__point_data.point.show_variance and self.__point_data.point.show_in_plot)
        if field == "color":
            self.__set_color(self.__point_data.point.color)
        if field == "point_values":
            self.__update_plot()

    @Qt.Slot(float)
    def __on_period_changed(self, old):
        p_curve = self.__point_data.point.point_curve
        period = self.__point_data.seasonal_period
        p_curve.seasonal_curve.period = period
        p_curve.semi_seasonal_curve.period = period / 2.0

    @Qt.Slot(str, Any)
    def __on_reference_data_changed(self, field):
        if field == "point_values":
            self.__update_plot()

    @Qt.Slot(str, Any)
    def __on_fit_changed(self, field):
        if field == "full_curve":
            p_curve = self.__point_data.point.point_curve
            self.fit_item.set_curve(p_curve.full_curve)
            if p_curve.is_empty:
                self.fit_item.setData()
            else:
                self.fit_item.start_fit()

    @Qt.Slot(Any, Any)
    def __on_points_clicked(self, _a, points):
        if len(points) > 0:
            self.__selected_band.band_number = int(points[0].index())
