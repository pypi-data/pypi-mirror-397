from ..__prelude__ import *

from ..misc import Qt, Matrix, Point, bresenham, ComputedValue, linmap, GLOBAL_THREAD_POOL, Runnable
from ..state import (
    ObservableList, ObservableStruct, WindowState, MaybeBandNumber,
    colormaps, Dataset,
    LinearCurve, SigmoidCurve, PeriodicCurve, CurveSum, CurveParam, CurveEstimate,
    MapPoint, PointCurve, PointData,
    MapProfile, ProfileData, FocusPoint,
    MapScene, Scene, ProfileScene,
    GeoScene,
    Layer, SwipeLayer, PointsLayer, SelectedBandLayer, RasterLayer, RasterRGBLayer,
    SELF, EACH,
)

def color_icon(color):
    pix = Qt.QPixmap(16, 16)
    pix.fill(color)
    return Qt.QIcon(pix)
