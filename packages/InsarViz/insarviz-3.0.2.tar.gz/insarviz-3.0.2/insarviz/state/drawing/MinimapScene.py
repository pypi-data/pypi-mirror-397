from typing import Optional
from OpenGL import GL

from .__prelude__ import (
    SelectedBand, Shader, Qt, Matrix, Bound, GLProgram,
    dynamic, SELF,
    destroy_texture,
)

from .Scene import Scene, SceneDrawing
from .MapScene import MapScene

class InitializedMinimapScene(SceneDrawing["MinimapScene"]):
    def __init__(self, context, scene):
        super().__init__(context, scene)
        self._program = GLProgram(self.drawing._shaders)
        self._image_mesh = self._program.create_square_mesh(GL.GL_TRIANGLES)
        self._rect_program = GLProgram(self.drawing._rect_shaders)
        self._loop_mesh = self._rect_program.create_square_mesh(GL.GL_LINE_LOOP)
        self.map_world_to_clip = Matrix.identity(4)

    @dynamic.memo(SELF.viewport_size)
    def world_to_clip(self):
        w, h = self.viewport_size
        hfactor = min(1.0, float(h)/float(w))
        vfactor = min(1.0, float(w)/float(h))

        return Matrix.product(
            Matrix.scale((hfactor, vfactor, 1.0, 1.0))
        )

    @dynamic.memo(SELF.drawing.colormap.createTexture,
                     destroy = destroy_texture)
    def GL_colormap_texture(self):
        return self.drawing.colormap.createTexture()

    def paintGL(self):
        gl = self.context.functions()
        gl.glEnable(GL.GL_BLEND)
        gl.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        gl.glClearColor(0.5, 0.5, 0.5, 0.0)
        gl.glClear(int(GL.GL_COLOR_BUFFER_BIT))

        colormap_texture = self.GL_colormap_texture
        dem_texture = self.drawing.selected_band.texture
        ref_texture = self.drawing.selected_band.reference_texture
        with self._program as p:
            p.uniforms.image             = dem_texture
            p.uniforms.reference_image   = ref_texture
            p.uniforms.model_to_clip     = self.world_to_clip * self.drawing.model_to_world
            p.uniforms.colormap          = colormap_texture
            p.uniforms.value_to_color    = self.drawing._colormap.value_to_color
            p.uniforms.texture_to_image  = dem_texture.texture_to_image
            p.uniforms.model_to_texture  = Matrix.product(
                self.drawing.map_scene.model_to_texture,
                Matrix.translate((-1,-1)),
                Matrix.scale((2,2,1)),
            )
            self._image_mesh.draw()
        with self._rect_program as p:
            p.uniforms.clip_to_map_model = Matrix.product(
                self.map_world_to_clip,
                self.drawing._map_scene.model_to_world
            ).inverse()
            p.uniforms.model_to_clip = self.world_to_clip * self.drawing.model_to_world
            p.uniforms.rect_color = Qt.QColor("white")
            self._loop_mesh.draw()

    def freeGL(self):
        self.dynamic_attribute("GL_colormap_texture").clear()

class MinimapScene(Scene):
    colormap = dynamic.readonly()
    selected_band = dynamic.readonly()
    map_scene = dynamic.readonly()

    def __init__(self, selected_band: SelectedBand, map_scene: MapScene, colormap):
        super().__init__()
        self._selected_band = selected_band
        self._map_scene = map_scene
        self._colormap = colormap
        self._shaders = [
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Vertex, "minimap/vertex.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Fragment, "minimap/fragment.glsl")
        ]
        self._rect_shaders = [
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Vertex, "viewport_rect/vertex.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Fragment, "viewport_rect/fragment.glsl")
        ]
        self.dynamic_attribute('_redraw').value_changed.connect(lambda: self._redraw())

    @dynamic.method(SELF.selected_band.image, SELF.selected_band.reference_image,
                    SELF.colormap.image, SELF.colormap.value_to_color,
                    SELF.map_scene.model_to_texture,
                    SELF.map_scene.model_to_world)
    def _redraw(self):
        self.renderChanged.emit()

    @dynamic.memo()
    def model_to_world(self):
        return Matrix.identity(4)
    @dynamic.memo()
    def model_to_texture(self):
        return Matrix.product(
            Matrix.translate((0.5,0.5)),
            Matrix.scale((0.5,0.5,1.0))
        )

    def whileDrag(self, dragMode, dragStart, dragEnd):
        return self._map_scene.whileDrag(Qt.Qt.KeyboardModifier.NoModifier, dragEnd, dragStart)

    def initializeDrawing(self, context, /):
        return InitializedMinimapScene(context, self)
