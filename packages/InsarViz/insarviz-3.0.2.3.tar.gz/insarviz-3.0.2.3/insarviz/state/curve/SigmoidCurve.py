import numpy as np

from .__prelude__ import Qt, dynamic, SELF
from .CurveParam import CurveParam
from .Curve import Curve

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, a_min = -500.0, a_max = 500.0)))
class SigmoidCurve(Curve):
    step          = dynamic.variable()
    initial_step  = dynamic.external()

    def __init__(self):
        super().__init__()
        self.scale = CurveParam('scale')
        self.scale.min_bound = -1.0
        self.scale.max_bound = 1.0
        self.steepness = CurveParam('steepness')
        self.step = CurveParam('step')

        self._dynamic_initial_step = SELF.step.initial[self]

    __mime_type__ = "application/x-insarviz/SigmoidCurve"

    @property
    def nparams(self):
        return 3
    @property
    def params(self):
        return [self.scale, self.steepness, self.step]

    def func(self, xs, scale, steepness, step):
        return scale * sigmoid(np.exp(steepness) * (xs - step))
    def jacobian(self, xs, scale, steepness, step):
        es = np.exp(steepness)
        sig = sigmoid(es * (xs - step))
        sig_prime = (scale * es) * sig * (1 - sig)

        return np.array([
            sig,
            (xs-step) * sig_prime,
            - sig_prime
        ])

    def hessian_epsilon(self, xs, err, grad, s, t, x0):
        et = np.exp(t)
        x_d = xs-x0
        s0 = sigmoid(et*x_d)
        s1 = s0*(1-s0)
        s2 = s1*(1-2*s0)

        et_x_d = et*x_d

        ds_ds = 0.0
        dt_ds = np.sum(err * (et_x_d*s1))
        dx0_ds = np.sum(err * (-et*s1))
        dt_dt = np.sum(err * ((s*et_x_d)*(s1 + et_x_d*s2)))
        dx0_dt = np.sum(err * (-(s*et)*(s1 + et_x_d*s2)))
        dx0_dx0 = np.sum(err * ((s*et*et)*s2))

        hessian = np.array([
            [ds_ds, dt_ds, dx0_ds],
            [dt_ds, dt_dt, dx0_dt],
            [dx0_ds, dx0_dt, dx0_dx0]
        ])
        return np.dot(hessian @ grad, grad)
