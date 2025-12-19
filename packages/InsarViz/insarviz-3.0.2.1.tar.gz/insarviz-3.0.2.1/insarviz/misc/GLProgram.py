from contextlib import ExitStack
import ctypes
import numpy as np
from OpenGL import GL
from shiboken6 import VoidPtr

from . import Qt, Matrix, Point, Bound

class GLUniform:
    def __init__(self, name, value):
        self.__name = name
        self.__value = value
        self.__release = lambda: None
        if isinstance(value, Matrix):
            self.__bind_in = self.__bind_matrix
        elif isinstance(value, int):
            self.__bind_in = lambda program: program.setUniformValue1i(self.__name, self.__value)
        elif isinstance(value, float):
            self.__bind_in = lambda program: program.setUniformValue1f(self.__name, self.__value)
        elif isinstance(value, Qt.QColor):
            self.__bind_in = self.__bind_color
        elif isinstance(value, list):
            self.__bind_in = lambda program: program.setUniformValue(self.__name, *self.__value)
        else:
            self.__bind_in = self.__bind_texture
            self.__release = lambda: self.__value.release()

    def __bind_matrix(self, program):
        w, h = self.__value.shape
        if w == 2:
            cons = Qt.QMatrix2x2
        elif w == 3:
            cons = Qt.QMatrix3x3
        else:
            cons = Qt.QMatrix4x4
        program.setUniformValue(self.__name, cons(self.__value.flatten()))
    def __bind_texture(self, program):
        next_id = program.alloc_id()
        self.__value.bind(next_id)
        program.setUniformValue1i(self.__name, next_id)
    def __bind_color(self, program):
        col = self.__value
        program.setUniformValue(self.__name, col.red()/255.0, col.green()/255.0, col.blue()/255.0, col.alpha()/255.0)

    def bind(self, program):
        return self.__bind_in(program)
    def release(self):
        self.__release()

FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)

def splitTriangle(n, points, i0, i1, i2):
    """Split a triangle in 2^n, by splitting its longest side, and
    creating two smaller triangles, then recursively splitting each of
    those 2^(n-1) times.

    The 'points' input is an array of points. i0, i1 and i2 are
    indices into that array, describing a triangle whose longest side
    joins i0 and i2.

    The functions will store new points into that array destructively,
    and return the indices of all newly-created triangles.
    """
    if n==0:
        return [i0,i1,i2]
    else:
        imid = len(points)
        mid = (points[i0] + points[i2]) * 0.5
        points.append(mid)
        new_triangles_1 = splitTriangle(n-1, points, i1, imid, i0)
        new_triangles_2 = splitTriangle(n-1, points, i2, imid, i1)
        return new_triangles_1 + new_triangles_2

DEFAULT_TEXTURE_TO_MODEL = Matrix.product(
    Matrix.translate((-1,-1)),
    Matrix.scale((2,2,1)),
)

