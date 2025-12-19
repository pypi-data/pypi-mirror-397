import numpy as np

from .Curve import Curve

class CurveSum(Curve):
    def __init__(self, *curves):
        super().__init__()
        self.curves = curves

    @property
    def nparams(self):
        return sum((c.nparams for c in self.curves))
    @property
    def params(self):
        return sum((curve.params for curve in self.curves), [])

    def func(self, xs, *params):
        ret = np.zeros_like(xs)
        for curve in self.curves:
            lparams = curve.nparams
            ret = ret + curve.func(xs, *params[:lparams])
            params = params[lparams:]
        return ret
    def jacobian(self, xs, *params):
        ret = []
        for curve in self.curves:
            lparams = curve.nparams
            ret.append(curve.jacobian(xs, *params[:lparams]))
            params = params[lparams:]
        return np.concatenate(ret)

    def hessian_epsilon(self, xs, err, grad, *params):
        ret = 0.0
        for curve in self.curves:
            lparams = curve.nparams
            ret += curve.hessian_epsilon(xs, err, grad[:lparams], *params[:lparams])
            params = params[lparams:]
            grad = grad[lparams:]
        return ret
