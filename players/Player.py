from ..modules import *
import math

class Player:
    def __init__(self, gameServer, name = 'dummy', id = None):
        self.gameServer = gameServer
        self.name = name
        self.mouse = Vec2(0, 0)
        self.centerPos = Vec2(0, 0)
        self.cells = []
        self.frozen = False
        self.mergeOverride = False
        self.spectate = False
        self.score = 0
        self.isRemoved = False
        self.spawnmass = 0
        self.rec = False
        self.viewNodes = []
        self.lastEject = None
        self.config = gameServer.config
        self.killreward = 0
        self.killedreward = 0 

        if gameServer:
            if id is None:
                gameServer.lastPlayerId += 1
                self.pID = gameServer.lastPlayerId
            else:
                self.pID = id
            gameServer.gameMode.onPlayerInit(self)
            self.joinGame()
            self.updateView()

    def step(self, action, *kargs, **kwargs):    # Hxu: action now is a N by 3 matrix
        self.killreward = 0
        self.killedreward = 0 

        if len(self.cells) == 0:
            self.isRemoved = True
        if self.isRemoved:
            return
        
        if action[0] < -1:action[0] = -1
        if action[1] < -1:action[1] = -1
        if action[0] >  1:action[0] = 1
        if action[1] >  1:action[1] = 1

        # action in format [0] mouse x, [1 mouse y, [2] key space bool, [3] key w bool, [4] no key bool
        assert action[0] >= -1 and action[0] <= 1 and action[1] >= -1 and action[1] <= 1
        self.mouse = self.centerPos.add(Vec2(action[0] * self.gameServer.config.serverViewBaseX, action[1] * self.gameServer.config.serverViewBaseY), 1)
        # assert np.sum(action[2:]) == 1
        if action[2] == 0:
            self.pressSpace()
        elif action[2] == 1:
            self.pressW()
        elif action[2] == 2:
            pass

        # self.updateView()

    def updateView(self):
        if self.isRemoved:
            return
        cx = 0
        cy = 0
        for cell in self.cells:
            cx += cell.position.x / len(self.cells)
            cy += cell.position.y / len(self.cells)
        self.centerPos = Vec2(cx , cy)
        scale = max(self.getScale(), self.gameServer.config.serverMinScale)
        halfWidth = (self.gameServer.config.serverViewBaseX + 100) / scale / 2
        halfHeight = (self.gameServer.config.serverViewBaseY + 100) / scale / 2
        self.viewBox = Bound(
            self.centerPos.x - halfWidth,
            self.centerPos.y - halfHeight,
            self.centerPos.x + halfWidth,
            self.centerPos.y + halfHeight)

        self.viewNodes = []
        self.gameServer.quadTree.find(self.viewBox, lambda check: self.viewNodes.append(check))
        if self.cells:
            self.maxradius = max(self.cells, key = lambda c : c.radius).radius
        else:
            self.maxradius = 0
        # self.viewNodes+=self.cells
        # render_order = {1: 0, 0: 1, 3: 2, 2: 3}
        # self.viewNodes = sorted(self.viewNodes, key=lambda x: x.size)

    def pressSpace(self):
        if self.gameServer.run:
            if len(self.cells) <= 2:
                self.mergeOverride = False
            if self.mergeOverride or self.frozen:
                return
        self.gameServer.splitCells(self)

    def pressW(self):
        if self.spectate or not self.gameServer.run:
            return
        self.gameServer.ejectMass(self)

    def setCenterPos(self, p):
        p.x = max(p.x, self.gameServer.border.minx)
        p.y = max(p.y, self.gameServer.border.miny)
        p.x = min(p.x, self.gameServer.border.maxx)
        p.y = min(p.y, self.gameServer.border.maxy)
        self.centerPos = p

    def getScale(self):
        scale = 0
        for cell in self.cells:
            scale += cell.radius
            self.score += cell.mass
        if scale == 0:
            self.scale = 0.4
        else:
            rate = 1.0
            if self.pID < self.gameServer.env.num_agents:rate = 1.5
            self.scale = math.pow(min(64 / scale, 1), 0.4) / rate
        return self.scale

    def joinGame(self):
        if self.cells:
            return
        self.gameServer.gameMode.onPlayerSpawn(self.gameServer, self)

    def get_view_box(self):
        # notice y positive is upward in opanai gym!
        return [self.viewBox.minx, self.viewBox.maxx, self.viewBox.miny, self.viewBox.maxy]
    
    def in_view(self, node):
        return node.x >= self.viewBox.minx and node.x <= self.viewBox.maxx and node.y >= self.viewBox.miny and node.y <= self.viewBox.maxy

    def maxcell(self):
        return max(self.cells, key=lambda c: c.radius)

    def mincell(self):
        return max(self.cells, key=lambda c: c.radius)

