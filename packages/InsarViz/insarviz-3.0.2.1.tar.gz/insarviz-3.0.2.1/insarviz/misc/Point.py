class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y)
    def __div__(self, x):
        return Point(self.x / x, self.y / x)
    def __mul__(self, x):
        return Point(self.x * x, self.y * x)
    def __str__(self):
        return str((self.x, self.y))
    def __repr__(self):
        return repr((self.x, self.y))
