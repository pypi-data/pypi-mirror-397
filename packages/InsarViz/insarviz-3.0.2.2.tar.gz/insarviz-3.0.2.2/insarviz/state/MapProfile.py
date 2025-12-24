import math
import numpy as np
import rasterio.windows

from .__prelude__ import Qt, ComputedValue, bresenham

from .observable import ObservableStruct, dynamic, Unique, SELF
from .MapPoint import MapPoint, PointCurve

def _line_coefs(x0, y0, x1, y1):
    dx = x1-x0
    dy = y1-y0
    div = y0*dx-x0*dy
    return (dy, -dx, div)
def _eval_line(line, p):
    a,b,c = line
    x,y = p
    return a*x+b*y+c
def _crosses_line(line, p1, p2):
    return _eval_line(line, p1) * _eval_line(line, p2) < 0
def _segments_intersection(p0, p1, p2, p3):
    """
    Return the intersection of two 2D segments, or None if they don't intersect
    """
    l0 = _line_coefs(*p0, *p1)
    l1 = _line_coefs(*p2, *p3)
    p2_c = _eval_line(l0, p2)
    p3_c = _eval_line(l0, p3)
    if p2_c*p3_c >= 0 or not _crosses_line(l1, p0, p1):
        return None
    x2, y2 = p2
    x3, y3 = p3
    x = (x2*p3_c - x3*p2_c) / (p3_c-p2_c)
    y = (y2*p3_c - y3*p2_c) / (p3_c-p2_c)
    return (x,y)

