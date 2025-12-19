from typing import Any
import numpy as np
import rasterio.windows
import warnings

from .__prelude__ import Qt, linmap

from .observable import ObservableStruct, dynamic, SELF, Unique
from .curve      import Curve, LinearCurve, SigmoidCurve, PeriodicCurve, CurveSum

def Enablable(SomeCurve):
    class Enablable(SomeCurve):
        is_enabled = dynamic.variable()
        def __init__(self):
            super().__init__()
            self.is_enabled = False

        def init_from_dict(self, dct):
            super().init_from_dict(dct)
            if "is_enabled" in dct:
                self.is_enabled = dct['is_enabled']

        def to_dict(self):
            return dict(super().to_dict(), is_enabled = self.is_enabled)
    return Enablable

class PointCurve(ObservableStruct):
    sigmoid_curve        = dynamic.readonly()
    linear_curve         = dynamic.readonly()
    seasonal_curve       = dynamic.readonly()
    semi_seasonal_curve  = dynamic.readonly()

    def __init__(self):
        super().__init__()
        self._sigmoid_curve        = Enablable(SigmoidCurve)()
        self._linear_curve         = Enablable(LinearCurve)()
        self._seasonal_curve       = Enablable(PeriodicCurve)()
        self._semi_seasonal_curve  = Enablable(PeriodicCurve)()

    __mime_type__ = "application/x-insarviz/PointCurve"
    def to_dict(self):
        return {
            "linear_curve": self.linear_curve.to_dict(),
            "sigmoid_curve": self.sigmoid_curve.to_dict(),
            "seasonal_curve": self.seasonal_curve.to_dict(),
            "semi_seasonal_curve": self.semi_seasonal_curve.to_dict(),
        }
    def init_from_dict(self, dct):
        self.linear_curve.init_from_dict(dct["linear_curve"])
        self.sigmoid_curve.init_from_dict(dct["sigmoid_curve"])
        if "seasonal_curve" in dct:
            self.seasonal_curve.init_from_dict(dct["seasonal_curve"])
        if "semi_seasonal_curve" in dct:
            self.semi_seasonal_curve.init_from_dict(dct["semi_seasonal_curve"])

    def _curves(self):
        return [
            self.sigmoid_curve,
            self.linear_curve,
            self.seasonal_curve,
            self.semi_seasonal_curve,
        ]

    @dynamic.memo(
        SELF.sigmoid_curve.is_enabled,
        SELF.linear_curve.is_enabled,
        SELF.seasonal_curve.is_enabled,
        SELF.semi_seasonal_curve.is_enabled,
    )
    def is_empty(self):
        return not any([curve.is_enabled for curve in self._curves()])

    @dynamic.memo(
        SELF.is_empty,
        SELF.sigmoid_curve.initial_step,
        SELF.seasonal_curve.period,
        SELF.semi_seasonal_curve.period,
    )
    def full_curve(self):
        return CurveSum(*[curve for curve in self._curves() if curve.is_enabled])

