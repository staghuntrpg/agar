from .Cell import Cell
class Food(Cell):
    def __init__(self, gameServer, owner, position, radius):
        Cell.__init__(self, gameServer, owner, position, radius)
        self.cellType = 1

    def onAdd(self, gameServer):
        gameServer.nodesFood.append(self)

    def onRemove(self, gameServer):
        if self in gameServer.nodesFood:
            gameServer.nodesFood.remove(self)