class MapProfile(ObservableStruct):
    name                    = dynamic.variable()
    x0                      = dynamic.variable()
    y0                      = dynamic.variable()
    end_points              = dynamic.variable()
    r                       = dynamic.variable()
    color                   = dynamic.variable()
    show_in_map             = dynamic.variable()
    show_spatial_variance   = dynamic.variable(False)
    show_temporal_variance  = dynamic.variable(False)
    focus_point             = dynamic.variable(0.5)

    def __init__(self, name, r, color, show_in_map, x0, y0, end_points = []):
        super().__init__()
        self.name = name
        self.x0 = int(x0)
        self.y0 = int(y0)
        self.end_points = end_points
        self.r = r
        self.color = color
        self.show_in_map = show_in_map
        self.dynamic_attribute("show_spatial_variance").value_changed.connect(self.__on_show_spatial_variance)
        self.dynamic_attribute("show_temporal_variance").value_changed.connect(self.__on_show_temporal_variance)

    @Qt.Slot()
    def __on_show_spatial_variance(self):
        if self.show_spatial_variance:
            self.show_temporal_variance = False
    @Qt.Slot()
    def __on_show_temporal_variance(self):
        if self.show_temporal_variance:
            self.show_spatial_variance = False

    __mime_type__ = "x-application/insarviz/map-profile"
    @staticmethod
    def from_dict(dct: dict):
        ret = MapProfile(dct["name"], dct["r"], Qt.QColor(dct["color"]), dct["show_in_map"], dct["x0"], dct["y0"], dct["end_points"])
        ret.show_spatial_variance = dct.get("show_spatial_variance", False)
        ret.show_temporal_variance = dct.get("show_temporal_variance", False)
        ret.focus_point = dct.get("focus_point", 0.5)
        return ret

    def to_dict(self):
        return {
            "name": self.name,
            "x0": self.x0,
            "y0": self.y0,
            "end_points": self.end_points,
            "r": self.r,
            "color": self.color.name(),
            "focus_point": self.focus_point,
            "show_in_map": self.show_in_map,
            "show_spatial_variance": self.show_spatial_variance,
            "show_temporal_variance": self.show_temporal_variance,
        }

    @dynamic.memo(SELF.focus_point)
    def focus_center(self):
        lengths = []
        x0, y0 = self.x0, self.y0
        for x1, y1 in self.end_points:
            lengths.append(max(abs(x1-x0), abs(y1-y0)))
            x0, y0 = x1, y1
        total_length = sum(lengths)
        if total_length == 0:
            return self.x0, self.y0
        focus = self.focus_point
        x0, y0 = self.x0, self.y0
        for l, (x1, y1) in zip(lengths, self.end_points):
            proportion = l / total_length
            if focus <= proportion:
                scale = focus/proportion
                dx, dy = (x1-x0) * scale, (y1-y0)*scale
                return x0+dx, y0+dy
            else:
                focus -= proportion
            x0, y0 = x1, y1
        return x0,y0

    def __normal_segment_vector(self, x0, y0, x1, y1):
        dx, dy = x1-x0, y1-y0
        rxy = math.sqrt(dx*dx+dy*dy)
        if rxy <= 0.00001:
            return 0.0,0.0
        return -dy*self.r/rxy, dx*self.r/rxy

    def __end_of_path(self, x0, y0, x1, y1, x2, y2):
        vx0, vy0 = self.__normal_segment_vector(x0, y0, x1, y1)
        vx1, vy1 = self.__normal_segment_vector(x1, y1, x2, y2)

        inter = _segments_intersection((x0+vx0, y0+vy0), (x1+vx0,y1+vy0),
                                       (x1+vx1, y1+vy1), (x2+vx1,y2+vy1))
        if inter is not None:
            return inter
        else:
            return (x1+vx1, y1+vy1)

    def __path_segment_to(self, path, x0, y0, x1, y1, x2, y2):
        vx0, vy0 = self.__normal_segment_vector(x0, y0, x1, y1)
        vx1, vy1 = self.__normal_segment_vector(x1, y1, x2, y2)

        inter = _segments_intersection((x0+vx0, y0+vy0), (x1+vx0,y1+vy0),
                                       (x1+vx1, y1+vy1), (x2+vx1,y2+vy1))
        if inter is not None:
            path.lineTo(*inter)
        else:
            # Pitfall : angles are the opposite of what they should be,
            # because the y axis goes down instead of up.
            path.lineTo(x1+vx0, y1+vy0)
            v0_angle = math.atan2(vy0, vx0) * 180.0 / math.pi
            v1_angle = math.atan2(vy1, vx1) * 180.0 / math.pi
            dv_angle = v0_angle - v1_angle
            while dv_angle < 0.0:
                dv_angle += 360.0
            path.arcTo(x1-self.r, y1-self.r, 2*self.r, 2*self.r, -v0_angle, dv_angle)

    @dynamic.method(SELF.color, SELF.r, SELF.show_in_map, SELF.focus_center)
    def draw(self, painter, opacity):
        if not self.show_in_map:
            return

        path = Qt.QPainterPath()
        path.setFillRule(Qt.Qt.FillRule.WindingFill)

        # Okay, this bears some explaining.
        #
        # To properly handle transparency, we need to draw the profile
        # as a single path rather than multiple overlapping segments.
        #
        # To do so, we draw a series of "path segments" between all
        # triplets of consecutive center points (p0, p1, p2), going
        # around the profile.
        #
        # For example, if our profile consists of only two points p0
        # and p1, we start at p1, draw a path segment (p1, p0, p1),
        # and a second path segment (p0, p1, p0) to close the loop.
        #
        # Could we have just drawn some opaque circles and rectangles
        # on a pixmap, and blitted the result with some transparency ?
        # Sure, but this way does more math and is, therefore, better.
        if len(self.end_points) == 0:
            return
        point_loop = list((*self.end_points, *reversed(self.end_points[:-1]), (self.x0, self.y0)))
        x0, y0, x1, y1, x2, y2 = *point_loop[-3 % len(point_loop)], *point_loop[-2], *point_loop[-1]
        path.moveTo(*self.__end_of_path(x0, y0, x1, y1, x2, y2))
        x0, y0, x1, y1 = x1, y1, x2, y2
        for x2, y2 in point_loop:
            self.__path_segment_to(path, x0, y0, x1, y1, x2, y2)
            x0, y0, x1, y1 = x1, y1, x2, y2

        alpha = int(255 * opacity)
        pen = Qt.QColor(self.color.red(),self.color.green(),self.color.blue(), alpha)
        painter.setPen(pen)
        painter.setBrush(pen)

        painter.drawPath(path)
        painter.setPen(Qt.QColor("black"))
        if self.focus_center is not None:
            painter.drawEllipse(Qt.QPoint(*self.focus_center), self.r, self.r)

