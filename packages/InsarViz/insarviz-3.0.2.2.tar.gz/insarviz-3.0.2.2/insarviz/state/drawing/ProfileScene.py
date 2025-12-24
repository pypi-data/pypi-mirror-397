from typing import Any, TypeVar
import numpy as np
import math
from OpenGL import GL
import datetime

from .__prelude__ import (
    Matrix, Point, Qt, Base10Increments, Shader, Bound, OpenGLPainter,
    GLProgram, dynamic, SELF,
    destroy_texture, linmap
)
from .Scene import Scene, SceneDrawing

def vec_angle(v1, v2):
    x1, y1 = v1
    x2, y2 = v2
    num = x1*y2-y1*x2
    denom = x1*x2+y1*y2
    return math.atan2(num, denom)

class ProfileScene(Scene):
    profile_data_changed = Qt.Signal()
    pan = dynamic.variable(Point(0.0,0.0))
    profile_data = dynamic.variable()

    def __init__(self, profile_data):
        super().__init__()
        self.profile_data = profile_data
        self.distance = 1.0

        self._line_shaders = [
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Vertex,"profile/line/vertex.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Fragment,"profile/line/fragment.glsl")
        ]
        self._profile_shaders = [
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Vertex,"profile/image/vertex.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Fragment,"profile/image/fragment.glsl"),
            Shader(Qt.QOpenGLShader.ShaderTypeBit.Fragment,"hsv_rgb.glsl"),
        ]

        self.dynamic_attribute('_redraw').value_changed.connect(lambda: self._redraw())
        self.dynamic_attribute('image_to_grid').value_changed.connect(self.__on_coords_changed)

    @Qt.Slot()
    def __on_coords_changed(self):
        grid_center_x, grid_center_y, _ = self.image_to_grid.transform_point((0.5, 0.5, 0.0))
        self.pan = Point(-grid_center_x, -grid_center_y)
        self.distance = 1.0

    @dynamic.method(SELF.model_to_world, SELF.distance, SELF.pan, SELF.profile_data.values_3d, SELF.diff_scale, SELF.profile_data.color, SELF.selected_band_position, SELF.profile_data.focus_point)
    def _redraw(self):
        self.renderChanged.emit()

    @dynamic.memo(SELF.profile_data.selected_band.dataset.has_band_dates)
    def show_time(self):
        if self.profile_data is None:
            def ret(x):
                return f"{x:.6g}"
        elif self.profile_data.selected_band.dataset.has_band_dates:
            def ret(timestamp):
                return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        else:
            def ret(x):
                return f"{x:.6g}"
        return ret

    @dynamic.memo(SELF.profile_data.smoothing_factor)
    def diff_scale(self):
        return 0.002*(self.profile_data.smoothing_factor+1)

    @dynamic.memo(SELF.profile_data.values_3d, SELF.profile_data.selected_band.timestamp)
    def selected_band_position(self):
        xs, _, _ = self.profile_data.values_3d
        start,end = np.nanmin(xs), np.nanmax(xs)
        from_x, _ = linmap(start, end)
        return 0.5*(1+from_x(self.profile_data.selected_band.timestamp)), 1/len(xs)

    @dynamic.memo(SELF.pitch, SELF.yaw)
    def model_to_world(self):
        return Matrix.product(
            Matrix.translate((0.0,0.0,8.0)),
            Matrix.rotate3(self.pitch, (-1.0,0.0,0.0,0.0)),
            Matrix.rotate3(self.yaw, (0.0,0.0,1.0,0.0)),
        )
    @dynamic.memo(SELF.distance, SELF.pan, SELF.image_to_grid_scale)
    def grid_to_model(self):
        return Matrix.product(
            Matrix.scale((1./self.distance, 1./self.distance, 1.0, 1.0)),
            Matrix.scale((2,2,1,1)),
            self.image_to_grid_scale.inverse(),
            Matrix.translate((self.pan.x, self.pan.y, 0.0)),
        )

    @dynamic.memo(SELF.profile_data.values_3d)
    def image_to_grid_scale(self):
        if self.profile_data is None:
            return Matrix.identity(4)
        xs, ys, zs = self.profile_data.values_3d
        w, h, d = xs[-1] - xs[0], ys[-1] - ys[0], max(abs(np.nanmin(zs)), abs(np.nanmax(zs)))
        if d < 1e-10:
            d = 1.0
        return Matrix.scale((h, w, d, 1))

    @dynamic.memo(SELF.image_to_grid_scale, SELF.height_scale)
    def image_to_grid(self):
        if self.profile_data is None:
            return Matrix.identity(4)
        xs, ys, zs = self.profile_data.values_3d
        return Matrix.product(
            Matrix.translate((ys[0], xs[0], 0.0)),
            self.image_to_grid_scale,
        )

    @dynamic.memo(SELF.profile_data.values_3d)
    def height_scale(self):
        if self.profile_data is None:
            return 1.0
        _, _, zs = self.profile_data.values_3d
        zscale = max(abs(np.nanmax(zs)), abs(np.nanmin(zs)))
        if zscale == 0.0:
            return 1.0
        return 1/zscale

    def startDrag(self, mode, dragStart):
        return dragStart
    def whileDrag(self, mode, dragStart, dragEnd):
        model_to_grid = Matrix.extend(4,2).inverse() * self.grid_to_model.inverse() * Matrix.extend(4,2)
        xa,ya = model_to_grid.transform_point(dragStart)
        xb,yb = model_to_grid.transform_point(dragEnd)
        self.pan += Point(xb-xa,yb-ya)
        return dragEnd

    def initializeDrawing(self, context):
        return ProfileSceneDrawing(context, self)

