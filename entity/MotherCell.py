from .Food import Food
from .Cell import Cell
import math
import random
from ..modules import *

class MotherCell(Cell):
    def __init__(self, gameServer, owner, position, radius):
        Cell.__init__(self, gameServer, owner, position, radius)
        self.cellType = 2
        self.isSpiked = True
        self.isMotherCell = True
        self.color = Color(206, 99, 99)
        self.motherCellMinRadius = 149
        self.motherCellSpawnAmount = 2
        if not self.radius:
            self.setRadius(self.motherCellMinRadius)

    def canEat(self, cell):
        maxMass = self.gameServer.config.motherCellMaxMass
        if maxMass and self.mass >= maxMass:
            return False
        return cell.cellType in [0, 2, 3]

    def onUpdate(self):
        maxFood = self.gameServer.config.foodMaxAmount
        if len(self.gameServer.nodeFood) >= maxFood:
            return
        radius1 = self.radius
        radius2 = self.gameServer.config.foodMinRadius
        for i in range(self.motherCellSpawnAmount):
            radius1 = math.sqrt(radius1**2 - radius2 **2)
            radius1 = math.max(radius1, self.motherCellMinRadius)
            self.setRadius(radius1)

            angle = random.random() * 2 * math.pi
            pos = self.position + radius1 * Vec2(math.sin(angle), math.cos(angle))

            food = Food(self.gameServer, None, pos, radius2)
            food.color = self.gameServer.getRandomColor()
            self.gameServer.addNode(food)

            food.setBoost(32 + 42*random.random(), angle)
            if len(self.gameServer.nodeFood) >= maxFood or radius1 <= self.motherCellMinRadius:
                break
        self.gameServer.updateNodeQuad(self)

    def onAdd(self):
        return

    def onRemove(self):
        return


