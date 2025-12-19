from .__prelude__ import (
    Qt, Matrix, destroy_texture,
    dynamic, SELF)
from .Layer import Layer, InitializedLayer

STACK_SHADER = """
#version 330
{geo_color_decl}
uniform sampler2D {temp_texture};
uniform mat3 {geo_to_image};

float {geo_height}(vec3 geo_coords) {{
  float dst_height = 0.0;
  {modify_dst_height}
  return dst_height;
}}

vec4 {geo_color}(vec3 geo_coords, inout float up_opacity) {{
  vec4 dst_color = vec4(0.0);
  vec4 src_color;
  {modify_dst}
  vec3 image_coords = {geo_to_image} * geo_coords;
  src_color = texture({temp_texture}, image_coords.xy / image_coords.z);
  dst_color = mix(dst_color, src_color, src_color.w);
  return dst_color;
}}
"""

class LayerStack(Layer):
    layers = dynamic.readonly()
    temp_point = dynamic.external()
    temp_profile = dynamic.external()
    dataset = dynamic.external()

    def __init__(self, dyn_dataset, dyn_temp_point, dyn_temp_profile, layers):
        super().__init__()
        self._dynamic_temp_point = dyn_temp_point
        self._dynamic_temp_profile = dyn_temp_profile
        self._dynamic_dataset = dyn_dataset
        self._layers = layers
        for layer in self.layers:
            layer.renderChanged.connect(self.renderChanged.emit)

        self.layers.endInsertRange.connect(self.__on_layers_inserted)
        self.layers.beginRemoveRange.connect(self.__on_layers_removed)
        self.layers.endRemoveRange.connect(self.__invalidate_shaders)
        self.layers.beginReplaceRange.connect(self.__before_layers_replaced)
        self.layers.endReplaceRange.connect(self.__after_layers_replaced)

    @Qt.Slot()
    def __invalidate_shaders(self):
        self.dynamic_attribute("shaders").invalidate()
        self.renderChanged.emit()

    @Qt.Slot(int, int)
    def __on_layers_inserted(self, start, length):
        for layer in self.layers[start:start+length]:
            layer.renderChanged.connect(self.renderChanged.emit)
        self.__invalidate_shaders()
    @Qt.Slot(int, int)
    def __on_layers_removed(self, start, end):
        for layer in self.layers[start:end]:
            layer.renderChanged.disconnect(self.renderChanged.emit)
    @Qt.Slot(int, int)
    def __before_layers_replaced(self, start, end):
        for layer in self.layers[start:end]:
            layer.renderChanged.disconnect(self.renderChanged.emit)
    @Qt.Slot(int, int)
    def __after_layers_replaced(self, start, end):
        for layer in self.layers[start:end]:
            layer.renderChanged.connect(self.renderChanged.emit)
        self.__invalidate_shaders()

    @dynamic.memo(SELF.dataset)
    def geo_to_image(self):
        w,h = self.dataset.size
        return Matrix.product(
            self.dataset.pixel_to_crs,
            Matrix.scale((w,h,1))
        ).inverse()

    @dynamic.memo()
    def shaders(self):
        modifications = []
        height_modifications = []
        declarations = []
        for layer in self._layers:
            modifications.append(
                "src_color = {geo_color}(geo_coords, up_opacity); dst_color = vec4(mix(dst_color.xyz, src_color.xyz, src_color.w), max(src_color.w, dst_color.w));".format(
                    geo_color = layer.local_ident("geo_color")
                )
            )
            declarations.append(
                "vec4 {geo_color}(vec3 geo_coords, inout float up_opacity);".format(
                    geo_color = layer.local_ident("geo_color")
                )
            )

            height_modifications.append(
                "dst_height += {geo_height}(geo_coords);".format(
                    geo_height = layer.local_ident("geo_height")
                )
            )
            declarations.append(
                "float {geo_height}(vec3 geo_coords);".format(
                    geo_height = layer.local_ident("geo_height")
                )
            )

        ret = [
            shader
            for layer in self._layers
            for shader in layer.shaders
        ] + [
            STACK_SHADER.format(
                modify_dst = '\n'.join(reversed(modifications)),
                modify_dst_height = '\n'.join(reversed(height_modifications)),
                geo_color_decl = '\n'.join(declarations),
                **self.local_idents("geo_color", "geo_height", "geo_to_image", "temp_texture")
            )
        ]

        return ret

    def GL_initialize(self, context):
        return InitializedLayerStack(context, self)

