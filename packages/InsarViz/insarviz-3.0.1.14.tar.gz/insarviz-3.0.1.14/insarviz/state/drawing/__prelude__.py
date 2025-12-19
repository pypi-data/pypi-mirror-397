import ctypes
from OpenGL import GL
import numpy as np
from shiboken6 import VoidPtr

from ..__prelude__ import *

from ..observable    import (
    dynamic,
    ObservableStruct, ObservableList, SELF, EACH,
)
from ..SelectedBand  import SelectedBand
from ..MapPoint      import MapPoint
from ..MapProfile    import MapProfile
from ..ColorMap      import ColorMap, colormaps
from ..Dataset       import Dataset

def destroy_texture(tex):
    if tex is not None:
        tex.destroy()

class OpenGLPainter:
    def __init__(self, width, height):
        self._device = Qt.QOpenGLPaintDevice(width, height)
        self._painter = Qt.QPainter(self._device)
        self._painter.translate(0.0, height)
        self._painter.scale(1.0,-1.0)

    def __enter__(self):
        return self._painter
    def __exit__(self, *__args__):
        self._painter.end()
