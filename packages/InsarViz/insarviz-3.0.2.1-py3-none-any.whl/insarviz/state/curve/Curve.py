import numpy as np

from .__prelude__ import ObservableStruct

class Curve(ObservableStruct):
    def init_from_dict(self, dct):
        for param in self.params:
            getattr(self, param.name).init_from_dict(dct[param.name])
    def to_dict(self):
        return {
            param.name: getattr(self, param.name).to_dict()
            for param in self.params
        }

    def nparams(self):
        return 0
    def params(self):
        return []

    def func(self, xs):
        return np.zeros_like(xs)
    def jacobian(self, xs):
        return np.reshape(np.array([]), (0, len(xs)))
    def hessian_epsilon(xs, err, grad):
        return 0.0
