from .__prelude__ import (
    SELF, dynamic
)

from .Layer import Layer, InitializedLayer

SWIPE_SHADER = """
#version 330

uniform mat3 geo_to_model;
uniform mat4 model_to_world;
uniform mat4 world_to_clip;
uniform float {cutoff};
uniform float {hidden_opacity};

float {geo_height}(vec3 geo_coords) {{
   return 0.0;
}}

vec4 {geo_color}(vec3 geo_coords, inout float up_opacity) {{
  vec3 model_coords = geo_to_model * geo_coords;
  vec4 clip_coords = world_to_clip * model_to_world * vec4(model_coords.xy, 0.0, model_coords.z);
  if({hidden_opacity} <= 0.5)
     up_opacity = clip_coords.x / clip_coords.w > {cutoff} ? 1.0 : 0.0;
  return vec4(0.0);
}}
"""

class SwipeLayer(Layer):
    cutoff = dynamic.variable()
    shaders = dynamic.readonly()

    def __init__(self):
        super().__init__()
        self._shaders = [
            SWIPE_SHADER.format(
                **self.local_idents("geo_color", "geo_height", "cutoff", "hidden_opacity")
            )
        ]
        self.cutoff = 0.0
        self.dynamic_attribute("_redraw").value_changed.connect(lambda: self._redraw())

    @dynamic.method(SELF.cutoff, SELF.is_enabled)
    def _redraw(self):
        self.renderChanged.emit()

    def GL_initialize(self, context):
        return InitializedSwipeLayer(context, self)

    __mime_type__ = "x-application/insarviz/SwipeLayer"
    @staticmethod
    def from_dict(dct, **__kwargs__):
        ret = SwipeLayer()
        ret.cutoff = dct['cutoff']
        return ret

    def to_dict(self):
        return {
            "cutoff": self.cutoff
        }


class InitializedSwipeLayer(InitializedLayer):
    def __init__(self, context, layer):
        super().__init__(context, layer)

    @dynamic.memo(SELF.layer.geo_to_clip, SELF.layer.cutoff, SELF.layer.is_enabled)
    def GL_setup(self):
        def doit(program):
            uni = self.local_uniforms(program.uniforms)
            uni.cutoff = 2*self.layer.cutoff-1
            uni.hidden_opacity = 0.0 if self.layer.is_enabled else 1.0
        return doit
