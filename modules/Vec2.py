# An object representing a 2D vector.
# Based on the Vector2 class from LibGDX.
import math

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'


    def add(self, d, m = 1.):
        self.x += d.x * m
        self.y += d.y * m
        return self

    def sub(self, x, y=None):
        if isinstance(x, Vec2):
            self.x -= x.x
            self.y -= x.y
        else:
            self.x -= x
            self.y -= y

        return self


    def sub2(self, d, m):
        self.x -= d.x * m
        self.y -= d.y * m
        return self


    def angle(self):
        return math.atan2(self.x, self.y)


    def clone(self):
        return Vec2(self.x, self.y)


    def dist(self):
        return self.x ** 2 + self.y ** 2


    def sqDist(self):
        return math.sqrt(self.dist())


    def normalize(self):
        return self.scale(1/self.sqDist())


    def scale(self, scaleX, scaleY = None):
        self.x *= scaleX
        self.y *= scaleY or scaleX
        return self
