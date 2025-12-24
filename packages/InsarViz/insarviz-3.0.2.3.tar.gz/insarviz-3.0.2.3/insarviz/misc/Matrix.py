from typing import Iterable
import numpy as np
from numpy.typing import NDArray

class Matrix:
    def __init__(self, coefs, inv_coefs):
        self.coefs = coefs
        self.inv_coefs = inv_coefs

    def inverse(self):
        return Matrix(self.inv_coefs, self.coefs)
    def transform_vect(self, vect):
        return (self * Matrix.vector(vect)).flatten()
    def transform_point(self, vect: Iterable[float]) -> NDArray[float]:
        return (self * Matrix.vector((*vect, 1.0))).flatten_homogeneous()
    def flatten(self):
        return self.coefs.flatten()
    def flatten_homogeneous(self):
        ret = self.coefs.flatten()
        dim = len(ret)
        return np.delete(ret, dim-1) / ret[dim-1]
    @property
    def shape(self):
        return self.coefs.shape

    @property
    def shape(self):
        return self.coefs.shape

    @staticmethod
    def extend(n, i):
        ident = np.fromfunction(lambda i,j: np.where(i==j, 1.0, 0.0), (n, n))
        return Matrix(np.delete(ident, i, axis=1), np.delete(ident, i, axis=0))

    @staticmethod
    def extended(n, i, m):
        ext = Matrix.extend(n,i)
        return Matrix.product(
            ext,
            m,
            ext.inverse()
        )

    @staticmethod
    def vector(v):
        n = len(v)
        va = np.array(v)
        return Matrix(np.reshape(va, (n,1)), np.reshape(va, (1,n)) / np.dot(va, va))

    @staticmethod
    def identity(n):
        ident = np.fromfunction(lambda i,j: np.where(i==j, 1.0, 0.0), (n, n))
        return Matrix(ident, ident)
    @staticmethod
    def translate(d):
        n = len(d)
        column = np.reshape(np.array([*d] + [0.0], dtype=float), (n+1,1))
        forward = np.fromfunction(lambda i,j: np.where(i==j,1.0,0.0) + np.where(np.logical_and(j==n, i<n), column, 0.0), (n+1, n+1))
        backward = np.fromfunction(lambda i,j: np.where(i==j,1.0,0.0) + np.where(np.logical_and(j==n, i<n), -column, 0.0), (n+1, n+1))
        return Matrix(forward, backward)

    @staticmethod
    def project(u):
        n = len(u)
        return (np.reshape(u,(n,1)) @ np.reshape(u,(1,n))) / np.dot(u,u)
    @staticmethod
    def reflect(u_tup):
        pu = Matrix.project(np.array(u_tup))
        return Matrix(2*pu, 2*pu) - Matrix.identity(len(u_tup))
    @staticmethod
    def rotate_xy(n,alpha):
        alpha_rad = alpha * np.pi / 180.0
        c, s = np.cos(alpha_rad), np.sin(alpha_rad)
        ret = np.fromfunction(lambda i, j: np.where(i==j, 1.0, 0.0), (n,n))
        ret[0,0] = c
        ret[1,0] = s
        ret[0,1] = -s
        ret[1,1] = c
        return Matrix(ret, np.moveaxis(ret, 1, 0))
    @staticmethod
    def rotate(u_tup, v_tup):
        u = np.array(u_tup)
        v = np.array(v_tup)
        un = u / np.sqrt(np.dot(u,u))
        vn = v / np.sqrt(np.dot(v,v))
        return Matrix.reflect(un+vn) * Matrix.reflect(vn)

    @staticmethod
    def swap_axes(n, i0, j0):
        def value_at(i,j):
            x = np.where(np.logical_or(i==i0,i==j0), -i + (i0+j0), i)
            return np.where(x==j, 1.0, 0.0)
        forward = np.fromfunction(value_at, (n, n))
        return Matrix(forward, forward)

    @staticmethod
    def scale(factors):
        f = np.array(factors)
        n = len(factors)
        forward = np.fromfunction(lambda i,j: np.where(i==j, f, 0.0), (n,n))
        backward = np.fromfunction(lambda i,j: np.where(i==j, 1/f, 0.0), (n,n))
        return Matrix(forward, backward)

    @staticmethod
    def frustum(l, r, b, t, n, f):
        w, h, d = r-l, t-b, f-n
        x0 = 2.*n/w
        x1 = (r+l)/w
        x2 = 2.*n/h
        x3 = (t+b)/h
        x4 = -(f+n)/d
        x5 = -2.*f*n/d
        forward = np.array([[x0, 0., x1 , 0.],
                            [0., x2, x3,  0.],
                            [0., 0., x4,  x5],
                            [0., 0., -1., 0.]])
        backward = np.array([
            [1/x0, 0.0, 0.0, x1/x0],
            [0.0, 1/x2, 0.0, x3/x2],
            [0.0, 0.0, 0.0, -1.0  ],
            [0.0, 0.0, 1/x5, x4/x5]
        ])
        return Matrix(forward, backward)

    @staticmethod
    def rotate3(alpha, norm):
        return Matrix.rotate((0.0,0.0,1.0,0.0), norm) * Matrix.rotate_xy(4, alpha) * Matrix.rotate(norm, (0.0,0.0,1.0,0.0))

    @staticmethod
    def product(m, *ms) -> "Matrix":
        ret = m
        for mat in ms:
            ret = ret * mat
        return ret

    def __mul__(self, m):
        return Matrix(self.coefs @ m.coefs, m.inv_coefs @ self.inv_coefs)
    def __add__(self, m):
        return Matrix(self.coefs + m.coefs, self.inv_coefs + m.inv_coefs)
    def __sub__(self, m):
        return Matrix(self.coefs - m.coefs, self.inv_coefs - m.inv_coefs)
    def __repr__(self):
        return repr((self.coefs, self.inv_coefs))
