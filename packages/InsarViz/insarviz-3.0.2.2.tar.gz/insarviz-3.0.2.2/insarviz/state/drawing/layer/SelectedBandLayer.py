from OpenGL import GL
import numpy as np

from .__prelude__ import (Qt, dynamic, SELF, Matrix, destroy_texture)
from .Layer import Layer, InitializedLayer

SELECTED_BAND_SHADER = """
#version 330

uniform sampler2D {texture};
uniform sampler2D {reference_texture};
uniform sampler1D {colormap};
uniform float {opacity};
uniform mat3 {geo_to_texture};
uniform mat2 {value_to_color};
uniform float {dem_scale};

float {geo_height}(vec3 geo_coords) {{
   vec3 image_coords = {geo_to_texture} * geo_coords;
   vec4 value = texture({texture}, image_coords.xy / image_coords.z);
   vec4 ref_value = texture({reference_texture}, image_coords.xy / image_coords.z);
   value -= ref_value * ref_value.w;
   return clamp(-value.x * {dem_scale}, -1, 1);
}}

vec4 {geo_color}(vec3 geo_coords, inout float up_opacity) {{
  vec3 image_coords = {geo_to_texture} * geo_coords;
  vec4 value = texture({texture}, image_coords.xy / image_coords.z);
  vec4 ref_value = texture({reference_texture}, image_coords.xy / image_coords.z);
  value.xyz -= ref_value.xyz * ref_value.w;
  vec2 colormap_index = {value_to_color} * vec2(value.x, 1.0);
  vec4 color = texture({colormap}, colormap_index.x / colormap_index.y);
  return vec4(color.xyz, value.w*{opacity}*up_opacity);
}}
"""

class SelectedBandLayer(Layer):
    is_removable = False

    colormap       = dynamic.readonly()
    selected_band  = dynamic.readonly()
    shaders        = dynamic.readonly()
    opacity        = dynamic.variable(1.0)
    is_enabled     = dynamic.variable(True)
    dem_weight     = dynamic.variable(1.0)

    def __init__(self, selected_band, colormap):
        super().__init__()
        self._selected_band: SelectedBand = selected_band
        self._colormap: ColorMap = colormap
        self._shaders = [
            SELECTED_BAND_SHADER.format(
                **self.local_idents("geo_color", "geo_height", "texture", "reference_texture", "colormap", "opacity", "geo_to_texture", "value_to_color", "dem_scale")
            )
        ]

        self.dynamic_attribute("_redraw").value_changed.connect(lambda: self._redraw())


    @dynamic.memo(SELF.selected_band.image_to_crs)
    def geo_to_image(self):
        return self.selected_band.image_to_crs.inverse()

    @dynamic.method(SELF.colormap.createTexture, SELF.colormap.value_to_color,
                    SELF.selected_band.texture,
                    SELF.selected_band.reference_texture,
                    SELF.opacity, SELF.is_enabled, SELF.dem_weight, SELF.value_scale)
    def _redraw(self):
        self.renderChanged.emit()

    @dynamic.memo(SELF.selected_band.image)
    def value_scale(self):
        img = np.where(self.selected_band.image[:,:,3] > 0.5, self.selected_band.image[:,:,0], np.nan)
        a, b = np.nanquantile(img, 0.02), np.nanquantile(img, 0.98)
        sc = max(abs(a), abs(b))
        if sc == 0.0:
            return 1
        else:
            return 1/sc

    def GL_initialize(self, context: Qt.QOpenGLContext, /):
        return InitializedSelectedBandLayer(context, self)

    __mime_type__ = "x-application/insarviz/SelectedBandLayer"
    @classmethod
    def can_from_mime(cls, mimeData, **kwargs):
        return super().can_from_mime(mimeData, **kwargs) and 'selected_band' in kwargs
    @staticmethod
    def from_dict(dct, selected_band = None, colormap = None, **__kwargs__):
        ret = SelectedBandLayer(selected_band, colormap)
        ret.opacity = dct['opacity']
        ret.is_enabled = dct.get('is_enabled', True)
        ret.dem_weight = dct.get('dem_weight', 0.0)
        return ret
    def to_dict(self):
        return {
            "opacity": self.opacity,
            "is_enabled": self.is_enabled,
            "dem_weight": self.dem_weight,
        }

class InitializedSelectedBandLayer(InitializedLayer):
    def __init__(self, context, band_layer):
        super().__init__(context, band_layer)

    @dynamic.memo(SELF.layer.colormap.createTexture,
                     destroy = destroy_texture)
    def GL_colormap_texture(self):
        return self.layer.colormap.createTexture()

    @dynamic.memo(
        SELF.layer.selected_band.texture, SELF.layer.selected_band.reference_texture,
        SELF.GL_colormap_texture,
        SELF.layer.opacity, SELF.layer.colormap.value_to_color,
        SELF.layer.geo_to_image, SELF.layer.is_enabled, SELF.layer.value_scale
    )
    def GL_setup(self):
        tex = self.layer.selected_band.texture
        ref_tex = self.layer.selected_band.reference_texture
        colormap = self.GL_colormap_texture
        def doit(program):
            uni = self.local_uniforms(program.uniforms)
            uni.texture = tex
            uni.reference_texture = ref_tex
            uni.colormap = colormap
            uni.opacity = self.layer.opacity if self.layer.is_enabled else 0.0
            uni.geo_to_texture = self.layer.geo_to_image
            uni.value_to_color = self.layer.colormap.value_to_color
            uni.dem_scale = float(self.layer.dem_weight * self.layer.value_scale)
        return doit

    def GL_free(self):
        self.dynamic_attribute("GL_colormap_texture").clear()
        self.dynamic_attribute("GL_setup").clear()
