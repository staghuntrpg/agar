from .Mode import Mode
from ..modules import *
import random
import math

class Teams(Mode):

    def __init__(self):
        Mode.__init__(self)

        self.ID = 1
        self.name = "Teams"
        self.decayMod = 1.5
        self.packetLB = 50
        self.haveTeams = True
        self.colorFuzziness = 32

        # Special
        self.teamAmount = 3; # Amount of teams. Having more than 3 teams will cause the leaderboard to work incorrectly (player issue).
        self.colors = [Color(223, 0, 0),Color(0, 223, 0), Color(0, 0, 223)] # Make sure you add extra colors here if you wish to increase the team amount [Default colors are: Red, Green, Blue]
        self.nodes = []; # Teams


    def fuzzColorComponent(self, component):
        component += int(random.random() * self.colorFuzziness)
        return component


    def getTeamColor(self, team):
        color = self.colors[team]
        return Color(self.fuzzColorComponent(color.r), self.fuzzColorComponent(color.b), self.fuzzColorComponent(color.g))

    # Override
    def onPlayerSpawn(self, gameServer, player):
        # Random color based on team
        player.color = self.getTeamColor(player.team)
        # Spawn player
        gameServer.spawnPlayer(player, gameServer.randomPos())


    def onServerInit(self, gameServer):
        for i in range(self.teamAmount):
            self.nodes.append([])

    # migrate current players to team mode
        for player in gameServer.players:
            tracker = player.playerTracker
            self.onPlayerInit(tracker)
            tracker.color = self.getTeamColor(tracker.team)
            for cell in tracker.cells:
                cell.color = tracker.color
                self.nodes[tracker.team].append(cell)


    def onPlayerInit(self, player):
        # Get random team
        player.team = math.floor(random.random() * self.teamAmount)


    def onCellAdd(self, cell):
        # Add to team list
        self.nodes[cell.owner.team].append(cell)


    def onCellRemove(self, cell):
        # Remove from team list
        if cell in self.nodes[cell.owner.team]:
            self.nodes[cell.owner.team].remove(cell)


    def onCellMove(self, cell, gameServer):
        # Find team
        for check in cell.owner.visibleNodes:
            if check.cellType != 0 or cell.owner == check.owner:
                continue
            # Collision with teammates
            team = cell.owner.team
            if check.owner.team == team:
                manifold = gameServer.checkCellCollision(cell, check) # Calculation info
                if manifold is not None:
                    manifold.check.canEat(manifold.cell)

