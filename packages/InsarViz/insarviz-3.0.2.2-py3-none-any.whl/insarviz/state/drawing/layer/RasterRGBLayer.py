import numpy as np

from .__prelude__ import (
    Qt, PureShader, Matrix, ColorMap, colormaps,
    dynamic, SELF,
    Dataset, destroy_texture
)
from .Layer import Layer, InitializedLayer

RASTER_SHADER = """
#version 330

uniform sampler2D {image};
uniform mat3 {geo_to_image};
uniform float {opacity};

float {geo_height}(vec3 geo_coords) {{
   return 0.0;
}}

vec4 {geo_color}(vec3 geo_coords, inout float up_opacity) {{
   vec3 image_coords = {geo_to_image}*geo_coords;
   vec4 value = texture({image}, image_coords.xy / image_coords.z);
   return vec4(value.xyz, {opacity}*up_opacity*value.w);
}}
"""

class RasterRGBLayer(Layer):
    opacity       = dynamic.variable(1.0)
    is_enabled    = dynamic.variable(True)
    image         = dynamic.readonly()
    geo_to_image  = dynamic.readonly()
    shaders       = dynamic.readonly()
    dataset       = dynamic.readonly()

    def __init__(self, dataset):
        super().__init__()
        self._dataset = dataset
        w,h = dataset.size
        first_band = dataset.read(1)
        self._image = np.reshape(
            np.stack([
                first_band,
                dataset.read(2),
                dataset.read(3),
                np.ones_like(first_band) * 255,
            ], axis=-1).astype(np.float32),
            (h,w,4)
        ) / 255.0
        self._geo_to_image = Matrix.product(
            dataset.pixel_to_crs,
            Matrix.scale((w,h,1))
        ).inverse()

        self._shaders = [
            RASTER_SHADER.format(
                **self.local_idents("image", "geo_to_image", "geo_color", "geo_height", "opacity")
            )
        ]
        self.dynamic_attribute("_redraw").value_changed.connect(lambda: self._redraw())

    @dynamic.method(SELF.opacity, SELF.is_enabled)
    def _redraw(self):
        self.renderChanged.emit()

    @property
    def description(self):
        return f"File: .../{self.dataset.file.name}"

    def GL_initialize(self, context):
        return InitializedRasterRGBLayer(context, self)

    __mime_type__ = "x-application/insarviz/RasterRGBLayer"
    @staticmethod
    def from_dict(dct, **__kwargs__):
        ret = RasterRGBLayer(Dataset(dct["dataset"]))
        ret.opacity = dct['opacity']
        ret.is_enabled = dct.get('is_enabled', True)
        return ret
    def to_dict(self):
        return {
            "opacity": self.opacity,
            "is_enabled": self.is_enabled,
            "dataset": str(self.dataset.file),
        }

class InitializedRasterRGBLayer(InitializedLayer):
    def __init__(self, context, layer):
        super().__init__(context, layer)

    @dynamic.memo(SELF.layer.image,
                     destroy = destroy_texture)
    def GL_texture(self):
        texture = Qt.QOpenGLTexture(Qt.QOpenGLTexture.Target.Target2D)
        img = self.layer.image
        h, w, _ = img.shape
        texture.setSize(w,h)
        texture.setWrapMode(Qt.QOpenGLTexture.WrapMode.ClampToBorder)
        texture.setBorderColor(Qt.QColor(0,0,0,0))
        texture.setFormat(Qt.QOpenGLTexture.TextureFormat.RGBA32F)
        texture.allocateStorage(Qt.QOpenGLTexture.PixelFormat.RGBA, Qt.QOpenGLTexture.PixelType.Float32)
        texture.setData(Qt.QOpenGLTexture.PixelFormat.RGBA, Qt.QOpenGLTexture.PixelType.Float32, img.data)
        texture.create()
        return texture

    @dynamic.memo(SELF.GL_texture, SELF.layer.opacity, SELF.layer.is_enabled)
    def GL_setup(self):
        image_texture = self.GL_texture
        def doit(program):
            uni = self.local_uniforms(program.uniforms)
            uni.image           = image_texture
            uni.opacity         = self.layer.opacity if self.layer.is_enabled else 0.0
            uni.geo_to_image    = self.layer.geo_to_image
        return doit