class FocusPoint(MapPoint):
    profile       = dynamic.readonly()
    name          = dynamic.external()
    color         = dynamic.external()
    r             = dynamic.external()
    show_in_plot  = dynamic.variable(True)
    show_variance = dynamic.external()
    point_curve   = dynamic.variable()
    focus         = dynamic.external()

    def __init__(self, profile):
        ObservableStruct.__init__(self)
        self._profile = profile
        self._dynamic_name           = SELF.name[profile]
        self._dynamic_color          = SELF.color[profile]
        self._dynamic_r              = SELF.r[profile]
        self._dynamic_show_variance  = SELF.show_spatial_variance[profile]
        self._dynamic_focus          = SELF.focus_point[profile]
        self.point_curve = PointCurve()

    @dynamic.memo(SELF.profile.focus_center)
    def x(self):
        return self.profile.focus_center[0]
    @dynamic.memo(SELF.profile.focus_center)
    def y(self):
        return self.profile.focus_center[1]

class BoundingBox:
    def __init__(self, minX, minY, maxX, maxY):
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY

    @staticmethod
    def centered_at(x, y, r):
        return BoundingBox(x-r, y-r, x+r, y+r)

    def union(self, bb):
        return BoundingBox(min(self.minX, bb.minX), min(self.minY, bb.minY),
                           max(self.maxX, bb.maxX), max(self.maxY, bb.maxY))
    def values(self):
        return [self.minX, self.minY, self.maxX, self.maxY]

