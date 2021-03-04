import math
from ..modules import *

class Cell:
    def __init__(self, gameServer, owner, position, radius):
        self.gameServer = gameServer
        self.owner = owner #playerTracker that owns this cell
        self.color = Color(0,0,0)
        self.size = 0
        self.radius = 0
        self.mass = 0
        self.cellType = -1 #0 = Player Cell, 1 = Food, 2 = Virus, 3 = Ejected Mass
        self.isSpiked = False #If true, then this cell has spikes around it
        self.isAgitated = False #If true, then this cell has waves on it's outline
        self.killedBy = None
        self.isMoving = False
        self.boostDistance = 0
        self.boostDirection = Vec2(1, 0)
        self.quadItem = None
        self.isRemoved = False

        if self.gameServer:
            self.tickOfBirth = self.gameServer.tickCounter
            self.nodeId = self.gameServer.lastNodeId
            self.gameServer.lastNodeId += 1
            self.setRadius(radius)
            self.position = position.clone()
            self.last_position = position.clone()

    def setRadius(self, radius):
        self.radius = radius
        self.size = radius * radius
        self.mass = self.size / 100

    def canEat(self, cell):
        return False

    def getAge(self):
        return self.gameServer.tickCounter - self.tickOfBirth

    def onEat(self, prey):
        if not self.gameServer.config.playerBotGrow:
            if self.radius >= 250 and prey.radius<=41 and prey.cellType == 0:
                prey.size = 0

        self.setRadius(math.sqrt(self.size + prey.size))

    def setBoost(self, distance, angle):
        self.boostDistance = distance 
        self.boostDirection = Vec2(math.sin(angle), math.cos(angle))
        self.isMoving = True
        if not self.owner and self not in self.gameServer.movingNodes:
            self.gameServer.movingNodes.append(self)

    def checkBorder(self, border):
        r = self.radius / 2
        if self.position.x < border.minx + r or self.position.x > border.maxx - r:
            self.boostDirection.scale(-1, 1);
            self.position.x = max(self.position.x, border.minx + r);
            self.position.x = min(self.position.x, border.maxx - r);

        if self.position.y < border.miny + r or self.position.y > border.maxy - r:
            self.boostDirection.scale(1, -1);
            self.position.y = max(self.position.y, border.miny + r);
            self.position.y = min(self.position.y, border.maxy - r);


    def onEaten(self, hunter):
        return

    def onAdd(self, gameServer):
        return

    def onRemove(self, gameServer):
        return

    def getBound(self):
        return Bound(self.position.x - self.radius, self.position.y - self.radius, self.position.x + self.radius, self.position.y + self.radius)