class GLProgram(Qt.QOpenGLShaderProgram):
    class __Mesh:
        def __init__(self, program, mesh_type, attribs, vertex_data, index_data = None):
            self.__program = program
            self.__mesh_type = mesh_type
            self.__vao = Qt.QOpenGLVertexArrayObject()
            self.__vao.create()

            gl = program.gl()
            with Bound(self.__vao):
                num_vertices, record_count = vertex_data.shape
                record_size = record_count * FLOAT_SIZE

                vbuf = Qt.QOpenGLBuffer(Qt.QOpenGLBuffer.Type.VertexBuffer)
                vbuf.create()
                vbuf.setUsagePattern(Qt.QOpenGLBuffer.UsagePattern.StaticDraw)
                vbuf.bind()
                vbuf.allocate(bytes(vertex_data), vertex_data.nbytes)

                offset = 0
                for name, attrib_count in attribs:
                    loc = program.attributeLocation(name)
                    if loc == -1:
                        offset += attrib_count
                        continue
                    gl.glEnableVertexAttribArray(loc)
                    gl.glVertexAttribPointer(loc, attrib_count, GL.GL_FLOAT, GL.GL_FALSE, record_size, VoidPtr(offset * FLOAT_SIZE))
                    offset += attrib_count

                if index_data is not None:
                    indices = Qt.QOpenGLBuffer(Qt.QOpenGLBuffer.Type.IndexBuffer)
                    indices.create()
                    indices.setUsagePattern(Qt.QOpenGLBuffer.UsagePattern.StaticDraw)
                    indices.bind()
                    indices.allocate(bytes(index_data), index_data.nbytes)

                    self.__has_indices = True
                    self.__num_vertices = len(index_data)
                else:
                    self.__has_indices = False
                    self.__num_vertices = num_vertices

        def draw(self):
            gl = self.__program.gl()
            with Bound(self.__vao):
                if self.__has_indices:
                    gl.glDrawElements(self.__mesh_type, self.__num_vertices, GL.GL_UNSIGNED_INT, VoidPtr(0))
                else:
                    gl.glDrawArrays(self.__mesh_type, 0, self.__num_vertices)

    class __Activated:
        class __Uniforms:
            def __init__(self, stack, program):
                self.__program = program
                self.__stack = stack

            def __setattr__(self, attr, val):
                if attr.startswith('_'):
                    super().__setattr__(attr, val)
                else:
                    uni = GLUniform(attr, val)
                    self.__stack.enter_context(Bound(uni, self.__program))

        def __init__(self, stack, program):
            self.__uniforms = self.__Uniforms(stack, program)

        @property
        def uniforms(self):
            return self.__uniforms

    def __init__(self, shaders):
        super().__init__()
        self.__context = Qt.QOpenGLContext.currentContext()
        assert self.__context is not None
        self.__exit_stack = ExitStack()
        self.__current_id = 0

        for shader in shaders:
            shader.compile(self)
        self.link()

    def gl(self):
        return self.__context.functions()

    def alloc_id(self):
        ret = self.__current_id
        self.__current_id += 1
        return ret

    def create_mesh(self, mesh_type, attribs, vertex_data, index_data = None):
        return self.__Mesh(self, mesh_type, attribs, vertex_data, index_data = index_data)

    def create_grid_mesh(self, attrib, w, h):
        h_inc = 1.0/h
        w_inc = 1.0/w

        ln = h_inc * np.arange(h+1)
        ln_x0 = np.stack([np.zeros_like(ln), ln], axis=-1)
        ln_x1 = np.stack([w_inc * np.ones_like(ln), ln], axis=-1)

        strip_line = np.reshape(np.stack([ln_x0, ln_x1], axis=1), (1, 2*(h+1), 2))

        a = np.tile(np.array([[[1,1]], [[1,-1]]]), ((w+1)//2,1,1))[:w,:,:]
        b = np.tile(np.array([[[0,0]], [[0,1]]]), ((w+1)//2,1,1))[:w,:,:]
        base = np.reshape(np.arange(w), (w, 1, 1)) * np.array([[[w_inc, 0.0]]])

        grid = np.reshape(a*strip_line + (b + base), (2*w*(h+1), 2)).astype(np.float32)

        return self.__Mesh(self, GL.GL_TRIANGLE_STRIP, [(attrib, 2)], grid)

    def create_square_mesh(self, mesh_type, split = 0, texture_to_model = DEFAULT_TEXTURE_TO_MODEL):
        vpoints = [Point(0.0,0.0), Point(1.0, 0.0), Point(1.0, 1.0), Point(0.0,1.0)]
        vinds = splitTriangle(split, vpoints, 0, 1 ,2)
        vinds += splitTriangle(split, vpoints, 2, 3, 0)
        vertex_data = np.array([
            [*texture_to_model.transform_point((p.x,p.y)), 0.0, p.x, p.y]
            for p in vpoints
        ]).astype(np.float32)
        return self.__Mesh(self, mesh_type, [("vertex_model_coord", 3), ("vertex_texcoord", 2)],
                           vertex_data, np.array(vinds, dtype="uint32"))

    def __enter__(self):
        stack = self.__exit_stack.__enter__()
        stack.enter_context(Bound(self))
        self.__current_id = 0
        return self.__Activated(stack, self)
    def __exit__(self, *args):
        return self.__exit_stack.__exit__(*args)

def example():
    prog = GLProgram([...])

    mesh = prog.create_mesh(
        GL.GL_TRIANGLES,
        [("vertex_model_coord", 3), ("vertex_tex_coord", 2)],
        np.array([[...], [...], ...]),
        index_data = np.array([0,1,2,...], dtype="uint32")
    )

    with prog as gl:
        gl.uniforms.opacity = 0.5
        gl.uniforms.main_texture = tex
        mesh.draw()
