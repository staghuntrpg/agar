from .Cell import Cell
class EjectedMass(Cell):
    def __init__(self, gameServer, owner, position, radius):
        Cell.__init__(self, gameServer, owner, position, radius)
        self.cellType = 3

    def onAdd(self, gameServer):
        gameServer.nodesEjected.append(self)

    def onRemove(self, gameServer):
        if self in gameServer.nodesEjected:
            gameServer.nodesEjected.remove(self)
