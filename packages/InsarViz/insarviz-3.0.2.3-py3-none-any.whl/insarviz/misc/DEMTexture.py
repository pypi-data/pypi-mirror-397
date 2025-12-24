from typing import override
import numpy as np
from . import Qt, Matrix
from OpenGL import GL

def unit_square_to_image(w, h):
    hfactor = max(float(h)/float(w), 1.0)
    vfactor = max(float(w)/float(h), 1.0)
    return Matrix.product(
        Matrix.translate((0.5,0.5)),
        Matrix.scale((hfactor, vfactor, 1.0)),
        Matrix.scale((0.5,-0.5,1.0))
    )

class DEMTexture(Qt.QOpenGLTexture):
    def __init__(self, image):
        super().__init__(Qt.QOpenGLTexture.Target.Target2D)
        self.image = image
        h, w, _ = self.image.shape
        self.texture_to_image = Matrix.product(
            unit_square_to_image(w, h),
            Matrix.translate((-1,-1)),
            Matrix.scale((2,2,1))
        )

    def create(self):
        if self.image is not None:
            self.setMagnificationFilter(Qt.QOpenGLTexture.Filter.Linear)
            self.setMinificationFilter(Qt.QOpenGLTexture.Filter.LinearMipMapLinear)
            self.setWrapMode(Qt.QOpenGLTexture.WrapMode.ClampToBorder)
            self.setBorderColor(Qt.QColor(0.0,0.0,0.0,0.0))

            h, w, _ = self.image.shape
            self.setSize(w, h)

            self.setFormat(Qt.QOpenGLTexture.TextureFormat.RGBA32F)
            self.allocateStorage(Qt.QOpenGLTexture.PixelFormat.RGBA, Qt.QOpenGLTexture.PixelType.Float32)
            self.setData(Qt.QOpenGLTexture.PixelFormat.RGBA, Qt.QOpenGLTexture.PixelType.Float32, self.image) #type: ignore
            self.generateMipMaps()

            self.image = None
        return super().create()
