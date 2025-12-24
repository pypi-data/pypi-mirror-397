from ..__prelude__ import *

from ..shaders import Shader, PureShader
from ..misc import Qt, Matrix, Point, DEMTexture, Bound, ComputedValue, linmap, bresenham, Base10Increments, GLProgram, unit_square_to_image

def inOpenGLContext(function, context = None):
    if context is None:
        context = Qt.QOpenGLContext.globalShareContext()
    current = Qt.QOpenGLContext.currentContext()
    surface = current.surface()
    context.makeCurrent(surface)
    ret = function()
    if current is not None:
        current.makeCurrent(surface)
    return ret