class PointData(ObservableStruct):
    selected_band  = dynamic.readonly()
    point          = dynamic.variable()
    color          = dynamic.external()
    point_curve    = dynamic.external()
    show_in_plot   = dynamic.external()
    show_variance  = dynamic.external()

    def __init__(self, selected_band, point):
        super().__init__()
        self._selected_band = selected_band
        self._dynamic_color          = SELF.color[point]
        self._dynamic_point_curve    = SELF.point_curve[point]
        self._dynamic_show_in_plot   = SELF.show_in_plot[point]
        self._dynamic_show_variance  = SELF.show_variance[point]
        self.point = point

    def set_point(self, point):
        self.point = point

    @dynamic.memo(SELF.selected_band.dataset)
    def point_xs(self):
        return np.array(self.selected_band.dataset.band_timestamps)

    @dynamic.memo(SELF.selected_band.dataset, Unique(SELF.point.x), Unique(SELF.point.y), Unique(SELF.point.r))
    def point_ys(self):
        return self.__compute_point_values()

    @dynamic.memo(SELF.point_xs, SELF.point_ys)
    def point_absolute_values(self):
        mean, _ = self.point_ys
        return self.point_xs, mean

    @dynamic.memo(SELF.point_absolute_values, SELF.selected_band.reference_band_number)
    def point_values(self):
        ref = self.selected_band.reference_band_number
        xs,ys = self.point_absolute_values
        if ref is None:
            ref_val = 0
        else:
            ref_val = ys[ref]
        return xs, ys - ref_val

    @dynamic.memo(SELF.point_ys)
    def point_variance(self):
        _, var = self.point_ys
        return var

    @dynamic.memo(SELF.point_xs)
    def fromto_x(self):
        xs = self.point_xs
        return linmap(xs[0], xs[-1])

    @dynamic.memo(SELF.fromto_x, SELF.selected_band.dataset)
    def seasonal_period(self):
        if not self.selected_band.dataset.has_band_dates:
            return 1.0

        from_x, _ = self.fromto_x
        period = from_x(365*24*3600) - from_x(0)
        return period

    def __compute_point_values(self):
        p = self.point
        dataset = self.selected_band.dataset
        if p is None:
            zeros = np.zeros_like(np.array(dataset.band_timestamps))
            return zeros, zeros

        win = rasterio.windows.Window(p.x-p.r, p.y-p.r, 1+2*p.r, 1+2*p.r)
        # Create a mask of circular shape
        mask_row = np.reshape(np.arange(1+2*p.r), (1,1+2*p.r)) - p.r
        mask_col = np.reshape(np.arange(1+2*p.r), (1+2*p.r,1)) - p.r
        mask = np.where(mask_row*mask_row + mask_col*mask_col <= p.r*p.r, 1.0, np.nan)

        samples = dataset.read([i+1 for i in range(dataset.count)],
                               window = win, masked = True)
        masked_samples = np.reshape(np.where(samples.mask, np.nan, samples.data), (dataset.count, *mask.shape)) * mask

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            return np.nanmean(masked_samples, axis=(1,2)), np.nanvar(masked_samples, axis=(1,2))

class MapPoint(ObservableStruct):
    name          = dynamic.variable()
    x             = dynamic.variable()
    y             = dynamic.variable()
    r             = dynamic.variable()
    color         = dynamic.variable()
    show_in_map   = dynamic.variable()
    show_in_plot  = dynamic.variable()
    show_variance = dynamic.variable(False)
    point_curve   = dynamic.variable()
    is_reference  = dynamic.variable(False)

    def __init__(self, name, x, y, r, color, show_in_map = True, show_in_plot = True, point_curve = None, show_variance = False):
        super().__init__()
        self.name = name
        self.x = x
        self.y = y
        self.r = r
        self.color: Qt.QColor = color
        self.show_in_map = show_in_map
        self.show_in_plot = show_in_plot
        self.point_curve = point_curve if point_curve is not None else PointCurve()
        self.show_variance = show_variance

    __mime_type__ = "x-application/insarviz/map-point"
    @staticmethod
    def from_dict(dct: dict):
        args = dict(dct, color = Qt.QColor(dct['color']))
        curve_dict = dct.get("point_curve", None)
        if curve_dict is not None:
            args["point_curve"] = PointCurve.from_dict(curve_dict)
        return MapPoint(**args)
    def to_dict(self):
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "r": self.r,
            "color": self.color.name(),
            "show_in_map": self.show_in_map,
            "show_in_plot": self.show_in_plot,
            "show_variance": self.show_variance,
            "point_curve": self.point_curve.to_dict()
        }

    @dynamic.method(SELF.color, SELF.x, SELF.y, SELF.r, SELF.show_in_map, SELF.is_reference)
    def draw(self, painter, opacity):
        if not self.show_in_map:
            return
        alpha = int(255 * opacity)
        if self.is_reference:
            pen = Qt.QPen(Qt.QColor("red"))
            pen.setWidth(5)
            painter.setPen(pen)
        else:
            if self.color.lightnessF() > 0.5:
                painter.setPen(Qt.QColor(0,0,0,alpha))
            else:
                painter.setPen(Qt.QColor(255, 255, 255, alpha))
        painter.setBrush(Qt.QColor(self.color.red(),self.color.green(),self.color.blue(),alpha))
        painter.drawEllipse(self.x-self.r+1,self.y-self.r+1,2*self.r-2,2*self.r-2)
