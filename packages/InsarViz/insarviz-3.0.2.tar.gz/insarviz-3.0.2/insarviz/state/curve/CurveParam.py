import numpy as np

from .__prelude__ import ObservableStruct, dynamic

class CurveParam(ObservableStruct):
    name       = dynamic.variable()
    min_bound  = dynamic.variable()
    max_bound  = dynamic.variable()
    initial    = dynamic.variable()

    def __init__(self, name, min_bound = -np.inf, max_bound = np.inf, initial = 0.0):
        super().__init__()
        self.name = name
        self.min_bound = min_bound
        self.max_bound = max_bound
        self.initial = initial

    @classmethod
    def from_dict(cls, dct, /, **kwargs):
        return CurveParam(dct['name'], dct['min_bound'], dct['max_bound'], dct['initial'])
    def init_from_dict(self, dct):
        self.name = dct["name"]
        self.min_bound = dct["min_bound"]
        self.max_bound = dct["max_bound"]
        self.initial = dct["initial"]
    def to_dict(self):
        return {
            'name': self.name,
            'min_bound': self.min_bound,
            'max_bound': self.max_bound,
            'initial': self.initial
        }
