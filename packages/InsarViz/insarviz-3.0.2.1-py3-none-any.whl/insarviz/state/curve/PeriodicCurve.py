import numpy as np
import math

from .__prelude__ import dynamic, SELF
from .CurveParam import CurveParam
from .Curve import Curve

class PeriodicCurve(Curve):
    phase      = dynamic.variable()
    amplitude  = dynamic.variable()
    period     = dynamic.variable(1.0)

    def __init__(self):
        super().__init__()
        self.phase = CurveParam("phase")
        self.amplitude = CurveParam("amplitude")
        self.amplitude.initial = 1.0
        self.period = 1.0

    __mime_type__ = "application/x-insarviz/PeriodicCurve"
    def init_from_dict(self, dct):
        super().init_from_dict(dct)
    def to_dict(self):
        return dict(super().to_dict(), period = self.period)

    @property
    def nparams(self):
        return 2
    @property
    def params(self):
        return [self.amplitude, self.phase]
    @dynamic.memo(SELF.period)
    def frequency(self):
        freq = 2.*math.pi / self.period
        return freq

    def func(self, xs, a, phi):
        return a*np.cos(self.frequency * xs + phi)
    def jacobian(self, xs, a, phi):
        xs_lin = self.frequency * xs + phi
        xcos = np.cos(xs_lin)
        xsin = np.sin(xs_lin)
        return np.array([xcos,-a*xsin])
    def hessian_epsilon(self, xs, err, grad, a, phi):
        xs_lin = self.frequency * xs + phi
        xcos = np.cos(xs_lin)
        xsin = np.sin(xs_lin)

        da_da = 0.0
        da_dphi = -np.sum(err*xsin)
        dphi_dphi = -a*np.sum(err*xcos)
        hessian = np.array([
            [da_da, da_dphi],
            [da_dphi, dphi_dphi]
        ])
        return np.dot(hessian @ grad, grad)
