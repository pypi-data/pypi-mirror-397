import numpy as np
from OpenGL import GL

from .__prelude__ import (
    logger,
    Matrix, Qt, Bound, inOpenGLContext,
    dynamic, SELF, EACH,
    OpenGLPainter, destroy_texture
)
from .Layer import Layer, InitializedLayer, ExistingTexture

POINTS_SHADER = """
#version 330

uniform sampler2D {points_texture};
uniform float {opacity};
uniform mat3 {geo_to_image};

float {geo_height}(vec3 geo_coords) {{
   return 0.0;
}}

vec4 {geo_color}(vec3 geo_coords, inout float up_opacity) {{
  vec3 image_coords = {geo_to_image} * geo_coords;
  vec4 color = texture({points_texture}, image_coords.xy / image_coords.z);
  return vec4(color.xyz, color.w*{opacity}*up_opacity);
}}
"""

class PointsLayer(Layer):
    is_removable = False

    opacity     = dynamic.variable(1.0)
    is_enabled  = dynamic.variable(True)
    dataset     = dynamic.external()
    points      = dynamic.readonly()
    profiles    = dynamic.readonly()
    shaders     = dynamic.readonly()

    point_drawings    = dynamic.external()
    profile_drawings  = dynamic.external()

    def __init__(self, dyn_dataset, points, profiles):
        super().__init__()
        self._dynamic_dataset = dyn_dataset
        self._points: ObservableList[MapPoint] = points
        self._dynamic_point_drawings = (SELF.points / EACH(SELF.draw))[self]
        self._profiles: ObservableList[MapPoint] = profiles
        self._dynamic_profile_drawings = (SELF.profiles / EACH(SELF.draw))[self]

        self._shaders = [
            POINTS_SHADER.format(
                **self.local_idents("geo_color", "geo_height", "points_texture", "geo_to_image", "opacity")
            )
        ]

        self.dynamic_attribute("_redraw").value_changed.connect(lambda: self._redraw())

    @dynamic.method(SELF.dataset, SELF.GL_draw_points_and_profiles)
    def _redraw(self):
        self.renderChanged.emit()

    @dynamic.memo(SELF.dataset)
    def texture_size(self):
        return self.dataset.size
    @dynamic.memo(SELF.dataset, SELF.texture_size)
    def geo_to_image(self):
        w, h = self.texture_size
        return Matrix.product(
            self.dataset.pixel_to_crs,
            Matrix.scale((w,h,1))
        ).inverse()

    @dynamic.method(SELF.opacity, SELF.is_enabled, SELF.point_drawings, SELF.profile_drawings)
    def GL_draw_points_and_profiles(self, painter):
        painter.setPen(Qt.QColor(255, 255, 255))
        for p in self.profiles:
            p.draw(painter, self.opacity)
        for p in self.points:
            p.draw(painter, self.opacity)

    def GL_initialize(self, context):
        return InitializedPointsLayer(context, self)

    __mime_type__ = "x-application/insarviz/PointsLayer"
    @classmethod
    def can_from_mime(cls, mimeData, **kwargs):
        return super().can_from_mime(mimeData, **kwargs) and 'points' in kwargs and 'profiles' in kwargs and 'selected_band' in kwargs
    @staticmethod
    def from_dict(dct, points = None, profiles = None, selected_band = None, **__kwargs__):
        ret = PointsLayer(selected_band.dynamic_attribute("dataset"), points, profiles)
        ret.opacity = dct['opacity']
        ret.is_enabled = dct.get('is_enabled', True)
        return ret

    def to_dict(self):
        return {
            "opacity": self.opacity,
            "is_enabled": self.is_enabled,
        }

class InitializedPointsLayer(InitializedLayer):
    def __init__(self, context, points_layer):
        super().__init__(context, points_layer)
        self.__points_context = self.GL_create_shared_context()

    @dynamic.memo(SELF.layer.GL_draw_points_and_profiles,
                     destroy = destroy_texture)
    def GL_texture(self):
        return self.GL_paint_into_texture(*self.layer.texture_size, self.__points_context, self.layer.GL_draw_points_and_profiles)

    @dynamic.memo(SELF.GL_texture, SELF.layer.geo_to_image, SELF.layer.opacity, SELF.layer.is_enabled)
    def GL_setup(self):
        tex = self.GL_texture
        def doit(program):
            uni = self.local_uniforms(program.uniforms)
            uni.points_texture = tex
            uni.geo_to_image = self.layer.geo_to_image
            uni.opacity = self.layer.opacity if self.layer.is_enabled else 0.0
        return doit

    def GL_free(self):
        self.dynamic_attribute("GL_texture").clear()
        self.dynamic_attribute("GL_setup").clear()