class ProfileSceneDrawing(SceneDrawing[ProfileScene]):
    def __init__(self, context, scene):
        super().__init__(context, scene)
        self._lines_program = GLProgram(self.drawing._line_shaders)
        self._profile_program = GLProgram(self.drawing._profile_shaders)

    @dynamic.memo(SELF.drawing.profile_data.values_3d)
    def GL_image_mesh(self):
        if self.drawing.profile_data is None:
            return None
        xs,ys,zs = self.drawing.profile_data.values_3d
        w,h = zs.shape
        return self._profile_program.create_grid_mesh("vertex_texture_coords", w, h)

    @dynamic.memo(SELF.drawing.profile_data.values_3d,
                     destroy = destroy_texture)
    def GL_profile_texture(self):
        if self.drawing.profile_data is None:
            return None

        profile_texture = Qt.QOpenGLTexture(Qt.QOpenGLTexture.Target.Target2D)
        profile_texture.setMagnificationFilter(Qt.QOpenGLTexture.Filter.Linear)
        profile_texture.setWrapMode(Qt.QOpenGLTexture.WrapMode.ClampToEdge)

        xs, ys, zs = self.drawing.profile_data.values_3d
        zs_cum = np.nancumsum(zs, axis=1)
        zs_cum = np.nancumsum(zs_cum, axis=0)
        zs_cumnans = np.cumsum(np.where(np.isnan(zs), 0.0, 1.0), axis=1)
        zs_cumnans = np.cumsum(zs_cumnans, axis=0)
        h,w = zs.shape
        profile_texture.setSize(w,h)
        profile_texture.setFormat(Qt.QOpenGLTexture.TextureFormat.RG32F)
        profile_texture.allocateStorage(Qt.QOpenGLTexture.PixelFormat.RG, Qt.QOpenGLTexture.PixelType.Float32)
        profile_texture.setData(Qt.QOpenGLTexture.PixelFormat.RG, Qt.QOpenGLTexture.PixelType.Float32,
                                np.stack([zs_cum, zs_cumnans], axis=-1).astype(np.float32))
        profile_texture.create()
        return profile_texture

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
    def clip_to_pixel(self):
        w,h = self.viewport_size
        return Matrix.scale((w/2.0, -h/2.0, 1.0)) * Matrix.translate((1.0,-1.0))

    def __draw_grid(self, gl):
        model_to_grid = self.drawing.grid_to_model.inverse()
        model_to_clip = Matrix.product(
            self.world_to_clip,
            self.drawing.model_to_world,
        )
        grid_to_clip = Matrix.product(
            model_to_clip,
            self.drawing.grid_to_model
        )

        lines = []
        major_ticks = {}
        for bottomleft, topright in [
                ((-1,-1,-1), (1,1,-1)),
                ((1,1,-1),   (1,-1,1)),
                ((1,-1,1),   (-1,-1,-1)),
                ((-1,1,1),   (1,-1,1)),
                ((-1,1,1),   (-1,-1,-1)),
                ((1,1,-1),   (-1,1,1)),
        ]:
            vertices = [None, None, None]
            for axis in range(3):
                if bottomleft[axis] == topright[axis]:
                    constant_axis = axis
                vertices[axis] = [*bottomleft]
                vertices[axis][axis] = topright[axis]
                vertices[axis] = model_to_clip.transform_point(vertices[axis])[:2]
            if vec_angle(vertices[(constant_axis+1)%3] - vertices[constant_axis],
                         vertices[(constant_axis+2)%3] - vertices[constant_axis]) >= 0:
                continue

            grid_bottomleft = model_to_grid.transform_point(bottomleft)
            grid_topright = model_to_grid.transform_point(topright)

            for axis in range(3):
                if bottomleft[axis] != topright[axis]:
                    line_bottomleft = [*grid_bottomleft, 1.0]
                    line_topright = [*grid_topright, 1.0]
                    line_topright[axis] = line_bottomleft[axis]
                    lines.append(line_bottomleft)
                    lines.append(line_topright)

                    line_bottomleft = [*grid_bottomleft, 1.0]
                    line_topright = [*grid_topright, 1.0]
                    line_bottomleft[axis] = line_topright[axis]
                    lines.append(line_bottomleft)
                    lines.append(line_topright)

                    for inc_type, inc in Base10Increments(grid_bottomleft[axis], grid_topright[axis]):
                        line_weight = 1.0 if inc_type == Base10Increments.MAJOR_INCREMENT else 0.0
                        line_start = [*grid_bottomleft, line_weight]
                        line_end = [*grid_topright, line_weight]
                        line_start[axis] = inc
                        line_end[axis] = inc
                        lines.append(line_start)
                        lines.append(line_end)
                        if inc_type == Base10Increments.MAJOR_INCREMENT:
                            start_ind = tuple(line_start[:3])
                            end_ind = tuple(line_end[:3])
                            ln = [start - 0.1*(end-start) for end,start in zip(end_ind, start_ind)]
                            if start_ind in major_ticks:
                                del major_ticks[start_ind]
                            else:
                                major_ticks[start_ind] = (ln, inc, axis)

                            ln = [end - 0.1*(start-end) for end,start in zip(end_ind, start_ind)]
                            if end_ind in major_ticks:
                                del major_ticks[end_ind]
                            else:
                                major_ticks[end_ind] = (ln, inc, axis)

        line_mesh = self._lines_program.create_mesh(GL.GL_LINES, [("grid_coords", 4)], np.array(lines, dtype=np.float32))
        with self._lines_program as p:
            p.uniforms.grid_to_clip = grid_to_clip
            line_mesh.draw()

        return [ln for ln in major_ticks.values()], grid_to_clip

    def __draw_major_ticks(self, gl, major_ticks, grid_to_clip):
        pixel_ratio = self.context.screen().devicePixelRatio()
        with OpenGLPainter(*[x*pixel_ratio for x in self.viewport_size]) as painter:
            painter.scale(1.0, -1.0)
            painter.setPen(Qt.QColor(0,0,0))
            grid_to_pixel = Matrix.product(
                Matrix.scale((self.viewport_size[0]*pixel_ratio, -self.viewport_size[1]*pixel_ratio, 1.0, 2.0)),
                Matrix.translate((1,1,1)),
                grid_to_clip
            )
            for grid_coord, inc, axis in major_ticks:
                pixel_x, pixel_y, _ = grid_to_pixel.transform_point(grid_coord)
                wHuge, hHuge = 32000, 32000
                rect = Qt.QRectF(pixel_x - wHuge, pixel_y - hHuge, 2*wHuge, 2*hHuge)
                if axis == 1:
                    text = self.drawing.show_time(inc)
                else:
                    text = "{:.6g}".format(inc)
                painter.drawText(rect, text, Qt.QTextOption(Qt.Qt.AlignCenter))
            painter.scale(1.0, -1.0)

    def __draw_image(self, gl):
        tex = self.GL_profile_texture
        mesh = self.GL_image_mesh
        if tex is None or mesh is None:
            return
        with self._profile_program as p:
            image_to_model = Matrix.product(
                self.drawing.grid_to_model,
                self.drawing.image_to_grid,
            )
            image_to_world = Matrix.product(
                self.drawing.model_to_world,
                image_to_model,
            )
            p.uniforms.tex = tex
            p.uniforms.height_scale = self.drawing.height_scale
            p.uniforms.image_to_model = image_to_model
            p.uniforms.model_to_image = image_to_model.inverse()
            p.uniforms.image_to_world = image_to_world
            p.uniforms.world_to_clip = self.world_to_clip
            p.uniforms.diff_scale = self.drawing.diff_scale
            p.uniforms.profile_color = self.drawing.profile_data.color
            band_position, band_width = self.drawing.selected_band_position
            p.uniforms.selected_band_position = band_position
            p.uniforms.selected_band_width = band_width

            p.uniforms.focus_position = self.drawing.profile_data.focus_point
            p.uniforms.focus_width = 1/len(self.drawing.profile_data.values_3d[1])
            mesh.draw()

    def paintGL(self):
        gl = self.context.functions()
        gl.glEnable(GL.GL_DEPTH_TEST)
        gl.glEnable(GL.GL_BLEND)
        gl.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        gl.glClearColor(1.0,1.0,1.0,1.0)
        gl.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        major_ticks, grid_to_clip = self.__draw_grid(gl)
        self.__draw_major_ticks(gl, major_ticks, grid_to_clip)
        gl.glEnable(GL.GL_DEPTH_TEST)
        gl.glEnable(GL.GL_BLEND)
        gl.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        self.__draw_image(gl)

    def freeGL(self):
        self.dynamic_attribute("GL_profile_texture").clear()
