import numpy as np
from OpenGL import GL
import math

from .__prelude__ import (
    SelectedBand, Qt, Shader, Point, Matrix, MapPoint, MapProfile, Bound,
    inOpenGLContext, OpenGLPainter,
    dynamic, SELF,
    GLProgram, PureShader,
    logger
)
from .Scene import Scene, SceneDrawing
from .layer import LayerStack
from .TileCache import TileCache

MAP_SHADER = """
#version 330
float {geo_height}(vec3 geo_coords);
vec4 {geo_color}(vec3 geo_coords, inout float up_opacity);

float geo_height(vec3 geo_coords) {{
  return {geo_height}(geo_coords);
}}
vec4 geo_color(vec3 geo_coords) {{
  float up_opacity = 1.0;
  return {geo_color}(geo_coords, up_opacity);
}}
"""

class MapScene(Scene):
    selected_band     = dynamic.readonly()
    band_colormap     = dynamic.readonly()
    tile_cache        = dynamic.readonly()
    temp_point        = dynamic.readonly()
    temp_profile      = dynamic.readonly()
    overlay_layer     = dynamic.readonly()
    flip_horizontally = dynamic.variable(False)
    flip_vertically   = dynamic.variable(False)
    geo_focus         = dynamic.variable(None)

    def __init__(self, selected_band: SelectedBand, points, profiles, layers, band_colormap):
        super().__init__()
        self._selected_band = selected_band
        self._shaders = [
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Vertex,"map/vertex.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.TessellationControl,"map/tess_control.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.TessellationEvaluation, "map/tess_eval.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.TessellationEvaluation, "map/utils.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Fragment,"map/fragment.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Fragment,"hsv_rgb.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Fragment,"map/utils.glsl")
        ]
        self._tile_shaders = [
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Vertex,"tile/vertex.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Fragment,"tile/fragment.glsl"),
        ]
        self._band_colormap = band_colormap

        self._tile_cache = TileCache()
        self.tile_cache.new_tile_available.connect(self.renderChanged.emit)

        self.color = (0.5, 0.5, 0.5, 0.5)

        self.distance = 5.0
        self.__points = points
        self.__profiles = profiles

        self._overlay_layer = LayerStack(
            SELF.selected_band.dataset[self],
            SELF.temp_point[self],
            SELF.temp_profile[self],
            layers
        )
        self._overlay_layer.renderChanged.connect(self.renderChanged.emit)
        self._temp_point = None
        self._temp_profile = None

        self.dynamic_attribute("_rerender").value_changed.connect(lambda: self._rerender())

    def init_from_dict(self, dct):
        self.yaw = dct['yaw']
        self.pitch = dct['pitch']
        self.distance = dct['distance']
        self.center = Point(*dct['center'])
        self.heightUnits = dct['heightUnits']
        self.flip_horizontally = dct.get('flip_horizontally', False)
        self.flip_vertically = dct.get('flip_vertically', False)

    def to_dict(self):
        return {
            'yaw': self.yaw,
            'pitch': self.pitch,
            'distance': self.distance,
            'center': [self.center.x, self.center.y],
            'heightUnits': self.heightUnits,
            'flip_horizontally': self.flip_horizontally,
            'flip_vertically': self.flip_vertically,
        }

    @dynamic.memo(SELF.distance, SELF.pitch, SELF.yaw, SELF.center)
    def model_to_world(self):
        return Matrix.product(
            Matrix.translate((0.0,0.0,self.distance)),
            Matrix.rotate3(self.pitch, (-1.0, 0.0, 0.0, 0.0)),
            Matrix.rotate3(self.yaw, (0.0, 0.0, 1.0, 0.0)),
            Matrix.translate((self.center.x, self.center.y, 0.0))
        )
    @dynamic.memo(SELF.flip_horizontally, SELF.flip_vertically)
    def model_to_texture(self):
        h_flip = -1.0 if self.flip_horizontally else 1.0
        v_flip = -1.0 if self.flip_vertically else 1.0
        return Matrix.product(
            Matrix.scale((h_flip, v_flip, 1.0)),
            Matrix.scale((0.5,0.5,1.0)),
            Matrix.translate((h_flip,v_flip))
        )

    @dynamic.memo(SELF.band_colormap.xzero, SELF.band_colormap.xone)
    def value_to_elevation(self):
        lower, upper = self.band_colormap.xzero, self.band_colormap.xone
        scale = max(abs(lower), abs(upper))
        return Matrix.scale((1./scale, 1.0))
    @dynamic.memo(SELF.selected_band.dataset)
    def image_to_geo(self):
        w,h = self.selected_band.size
        return Matrix.product(
            self.selected_band.dataset.pixel_to_crs,
            Matrix.scale((w,h,1))
        )

    @dynamic.memo(SELF.selected_band.dataset)
    def show_background(self):
        return self.selected_band.dataset.is_georeferenced

    @dynamic.method(SELF.selected_band.image, SELF.selected_band.reference_image,
                    SELF.heightUnits, SELF.model_to_world, SELF.temp_point, SELF.temp_profile,
                    SELF.model_to_texture, SELF.geo_focus,
                    SELF.band_colormap.image, SELF.band_colormap.value_to_color)
    def _rerender(self):
        self.renderChanged.emit()

    def __create_point(self, dragStart: tuple[int, int], dragEnd: tuple[int, int]):
        xa,ya = dragStart
        xb,yb = dragEnd
        model_to_image = Matrix.product(
            self.selected_band.texture.texture_to_image,
            self.model_to_texture
        )
        def sq(x):
            return x*x
        dx_image, dy_image, _ = model_to_image.transform_vect((xb-xa, yb-ya, 0.0))
        w,h = self.selected_band.size
        # Clamp the radius to 100 pixels, to avoid users accidentally
        # computing the mean of the whole dataset
        radius = min(int(math.sqrt(sq(dx_image*w) + sq(dy_image*h))), 100)
        x_image, y_image = model_to_image.transform_point(dragStart)
        return MapPoint("Point", x_image*w, y_image*h, radius, Qt.QColor("blue"))
    def __create_profile(self, dragStart):
        dragEnd = dragStart
        x0, y0 = self.__model_to_pixel(*dragStart)
        x1, y1 = self.__model_to_pixel(*dragEnd)
        return MapProfile("Profile", 0, Qt.QColor("orange"), True, x0, y0, [(x1, y1)])
    def __model_to_pixel(self, x_model, y_model):
        model_to_image = Matrix.product(
            self.selected_band.texture.texture_to_image,
            self.model_to_texture
        )
        x_image, y_image = model_to_image.transform_point((x_model, y_model))
        w , h = self.selected_band.size
        return (int(x_image*w), int(y_image*h))

    def startDrag(self, dragMode, dragStart):
        if dragMode == Qt.Qt.KeyboardModifier.ShiftModifier:
            if self.temp_profile is None:
                self._temp_profile = self.__create_profile(dragStart)
            else:
                self.__append_profile_point(dragStart)
        return dragStart
    def whileDrag(self, dragMode, dragStart, dragEnd):
        if dragMode == Qt.Qt.KeyboardModifier.NoModifier:
            xa, ya = dragStart
            xb, yb = dragEnd
            self.center += Point(xb-xa, yb-ya)
        if dragMode == Qt.Qt.KeyboardModifier.ControlModifier:
            self._temp_point = self.__create_point(dragStart, dragEnd)
        if dragMode == Qt.Qt.KeyboardModifier.ShiftModifier:
            self._temp_profile.end_points[-1] = self.__model_to_pixel(*dragEnd)
            self.dynamic_attribute("temp_profile").value_changed.emit(self.temp_profile)

        return dragStart
    def endDrag(self, dragMode, dragStart, dragEnd):
        if dragMode == Qt.Qt.KeyboardModifier.ControlModifier:
            self._temp_point = None
            self.__points.append(self.__create_point(dragStart, dragEnd))
        if dragMode == Qt.Qt.KeyboardModifier.ShiftModifier:
            if self._temp_profile is not None:
                self.__append_profile_point(dragEnd)
            return dragEnd
    def __append_profile_point(self, pt):
        new_point = self.__model_to_pixel(*pt)
        if len(self.temp_profile.end_points) < 2 or new_point != self.temp_profile.end_points[-2]:
            self.temp_profile.end_points.append(new_point)
        self.dynamic_attribute("temp_profile").value_changed.emit(self.temp_profile)

    def abortDrag(self, dragMode, dragStart):
        if dragMode == Qt.Qt.KeyboardModifier.ControlModifier:
            self._temp_point = None
        if dragMode == Qt.Qt.KeyboardModifier.ShiftModifier:
            if len(self.temp_profile.end_points) > 1:
                self.temp_profile.end_points[-1:] = []
                self.__profiles.append(self.temp_profile)
                self._temp_profile = None

    def initializeDrawing(self, context):
        gl = context.functions()
        logger.debug("Loading map scene (max texture size : %d)", gl.glGetIntegerv(GL.GL_MAX_TEXTURE_SIZE))
        return InitializedMapScene(context, self)

