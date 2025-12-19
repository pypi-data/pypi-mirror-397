from typing import TypeVar

from .__prelude__ import ObservableStruct, dynamic, Qt

GenericDrawing = TypeVar("GenericDrawing", covariant=True)

class InitializedDrawing[GenericDrawing](ObservableStruct):
    context = dynamic.readonly()
    drawing = dynamic.readonly()
    viewport_size = dynamic.readonly()

    def __init__(self, context: Qt.QOpenGLContext, drawing: GenericDrawing):
        super().__init__()
        self._context = context
        self._drawing = drawing
        self._viewport_size = (1,1)

    def resizeViewport(self, w, h, /):
        self._viewport_size = (w,h)
    def paintGL(self):
        pass
    def freeGL(self):
        pass

class GLDrawing(ObservableStruct):
    renderChanged = Qt.Signal()

    def initializeDrawing(self, context: Qt.QOpenGLContext, /) -> InitializedDrawing["GLDrawing"]:
        return InitializedDrawing(context, self)
