class Bound():
    def __init__(self, minx, miny, maxx, maxy):
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
        self.width = self.maxx - self.minx
        self.height =self.maxy - self.miny

    def __repr__(self):
        return '[' + str(self.minx) + ',' + str(self.miny) + ',' + str(self.maxx) + ',' + str(self.maxy) + ']'

    def contains(self, position):
        return position.x > self.minx and position.x < self.maxx and position.y > self.miny and position.y < self.maxy

class QuadItem():
    def __init__(self, cell, bound):
        self.cell = cell
        self.bound = bound

class Color():
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return '[' + str(self.r) + ',' + str(self.g) + ',' + str(self.b) + ']'

class Collision():
    def __init__(self, cell, check, d, p):
        self.cell = cell
        self.check = check
        self.d = d
        self.p = p