import numpy as np

from .__prelude__ import (
    Qt, PureShader, Matrix, ColorMap, colormaps,
    dynamic, SELF,
    Dataset, destroy_texture
)
from .Layer import Layer, InitializedLayer

RASTER_SHADER = """
#version 400

uniform sampler2D {image};
uniform sampler1D {colormap};
uniform mat3 {geo_to_image};
uniform mat2 {value_to_color};
uniform float {opacity};
uniform float {height_scale};
uniform float {height_mean};

float {geo_height}(vec3 geo_coords) {{
   vec3 image_coords = {geo_to_image}*geo_coords;
   vec4 value = texture({image}, image_coords.xy / image_coords.z);
   return fma(value.x, {height_scale}, -{height_mean});
}}

vec4 {geo_color}(vec3 geo_coords, inout float up_opacity) {{
   vec3 image_coords = {geo_to_image}*geo_coords;
   vec4 value = texture({image}, image_coords.xy / image_coords.z);
   vec2 color_index = {value_to_color} * vec2(value.x, 1.0);
   vec4 color = texture({colormap}, color_index.x / color_index.y);
   return vec4(color.xyz, {opacity}*up_opacity*value.y);
}}
"""

class RasterLayer(Layer):
    colormap      = dynamic.variable()
    opacity       = dynamic.variable(1.0)
    is_enabled    = dynamic.variable(True)
    image         = dynamic.readonly()
    shaders       = dynamic.readonly()
    geo_to_image  = dynamic.readonly()
    dataset       = dynamic.readonly()
    band_number   = dynamic.readonly()
    dem_weight    = dynamic.variable(0.0)

    def __init__(self, dataset, band_number):
        super().__init__()
        self._dataset = dataset
        self._band_number = band_number
        self._image = dataset.read(band_number+1, masked=True)
        w,h = dataset.size
        self._geo_to_image = Matrix.product(
            dataset.pixel_to_crs,
            Matrix.scale((w,h,1))
        ).inverse()
        self._shaders = [
            RASTER_SHADER.format(
                **self.local_idents("image", "geo_to_image", "geo_color", "geo_height", "height_scale", "height_mean", "colormap", "opacity", "value_to_color")
            )
        ]
        self.colormap = ColorMap("grey", np.array(colormaps["grey"]) * 255.0)
        self.colormap.image_histogram = self.image_histogram

        self.dynamic_attribute("_redraw").value_changed.connect(lambda: self._redraw())

    @dynamic.method(SELF.colormap.value_to_color, SELF.colormap.createTexture, SELF.opacity, SELF.is_enabled, SELF.dem_weight)
    def _redraw(self):
        self.renderChanged.emit()

    @dynamic.memo(SELF.image)
    def image_histogram(self):
        img = self.image
        hist, bins = np.histogram(img.data[~img.mask], bins='fd', density=True)
        return (hist, bins)

    @dynamic.memo(SELF.image)
    def height_scale(self):
        a,b = np.nanquantile(self.image.data, 0.05, axis = None), np.nanquantile(self.image.data, 0.95, axis = None)
        return 1/max(abs(a), abs(b))
    @dynamic.memo(SELF.image, SELF.height_scale)
    def height_mean(self):
        return np.nanmean(self.image.data) * self.height_scale

    def GL_initialize(self, context):
        return InitializedRasterLayer(context, self)

    @property
    def description(self):
        return f"File: .../{self.dataset.file.name}"

    __mime_type__ = "x-application/insarviz/RasterLayer"
    @staticmethod
    def from_dict(dct, **__kwargs__):
        ret = RasterLayer(Dataset(dct["dataset"]), dct["band_number"])
        ret.opacity = dct['opacity']
        ret.is_enabled = dct.get('is_enabled', True)
        ret.colormap.init_from_dict(dct["colormap"])
        ret.dem_weight = dct.get('dem_weight', 0.0)
        return ret
    def to_dict(self):
        return {
            "opacity": self.opacity,
            "is_enabled": self.is_enabled,
            "dataset": str(self.dataset.file),
            "band_number": self.band_number,
            "colormap": self.colormap.to_dict(),
            "dem_weight": self.dem_weight,
        }

class InitializedRasterLayer(InitializedLayer):
    def __init__(self, context, layer):
        super().__init__(context, layer)

    @dynamic.memo(SELF.layer.image,
                     destroy = destroy_texture)
    def GL_texture(self):
        texture = Qt.QOpenGLTexture(Qt.QOpenGLTexture.Target.Target2D)
        img = self.layer.image
        h, w = img.shape
        texture.setWrapMode(Qt.QOpenGLTexture.ClampToBorder)
        texture.setBorderColor(Qt.QColor(0,0,0,0))
        texture.setSize(w,h)
        texture.setFormat(Qt.QOpenGLTexture.TextureFormat.RG32F)
        texture.allocateStorage(Qt.QOpenGLTexture.PixelFormat.RG, Qt.QOpenGLTexture.PixelType.Float32)
        texture_data = np.stack([
            img.data,
            np.where(img.mask, 0.0, 1.0)
        ], axis=-1).astype(np.float32)
        texture.setData(Qt.QOpenGLTexture.PixelFormat.RG, Qt.QOpenGLTexture.PixelType.Float32, texture_data)
        texture.create()
        return texture

    @dynamic.memo(SELF.layer.colormap.createTexture,
                     destroy = destroy_texture)
    def GL_colormap_texture(self):
        return self.layer.colormap.createTexture()

    @dynamic.memo(SELF.GL_texture, SELF.GL_colormap_texture,
                  SELF.layer.opacity, SELF.layer.colormap.value_to_color,
                  SELF.layer.is_enabled, SELF.layer.height_scale, SELF.layer.dem_weight)
    def GL_setup(self):
        image_texture = self.GL_texture
        colormap_texture = self.GL_colormap_texture
        def doit(program):
            uni = self.local_uniforms(program.uniforms)
            uni.image           = image_texture
            uni.colormap        = colormap_texture
            uni.value_to_color  = self.layer.colormap.value_to_color
            uni.opacity         = self.layer.opacity if self.layer.is_enabled else 0.0
            uni.geo_to_image    = self.layer.geo_to_image
            uni.height_scale    = float(self.layer.height_scale * self.layer.dem_weight)
            uni.height_mean     = float(self.layer.height_mean * self.layer.dem_weight)
        return doit

    def GL_free(self):
        self.dynamic_attribute("GL_setup").clear()
        self.dynamic_attribute("GL_texture").clear()
        self.dynamic_attribute("GL_colormap_texture").clear()