class InitializedLayerStack(InitializedLayer):
    def __init__(self, context, layer):
        super().__init__(context, layer)
        self.__temp_context = self.GL_create_shared_context()

        self.__initialized_layers = [
            None for layer in self.layer.layers
        ]
        self.__removed_layers = []
        self.layer.layers.endInsertRange.connect(self.__on_insert_layers)
        self.layer.layers.endRemoveRange.connect(self.__on_remove_layers)
        self.layer.layers.endReplaceRange.connect(self.__on_replace_layers)

    @Qt.Slot(int, int)
    def __on_insert_layers(self, start, count):
        self.__initialized_layers[start:start] = [ None for _ in range(count) ]
        self.dynamic_attribute("GL_initialized_layers").invalidate()
    @Qt.Slot(int, int)
    def __on_remove_layers(self, start, end):
        self.__remove_layers(self.__initialized_layers[start:end])
        self.__initialized_layers[start:end] = []
        self.dynamic_attribute("GL_initialized_layers").invalidate()
    @Qt.Slot(int, int)
    def __on_replace_layers(self, start, end):
        self.__remove_layers(self.__initialized_layers[start:end])
        self.__initialized_layers[start:end] = [ None for _ in range(start, end) ]
        self.dynamic_attribute("GL_initialized_layers").invalidate()

    def __GL_initialize_layer(self, i, layer):
        ini_layer = layer.GL_initialize(self.context)
        ini_layer.dynamic_attribute("GL_setup").value_changed.connect(self.__layer_needs_setup)
        self.__initialized_layers[i] = ini_layer
    @Qt.Slot()
    def __layer_needs_setup(self):
        self.dynamic_attribute("GL_setup").invalidate()
    def __remove_layers(self, layers):
        self.__removed_layers += layers
        for layer in layers:
            if layer is not None:
                layer.dynamic_attribute("GL_setup").value_changed.disconnect(self.__layer_needs_setup)

    def __GL_free_removed(self):
        for layer in self.__removed_layers:
            if layer is not None:
                layer.GL_free()
        self.__removed_layers = []

    @dynamic.memo()
    def GL_initialized_layers(self):
        self.__GL_free_removed()
        for i, layer in enumerate(self.layer.layers):
            ini_layer = self.__initialized_layers[i]
            if ini_layer is None:
                self.__GL_initialize_layer(i, layer)
        return self.__initialized_layers

    @dynamic.memo(SELF.layer.dataset, SELF.layer.temp_point, SELF.layer.temp_profile,
                     destroy = destroy_texture)
    def GL_temp_texture(self):
        def do_paint(painter):
            if self.layer.temp_point is not None:
                self.layer.temp_point.draw(painter, 1.0)
            if self.layer.temp_profile is not None:
                self.layer.temp_profile.draw(painter, 1.0)
        return self.GL_paint_into_texture(*self.layer.dataset.size, self.__temp_context, do_paint)

    @dynamic.memo(SELF.GL_initialized_layers, SELF.GL_temp_texture, SELF.layer.geo_to_image)
    def GL_setup(self):
        all_setups = [
            layer.GL_setup for layer in self.GL_initialized_layers
        ]
        tex = self.GL_temp_texture
        def doit(program):
            for setup in all_setups:
                setup(program)
            uni = self.local_uniforms(program.uniforms)
            uni.temp_texture = tex
            uni.geo_to_image = self.layer.geo_to_image
        return doit

    def GL_free(self):
        self.__GL_free_removed()
        self.dynamic_attribute("GL_setup").clear()
        self.dynamic_attribute("GL_temp_texture").clear()
        self.dynamic_attribute("GL_initialized_layers").clear()
        for layer in self.__initialized_layers:
            if layer is not None:
                layer.GL_free()
