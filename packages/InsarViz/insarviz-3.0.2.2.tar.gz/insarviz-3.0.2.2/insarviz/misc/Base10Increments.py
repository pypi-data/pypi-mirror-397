import math

class Base10Increments:
    MAJOR_INCREMENT = 0
    MINOR_INCREMENT = 1

    @classmethod
    def _gen_increments(cls,a,b):
        order = math.floor(math.log((b-a), 10))
        increment = (10.0**order)
        if (b-a) / increment < 5:
            order -= 1
            increment = (10.0**order)
        rng = (b-a)/increment
        start_n = math.ceil(a/increment)
        start = start_n*increment
        mod = start_n % 10
        count = math.ceil(rng)
        major_inc = 1
        if count >= 20:
            major_inc = 5
        elif count >= 10:
            major_inc = 2
        for i in range(count):
            inc_type = cls.MAJOR_INCREMENT if (mod+i) % major_inc == 0 else cls.MINOR_INCREMENT
            val = start+i*increment
            if val <= b:
                yield inc_type, val

    def __init__(self, a, b):
        if a <= b:
            self._a, self._b = a, b
        else:
            self._a, self._b = b, a

    def __iter__(self):
        return self._gen_increments(self._a, self._b)
