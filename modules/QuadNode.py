from .GameAbstractions import *

def disjoint(a, b):
    return b.minx > a.maxx or b.maxx < a.minx or b.miny > a.maxy or b.maxy < a.miny

class QuadNode:
    def __init__(self, bound, maxChildren, maxLevel, level = 0, parent = None):
        self.halfWidth = (bound.maxx - bound.minx) / 2
        self.halfHeight = (bound.maxy - bound.miny) / 2
        self.parent = parent
        self.level = level
        self.maxLevel = maxLevel
        self.maxChildren = maxChildren
        # self.bound = Bound(bound.minx, bound.miny, bound.maxx, bound.maxy)
        self.bound = bound
        self.bound.cx = bound.minx + self.halfWidth
        self.bound.cy = bound.miny + self.halfHeight

        self.childNodes = []
        self.items = []


    def insert(self, item):
        if self.childNodes:
            quad = self.getQuad(item.bound)
            if quad != -1:
                self.childNodes[quad].insert(item)
                return

        self.items.append(item)
        item.quadNode = self  # used for quick search quad node by item

        if self.childNodes or self.level >= self.maxLevel or len(self.items) <  self.maxChildren:
            return

        # split and rebalance current node
        if not self.childNodes:
            # split into 4 subnodes (top, left, bottom, right)
            w = self.halfWidth
            h = self.halfHeight
            my = self.bound.miny
            mx = self.bound.minx
            mh = my + h
            mw = mx + w
            b0 = Bound(mw, my, mw + w, my + h)
            b1 = Bound(mx, my, mx + w, my + h)
            b2 = Bound(mx, mh, mx + w, mh + h)
            b3 = Bound(mw, mh, mw + w, mh + h)
            self.childNodes.append(QuadNode(b0, self.maxChildren, self.maxLevel, self.level+1, self))
            self.childNodes.append(QuadNode(b1, self.maxChildren, self.maxLevel, self.level+1,  self))
            self.childNodes.append(QuadNode(b2, self.maxChildren, self.maxLevel, self.level+1,  self))
            self.childNodes.append(QuadNode(b3, self.maxChildren, self.maxLevel, self.level+1,  self))

            for item in self.items:
                quad = self.getQuad(item.bound)
                if quad != -1:
                    self.items.remove(item)
                    item.quadNode = None
                    self.childNodes[quad].insert(item)

    def remove(self, item):
        if item.quadNode is not self:
            item.quadNode.remove(item)
            return
        self.items.remove(item)
        item.quadNode = None
        self.cleanup(self)

    def cleanup(self, node):
        if not node.parent or node.items:
            return
        for child in node.childNodes:
            if child.childNodes or child.items:
                return
        node.childNodes  = []
        self.cleanup(node.parent)

    def update(self, item):
        self.remove(item)
        self.insert(item)

    def clear(self):
        for item in self.items:
            item.quadNode = None
        self.items = []
        for childnode in self.childNodes:
            childnode.clear()
        self.childNodes = []

    def contains(self, item):
        if not item.quadNode:
            return False
        if item.quadNode != self:
            return item.quadNode.contains(item)
        return item in self.items



    def find(self, bound, callback):
        if self.childNodes:
            quad = self.getQuad(bound)
            if quad != -1:
                self.childNodes[quad].find(bound, callback)
            else:
                for node in self.childNodes:
                    if not disjoint(node.bound, bound):
                        node.find(bound, callback)

        for item in self.items:
            if not disjoint(item.bound, bound):
                callback(item.cell)

    # Returns quadrant for the bound.
    # Returns -1 if bound cannot completely fit within a child node
    def getQuad(self, bound):
        isTop = bound.maxy < self.bound.cy
        if bound.maxx < self.bound.cx:
            if isTop:
                return 1
            elif bound.miny > self.bound.cy:
                return 2 # isBottom
        elif bound.minx > self.bound.cx: # isRight
            if isTop:
                return 0
            elif bound.miny > self.bound.cy:
                return 3 # isBottom
        return -1 # cannot fit (too large radius)


