from typing import Optional
import math

from .__prelude__ import Qt, Matrix, Point, Scene, logger

class GLWidget(Qt.QOpenGLWidget):
    positionChanged = Qt.Signal(float, float)
    resized_viewport = Qt.Signal(int, int)

    def __init__(self, scene_info: Scene):
        super().__init__()
        self.setFocusPolicy(Qt.Qt.FocusPolicy.WheelFocus)
        self.setMouseTracking(True)
        self._scene: Scene  = scene_info
        self._scene.renderChanged.connect(self.update)
        self._initialized_scene = None
        self._initialized_scene_mods = []

        self._clip_to_pixel: Optional[Matrix]  = None
        # contains the position of the cursor (in model space) when dragging, and None otherwise
        self.dragMode = None
        self.dragStart: Optional[tuple[float, float]] = None

    @property
    def scene(self):
        return self._scene

    @property
    def clip_to_pixel(self) -> Matrix:
        if self._clip_to_pixel is None:
            w, h = float(self.width()), float(self.height())
            self._clip_to_pixel = Matrix.scale((w/2.0, -h/2.0, 1.0)) * Matrix.translate((1.0,-1.0))
        return self._clip_to_pixel

    @property
    def world_to_clip(self):
        return self.initialized_scene.world_to_clip

    def sizeHint(self):
        return Qt.QSize(100,100)

    def pixel_to_model(self, x, y) -> tuple[float,float]:
        clip_x, clip_y = self.clip_to_pixel.inverse().transform_point((x, y))
        return self.initialized_scene.clip_to_model(clip_x, clip_y)

    def mousePressEvent(self, event):
        pos = event.position()
        mods = Qt.QGuiApplication.keyboardModifiers()
        self.dragMode = mods
        self.dragStart = self._scene.startDrag(mods, self.pixel_to_model(pos.x(), pos.y()))
    def mouseReleaseEvent(self, event):
        if self.dragStart is not None:
            pos = event.position()
            self.dragStart = self._scene.endDrag(self.dragMode, self.dragStart, self.pixel_to_model(pos.x(), pos.y()))
    def mouseMoveEvent(self, event):
        pos = event.position()
        xb,yb = self.pixel_to_model(pos.x(), pos.y())
        if self.dragStart is not None:
            self.dragStart = self._scene.whileDrag(self.dragMode, self.dragStart, (xb,yb))
        self.positionChanged.emit(xb,yb)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.Qt.KeyboardModifier.NoModifier:
            if event.key() == Qt.Qt.Key.Key_Right:
                self._scene.selected_band.band_number += 1
            if event.key() == Qt.Qt.Key.Key_Left:
                self._scene.selected_band.band_number -= 1
    def keyReleaseEvent(self, event):
        if self.dragStart is not None:
            if event.modifiers() != self.dragMode:
                self._scene.abortDrag(self.dragMode, self.dragStart)
                self.dragStart = None

    def preserving_pointer(self, pos, doit):
        x_b, y_b = self.pixel_to_model(pos.x(), pos.y())
        doit()
        x_a, y_a = self.pixel_to_model(pos.x(), pos.y())
        self._scene.center += Point(x_a - x_b, y_a - y_b)

    def wheelEvent(self, event):
        angle = event.angleDelta().y() / 32.0
        mods = Qt.QGuiApplication.keyboardModifiers()
        if mods == Qt.Qt.KeyboardModifier.ShiftModifier | Qt.Qt.KeyboardModifier.ControlModifier:
            units = self._scene.heightUnits
            self._scene.heightUnits = min(1.0, max(0, units + angle/360.0))
        elif mods == Qt.Qt.KeyboardModifier.ShiftModifier:
            def doit():
                self._scene.pitch = max(0.0,min(85.0,self._scene.pitch + angle))
            self.preserving_pointer(event.position(), doit)
        elif mods == Qt.Qt.KeyboardModifier.ControlModifier:
            def doit():
                self._scene.yaw += angle
            self.preserving_pointer(event.position(), doit)
        else:
            def doit():
                self._scene.distance *= math.exp(math.log(0.25)*math.radians(angle))
            self.preserving_pointer(event.position(), doit)

    def modify_initialized_scene(self, mod):
        if self._initialized_scene is None:
            self._initialized_scene_mods.append(mod)
        else:
            mod(self._initialized_scene)

    @property
    def initialized_scene(self):
        if self._initialized_scene is None:
            self._initialized_scene = self._scene.initializeDrawing(self.context())
            for mod in self._initialized_scene_mods:
                mod(self._initialized_scene)
            self._initialized_scene_mods = []
        return self._initialized_scene

    def initializeGL(self):
        _ = self.initialized_scene

    def resizeGL(self, w, h):
        self._clip_to_pixel = None
        self.initialized_scene.resizeViewport(w, h)
        self.resized_viewport.emit(w,h)

    def paintGL(self):
        ret = self.initialized_scene.paintGL()
        return ret

    def closeEvent(self, event):
        event.accept()
        if self._initialized_scene is not None:
            self.context().makeCurrent(Qt.QOffscreenSurface())
            self._initialized_scene.freeGL()