class ProfileData(ObservableStruct):
    smoothing_factor        = dynamic.variable()
    selected_band           = dynamic.readonly()
    reference_data          = dynamic.readonly()
    color                   = dynamic.external()
    profile                 = dynamic.readonly()
    computed_values         = dynamic.readonly()
    show_spatial_variance   = dynamic.external()
    show_temporal_variance  = dynamic.external()
    focus_point             = dynamic.external()

    def __init__(self, selected_band, profile, reference_data):
        super().__init__()
        self._selected_band = selected_band
        self._reference_data = reference_data
        self._profile = profile
        self._dynamic_color = Unique(SELF.profile.color)[self]
        self._dynamic_show_spatial_variance = SELF.profile.show_spatial_variance[self]
        self._dynamic_show_temporal_variance = SELF.profile.show_temporal_variance[self]
        self._dynamic_focus_point = SELF.profile.focus_point[self]
        self._computed_values = ComputedValue((None, None))

        self.__unique_radii = Unique(SELF.profile.r)[self]
        self.__unique_radii.value_changed.connect(lambda: self.computed_values.recompute(self.__get_profile_values))

        self.computed_values.recompute(self.__get_profile_values)
        self.computed_values.ready.connect(self.__on_values_ready)

        self.smoothing_factor = 0

    # Do not reference this in other classes, as it may change unexpectedly
    @dynamic.memo()
    def raw_computed_values(self):
        return self.computed_values.latest()

    @dynamic.memo(
        SELF.reference_data.point_values,
        SELF.selected_band.band_number,
        SELF.selected_band.reference_band_number,
        SELF.raw_computed_values
    )
    def values_and_variance_2d(self):
        values, xs = self.raw_computed_values
        if values is None:
            return None
        ys = values[self.selected_band.band_number, :]

        ref_band = self.selected_band.reference_band_number
        if ref_band is None:
            ref_profile = np.zeros_like(ys[:,0])
        else:
            ref_profile = values[ref_band, :, 0]
        ys_adjusted = ys[:, 0]-ref_profile-self.reference_data.point_values[1][self.selected_band.band_number]
        return xs, ys_adjusted, ys[:, 1]

    @dynamic.memo(SELF.values_and_variance_2d)
    def values_2d(self):
        vals = self.values_and_variance_2d
        if vals is None:
            return None
        xs, ys, _1 = vals
        return xs, ys
    @dynamic.memo(SELF.raw_computed_values)
    def temporal_variance(self):
        values, xs = self.raw_computed_values
        if values is None:
            return None
        return np.nanvar(values[:, :, 0], axis=0)
    @dynamic.memo(SELF.temporal_variance, SELF.values_2d)
    def values_2d_temporal(self):
        vals = self.values_2d
        if vals is None:
            return None
        xs, ys = vals
        return xs, ys, self.temporal_variance

    @dynamic.memo(
        SELF.raw_computed_values,
        SELF.reference_data.point_values,
    )
    def values_3d(self):
        values, ys = self.raw_computed_values
        if values is not None:
            xs, zs_ref = self.reference_data.point_values
            zs = values[:,:,0]-np.reshape(zs_ref, (len(zs_ref), 1))
            return xs, ys, zs
        return np.array([0,1]), np.array([0,1]), np.array([[0,0],[0,0]])

    @Qt.Slot()
    def __on_values_ready(self):
        self.dynamic_attribute("raw_computed_values").invalidate()

    def __get_segment_values(self, x0, y0, x1, y1):
        r = self.profile.r
        minX, minY, maxX, maxY = BoundingBox.centered_at(x0, y0, r).union(BoundingBox.centered_at(x1, y1, r)).values()

        # Create a mask of circular shape
        mask_row = np.reshape(np.arange(2*r+1), (1,2*r+1)) - r
        mask_col = np.reshape(np.arange(2*r+1), (2*r+1,1)) - r
        mask = np.where(mask_row*mask_row + mask_col*mask_col <= r*r, 1.0, 0.0)

        win = rasterio.windows.Window(minX, minY, maxX-minX+1, maxY-minY+1)
        centers = np.array([])
        centers = bresenham.line(x0, y0, x1, y1)
        band_profiles = []
        progress = 0.0
        progress_increment = 1.0 / self.selected_band.dataset.count
        for i in range(self.selected_band.dataset.count):
            band_data = self.selected_band.dataset.read(i+1, window=win)
            band_profile = []

            for (x,y) in centers:
                cx_in_band, cy_in_band = x-minX, y-minY
                data_around_point = band_data[cy_in_band-r:cy_in_band+r+1, cx_in_band-r:cx_in_band+r+1]
                masked_data = mask * data_around_point
                mean = np.nanmean(masked_data)
                var = np.nanvar(masked_data)
                band_profile.append((np.nan if mean == 0.0 else mean, var))
            band_profiles.append(band_profile)
            progress += progress_increment
            yield progress
        return np.array(band_profiles)
    def __get_profile_values(self):
        p = self.profile
        segments = []
        x0, y0 = p.x0, p.y0
        progress_increment = 1.0 / len(self.profile.end_points)
        progress = 0.0
        fmt = "Compute values for profile %s : %%p%%" % self.profile.name
        for x1,y1 in self.profile.end_points:
            new_segment = yield from map(lambda seg_progress: (fmt, progress+progress_increment*seg_progress),
                                         self.__get_segment_values(x0, y0, x1, y1))
            segments.append(new_segment)
            progress += progress_increment
            yield fmt, progress
            x0,y0 = x1, y1
        ret = np.concatenate(segments, axis=1)
        return ret, np.arange(ret.shape[1])
