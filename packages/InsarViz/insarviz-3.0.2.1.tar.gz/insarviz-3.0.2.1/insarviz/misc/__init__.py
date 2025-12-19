from .                 import Qt, bresenham
from .Matrix           import Matrix
from .DEMTexture       import DEMTexture, unit_square_to_image
from .Point            import Point
from .Bound            import Bound
from .ComputedValue    import ComputedValue
from .Base10Increments import Base10Increments
from .Threads          import Runnable, GLOBAL_THREAD_POOL
from .GLProgram        import GLProgram

def linmap(A,B):
    """Given an interval [A, B], return a pair of affine functions (f, g)
    such that f(A) = -1 and f(B) = 1, and g(-1) = A and g(1) = B.

    These functions allow for efficient computing of affine mappings
    between [A,B] and [-1,1], both for scalar values and NumPy arrays.
    """
    s = A+B
    d = B-A
    if d==0.0:
        # if we map a null interval, map it to the identity
        d = 2.0
        s = 0.0

    a_from = 2.0 / d
    b_from = - s / d
    def from_lin(x):
        return a_from * x + b_from

    a_to = d / 2.0
    b_to = s / 2.0
    def to_lin(x):
        return a_to * x + b_to

    return (from_lin,to_lin)