class InitializedMapScene(SceneDrawing["MapScene"]):
    def __init__(self, context, map_scene):
        super().__init__(context, map_scene)

        self.__tile_program: Qt.QOpenGLShaderProgram = GLProgram(map_scene._tile_shaders)
        self.__tile_mesh = self.__tile_program.create_square_mesh(GL.GL_TRIANGLES, split=0, texture_to_model = Matrix.identity(3))

        self.__initialized_overlay = self.drawing.overlay_layer.GL_initialize(context)
        GL.glPatchParameteri(GL.GL_PATCH_VERTICES, 3)

    @dynamic.memo(SELF.drawing.overlay_layer.shaders)
    def GL_program(self):
        return GLProgram(self.drawing._shaders + [
            PureShader(Qt.QOpenGLShader.ShaderTypeBit.Fragment, shader)
            for shader in self.drawing.overlay_layer.shaders
        ] + [
            PureShader(Qt.QOpenGLShader.ShaderTypeBit.TessellationEvaluation, shader)
            for shader in self.drawing.overlay_layer.shaders
        ] + [
            PureShader(Qt.QOpenGLShader.ShaderTypeBit.Fragment, MAP_SHADER.format(
                geo_color = self.drawing.overlay_layer.local_ident("geo_color"),
                geo_height = self.drawing.overlay_layer.local_ident("geo_height")
            )),
            PureShader(Qt.QOpenGLShader.ShaderTypeBit.TessellationEvaluation, MAP_SHADER.format(
                geo_color = self.drawing.overlay_layer.local_ident("geo_color"),
                geo_height = self.drawing.overlay_layer.local_ident("geo_height")
            ))

        ])
    @dynamic.memo(SELF.GL_program, SELF.drawing.model_to_texture)
    def GL_mesh(self):
        return self.GL_program.create_square_mesh(
            GL.GL_PATCHES, split=8,
            texture_to_model = self.drawing.model_to_texture.inverse())

    @dynamic.memo(SELF.viewport_size)
    def world_to_clip(self):
        w,h = self.viewport_size
        hfactor = max(1.0, w/h)/4.0
        vfactor = max(1.0, h/w)/4.0
        near = 4.0*0.005
        return Matrix.frustum(-hfactor*near, hfactor*near,
                              -vfactor*near, vfactor*near,
                              -near, -1000.0)
    @dynamic.memo(SELF.viewport_size)
    def tiles_per_screen(self):
        w,h = self.viewport_size
        return max(w/256.0, h/256.0) # Each tile is 256 pixels wide
    @dynamic.memo(SELF.viewport_size)
    def clip_to_pixel(self):
        w,h = self.viewport_size
        return Matrix.scale((w/2.0, -h/2.0, 1.0)) * Matrix.translate((1.0,-1.0))

    def paintGL(self):
        program = self.GL_program
        mesh = self.GL_mesh
        glfunc = self.context.functions()
        setup_overlay = self.__initialized_overlay.GL_setup

        glfunc.glEnable(GL.GL_DEPTH_TEST)

        glfunc.glClearColor(*self.drawing.color)
        glfunc.glClear(int(GL.GL_COLOR_BUFFER_BIT) | int(GL.GL_DEPTH_BUFFER_BIT))

        if self.drawing.show_background:
            if self.drawing.pitch < 60.0:
                self.drawing.tile_cache.GL_paint_background(
                    glfunc,
                    model_to_crs = Matrix.product(
                        self.drawing.selected_band.image_to_crs,
                        self.drawing.selected_band.texture.texture_to_image,
                        self.drawing.model_to_texture
                    ),
                    clip_to_model = self.clip_to_model,
                    model_to_world = self.drawing.model_to_world,
                    world_to_clip = self.world_to_clip,
                    tiles_per_screen = self.tiles_per_screen,
                )

        dem_texture = self.drawing.selected_band.texture
        ref_texture = self.drawing.selected_band.reference_texture
        tex_to_image = dem_texture.texture_to_image

        glfunc.glEnable(GL.GL_BLEND)
        glfunc.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        with program as p:
            p.uniforms.image = dem_texture
            p.uniforms.ref_image = ref_texture

            p.uniforms.texture_to_image = tex_to_image
            p.uniforms.image_to_texture = tex_to_image.inverse()

            p.uniforms.image_to_geo = self.drawing.image_to_geo
            p.uniforms.geo_to_model = Matrix.product(
                self.drawing.image_to_geo,
                tex_to_image,
                self.drawing.model_to_texture,
            ).inverse()
            setup_overlay(p)

            p.uniforms.heightUnits = float(self.drawing.heightUnits)
            p.uniforms.value_to_elevation = self.drawing.value_to_elevation
            _,_,z_near = self.world_to_clip.inverse().transform_point((0.0,0.0,-1.0))
            p.uniforms.near = z_near

            p.uniforms.world_to_clip = self.world_to_clip
            p.uniforms.model_to_world = self.drawing.model_to_world

            mesh.draw()

        if self.drawing.geo_focus is not None:
            with OpenGLPainter(*self.viewport_size) as painter:
                center = (tex_to_image * self.drawing.model_to_texture).inverse().transform_point(self.drawing.geo_focus)
                clip_cx, clip_cy, _ = (self.world_to_clip * self.drawing.model_to_world).transform_point((*center, 0.0))
                pixel_cx, pixel_cy = self.clip_to_pixel.transform_point((clip_cx, -clip_cy))
                painter.setBrush(Qt.QColor('red'))
                painter.drawEllipse(Qt.QPointF(pixel_cx, pixel_cy), 10 , 10)

    def freeGL(self):
        self.__initialized_overlay.GL_free()
