import numpy as np

from .CurveParam import CurveParam
from .Curve import Curve

class LinearCurve(Curve):
    def __init__(self):
        super().__init__()
        self.velocity = CurveParam("velocity")
        self.bias = CurveParam("bias")

    __mime_type__ = "application/x-insarviz/LinearCurve"

    @property
    def nparams(self):
        return 2
    @property
    def params(self):
        return [self.velocity, self.bias]

    def func(self, xs, v, b):
        return xs * v + b
    def jacobian(self, xs, v, b):
        return np.array([xs, np.ones_like(xs)])
    def hessian_epsilon(self, xs, err, grad, v, b):
        return 0.0
