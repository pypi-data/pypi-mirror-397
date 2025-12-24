from OpenGL import GL
import numpy as np

from .__prelude__ import (
    dynamic, SELF, Matrix, unit_square_to_image,
    Shader, PureShader, Qt, GLProgram, destroy_texture,
    Point
)
from .Scene import Scene, SceneDrawing

GEO_SHADER = """
#version 330
uniform mat3 geo_to_lut;
uniform sampler2D lut_texture;

vec4 {radar_color}(vec3 geo_coords, inout float up_opacity);

vec4 geo_color(vec3 geo_coords) {{
  vec3 lut_coords_homo = geo_to_lut * geo_coords;
  vec2 lut_coords = lut_coords_homo.xy / lut_coords_homo.z;
  vec4 lut_values = texture(lut_texture, lut_coords);
  float up_opacity = 1.0;
  return {radar_color}(vec3(lut_values.xy,1), up_opacity);
}}
"""

class GeoScene(Scene):
    selected_band    = dynamic.readonly()
    lut_geo_dataset  = dynamic.readonly()
    overlay_layer    = dynamic.external()
    tile_cache       = dynamic.external()

    def __init__(self, selected_band, lut_geo_dataset, dynamic_overlay_layer, dynamic_tile_cache):
        super().__init__()
        self._selected_band = selected_band
        self._lut_geo_dataset = lut_geo_dataset
        self._dynamic_tile_cache = dynamic_tile_cache
        self._dynamic_overlay_layer = dynamic_overlay_layer
        self.distance = 4.0

        self.dynamic_attribute("_rerender").value_changed.connect(lambda: self._rerender())

    @dynamic.method(SELF.model_to_world, SELF.tile_cache.provider)
    def _rerender(self):
        self.renderChanged.emit()

    @dynamic.memo(SELF.lut_geo_dataset.size, SELF.lut_geo_dataset.pixel_to_crs, SELF.model_to_image)
    def model_to_geo(self):
        w, h = self.lut_geo_dataset.size
        return Matrix.product(
            self.lut_geo_dataset.pixel_to_crs,
            Matrix.scale((w, h, 1)),
            self.model_to_image,
        )
    @dynamic.memo(SELF.distance, SELF.center)
    def model_to_world(self):
        return Matrix.product(
            Matrix.translate((0,0,self.distance)),
            Matrix.translate((self.center.x, self.center.y, 0.0)),
        )
    @dynamic.memo(SELF.lut_geo_dataset.size)
    def model_to_image(self):
        w, h = self.lut_geo_dataset.size
        return unit_square_to_image(w,h)

    @dynamic.memo(SELF.lut_geo_dataset)
    def lut_image(self):
        ret = np.stack([
            self.lut_geo_dataset.read(1),
            self.lut_geo_dataset.read(2),
        ], axis=-1).astype(np.float32)
        return ret
    @dynamic.memo(SELF.selected_band.size)
    def lut_scale(self):
        w, h = self.selected_band.size
        return np.array([1/w, 1/h])

    def whileDrag(self, dragMode, dragStart, dragEnd):
        if dragMode == Qt.Qt.KeyboardModifier.NoModifier:
            xa, ya = dragStart
            xb, yb = dragEnd
            self.center += Point(xb-xa, yb-ya)
        return dragStart

    @property
    def shaders(self):
        return [
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Vertex, "geo_map/vertex.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Fragment, "geo_map/fragment.glsl"),
        ]

    def initializeDrawing(self, context):
        return GeoSceneDrawing(context, self)

class GeoSceneDrawing(SceneDrawing):
    def __init__(self, context, geo_scene):
        super().__init__(context, geo_scene)
        self.__initialized_overlay = self.drawing.overlay_layer.GL_initialize(context)
        self.__initialized_overlay.dynamic_attribute("GL_setup").value_changed.connect(lambda: self.drawing.renderChanged.emit())

    @dynamic.memo(SELF.viewport_size)
    def world_to_clip(self):
        w, h = self.viewport_size
        hfactor = max(1.0, w/h)/4.0
        vfactor = max(1.0, h/w)/4.0
        near = 4.0*0.005
        return Matrix.frustum(-hfactor*near, hfactor*near,
                              -vfactor*near, vfactor*near,
                              -near, -1000.0)

    @dynamic.memo(SELF.drawing.overlay_layer.shaders)
    def GL_program(self):
        return GLProgram(
            self.drawing.shaders + [
                PureShader(Qt.QOpenGLShader.ShaderTypeBit.Fragment, shader)
                for shader in self.drawing.overlay_layer.shaders
            ] + [
                PureShader(Qt.QOpenGLShader.ShaderTypeBit.Fragment, GEO_SHADER.format(
                    radar_color = self.drawing.overlay_layer.local_ident("geo_color")
                ))
            ]
        )
    @dynamic.memo(SELF.GL_program)
    def GL_mesh(self):
        return self.GL_program.create_square_mesh(GL.GL_TRIANGLES)

    @dynamic.memo(SELF.drawing.lut_geo_dataset, destroy = destroy_texture)
    def GL_lut_geo_texture(self):
        ret = Qt.QOpenGLTexture(Qt.QOpenGLTexture.Target2D)
        w, h = self.drawing.lut_geo_dataset.size
        img = self.drawing.lut_image

        ret.setWrapMode(Qt.QOpenGLTexture.ClampToEdge)
        ret.setSize(w, h)
        ret.setFormat(Qt.QOpenGLTexture.TextureFormat.RG32F)
        ret.allocateStorage(Qt.QOpenGLTexture.PixelFormat.RG, Qt.QOpenGLTexture.PixelType.Float32)
        ret.setData(Qt.QOpenGLTexture.PixelFormat.RG, Qt.QOpenGLTexture.PixelType.Float32, img) #type: ignore
        ret.create()

        return ret

    @dynamic.memo(SELF.viewport_size)
    def tiles_per_screen(self):
        w,h = self.viewport_size
        return max(w/256.0, h/256.0) # Each tile is still 256 pixels wide

    def paintGL(self):
        gl = self.context.functions()

        program = self.GL_program
        mesh = self.GL_mesh

        lut_texture = self.GL_lut_geo_texture
        setup_overlay = self.__initialized_overlay.GL_setup

        gl.glEnable(GL.GL_BLEND)
        gl.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(GL.GL_DEPTH_TEST)
        gl.glClearColor(0.0,0.0,0.0,0.0)
        gl.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.drawing.tile_cache.GL_paint_background(
            gl,
            model_to_crs = self.drawing.model_to_geo,
            clip_to_model = self.clip_to_model,
            model_to_world = self.drawing.model_to_world,
            world_to_clip = self.world_to_clip,
            tiles_per_screen = self.tiles_per_screen,
        )

        with program as p:
            setup_overlay(p)
            p.uniforms.lut_texture = lut_texture

            p.uniforms.model_to_clip = Matrix.product(
                self.world_to_clip,
                self.drawing.model_to_world,
            )
            p.uniforms.model_to_geo = self.drawing.model_to_geo
            p.uniforms.geo_to_lut = self.drawing.model_to_image * self.drawing.model_to_geo.inverse()
            mesh.draw()

    def freeGL(self):
        self.dynamic_attribute("GL_lut_geo_texture").clear()
