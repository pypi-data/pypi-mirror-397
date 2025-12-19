import numpy as np

from .CurveParam import CurveParam
from .Curve import Curve

class ScaledStepCurve(Curve):
    def __init__(self):
        super().__init__()
        self.scale = CurveParam("scale")
        self.step = 0.0

    __mime_type__ = "application/x-insarviz/ScaledStepCurve"

    @property
    def nparams(self):
        return 1
    @property
    def params(self):
        return [self.scale]

    def func(self, xs, scale):
        return scale * np.where(xs >= self.step, xs, 0.0)
    def jacobian(self, xs, scale):
        return np.array([np.where(xs >= self.step, xs, 0.0)])
    def hessian_epsilon(self, xs, err, grad, v, b):
        return 0.0
