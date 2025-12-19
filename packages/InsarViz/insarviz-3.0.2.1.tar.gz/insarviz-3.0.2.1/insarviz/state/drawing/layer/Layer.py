import numpy as np
from OpenGL import GL

from .__prelude__ import (
    Qt, ObservableStruct, ColorMap, colormaps, dynamic,
    Bound, inOpenGLContext, OpenGLPainter
)

class ExistingTexture:
    def __init__(self, texture_id):
        self.__texture_id = texture_id
    def destroy(self):
        arr = np.array([self.__texture_id])
        GL.glDeleteTextures(1, arr)

    def bind(self, index = 0):
        GL.glActiveTexture(int(GL.GL_TEXTURE0) + index)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.__texture_id)
    def release(self):
        pass
    def create(self):
        pass

class Layer(ObservableStruct):
    LAYER_ID = 0

    is_enabled = dynamic.variable(True)
    is_removable = True

    renderChanged = Qt.Signal()

    def __init__(self):
        super().__init__()
        self.__layer_id = self.LAYER_ID
        Layer.LAYER_ID += 1

    @dynamic.memo()
    def shaders(self):
        return []

    @property
    def layer_id(self):
        return self.__layer_id

    def local_ident(self, ident):
        return f"layer_{self.layer_id}_{ident}"
    def local_idents(self, *idents):
        return { ident: self.local_ident(ident) for ident in idents }

    def GL_initialize(self, context):
        raise NotImplementedError

class InitializedLayer(ObservableStruct):
    class __LocalUniforms:
        def __init__(self, layer, uni):
            self.__uniforms = uni
            self.__layer = layer
        def __setattr__(self, attr, val):
            if attr.startswith('_'):
                super().__setattr__(attr, val)
            else:
                setattr(self.__uniforms, self.__layer.local_ident(attr), val)

    layer = dynamic.readonly()
    context = dynamic.readonly()

    def __init__(self, context, layer):
        super().__init__()
        self._layer = layer
        self._context = context

    def local_uniforms(self, uni):
        return self.__LocalUniforms(self.layer, uni)

    def GL_create_shared_context(self):
        ret = Qt.QOpenGLContext()
        ret.setShareContext(self.context)
        ret.create()
        return ret

    def GL_paint_into_texture(self, w, h, shared_context, draw):
        fbo = Qt.QOpenGLFramebufferObject(w, h, Qt.QOpenGLFramebufferObject.Attachment.CombinedDepthStencil, target = GL.GL_TEXTURE_2D)
        def run():
            with Bound(fbo):
                gl = shared_context.functions()
                gl.glViewport(0,0,w,h)
                gl.glClearColor(0.0, 0.0, 0.0, 0.0)
                gl.glClear(GL.GL_COLOR_BUFFER_BIT)
                with OpenGLPainter(w,h) as painter:
                    draw(painter)
        inOpenGLContext(run, shared_context)
        return ExistingTexture(fbo.takeTexture())

    @dynamic.memo()
    def GL_setup(self):
        return lambda prog: None

    def GL_free(self):
        pass
