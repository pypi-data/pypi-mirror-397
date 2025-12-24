# -*- coding: utf-8 -*-

"""Bresenham algorithm for line drawing."""


def line(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """returns list of indices of pixels for the line from (x0, y0) to (x1, y1)

    both ends are included.

    Parameters
    ----------
    x0 : int
        row of first point
    y0 : int
        col of first point
    x1 : int
        row of second point
    y1 : int
        col of second point

    Examples
    --------
    >>> from insarviz.bresenham import line
    >>> import numpy as np
    >>> X0, Y0, X1, Y1 = 0, 0, 4, 3
    >>> res = line(X0, Y0, X1, Y1)
    >>> print(res, type(res)==list, type(res[0])==tuple)
    [(0, 0), (1, 1), (2, 2), (3, 2), (4, 3)] True True
    """

    idxs: list[tuple[int, int]] = []
    dx, dy = x1-x0, y1-y0

    xsign = 1 if dx > 0 else -1
    ysign = 1 if dy > 0 else -1

    dx, dy = abs(dx), abs(dy)

    if dx > dy:
        xx, xy, yx, yy = xsign, 0, 0, ysign
    else:
        dx, dy = dy, dx
        xx, xy, yx, yy = 0, ysign, xsign, 0

    D = 2*dy - dx
    y = 0

    for x in range(dx + 1):
        idxs += [(x0 + x*xx + y*yx, y0 + x*xy + y*yy)]
        if D >= 0:
            y += 1
            D -= 2*dx
        D += 2*dy
    return idxs
