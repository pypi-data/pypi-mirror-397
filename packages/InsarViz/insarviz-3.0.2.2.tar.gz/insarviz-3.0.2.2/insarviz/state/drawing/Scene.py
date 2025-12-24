from typing import TypeVar
from .__prelude__ import SelectedBand, Matrix, Point, Qt, dynamic
from .GLDrawing import GLDrawing, InitializedDrawing

GenericScene = TypeVar("GenericScene", bound="Scene", covariant=True)

class SceneDrawing[GenericScene](InitializedDrawing[GenericScene]):
    def __init__(self, context: Qt.QOpenGLContext, scene: GenericScene):
        super().__init__(context, scene)

    @property
    def world_to_clip(self):
        return Matrix.identity(4)

    def clip_to_model(self, clip_x, clip_y):
        clip_to_model = Matrix.product(self.world_to_clip, self.drawing.model_to_world).inverse()

        v1_model = clip_to_model.transform_point((clip_x, clip_y, -0.5))
        v2_model = clip_to_model.transform_point((clip_x, clip_y, 0.5))
        ray_direction = v2_model - v1_model

        zMul = -v2_model[2]/ray_direction[2]
        return (v2_model[0]+ray_direction[0]*zMul, v2_model[1]+ray_direction[1]*zMul)

class Scene(GLDrawing):
    center          = dynamic.variable(Point(0.0, 0.0))
    heightUnits     = dynamic.variable(0.0)
    distance        = dynamic.variable(0.0)
    yaw             = dynamic.variable(0.0)
    pitch           = dynamic.variable(0.0)
    model_to_world  = dynamic.variable(Matrix.identity(4))

    def startDrag(self,  __dragMode__: Qt.Qt.KeyboardModifier, dragPrev: tuple[float, float]):
        return dragPrev
    def whileDrag(self, __dragMode__: Qt.Qt.KeyboardModifier, dragPrev: tuple[float, float], __dragNext__: tuple[float, float], /):
        return dragPrev
    def endDrag(self, __dragMode__: Qt.Qt.KeyboardModifier, __dragPrev__: tuple[float, float], __dragNext__: tuple[float, float], /):
        return None
    def abortDrag(self,  __dragMode__: Qt.Qt.KeyboardModifier, dragPrev: tuple[float, float]):
        pass

    def initializeDrawing(self, context, /):
        return SceneDrawing(context, self)
