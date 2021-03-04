class Mode():
    def __init__(self):
        self.ID = -1
        self.name = "Blank"
        self.decayMod = 0.0; # Modifier for decay rate (Multiplier)
        self.packetLB = 49; # Packet id for leaderboard packet (48 = Text List, 49 = List, 50 = Pie chart)
        self.haveTeams = False; # True = gamemode uses teams, false = gamemode doesnt use teams
        self.specByLeaderboard = False; # false = spectate from player list instead of leaderboard
        self.IsTournament = False

    # Override these
    def onServerInit(self, gameServer):
    # Called when the server starts
        gameServer.run = True


    def onTick(self,gameServer):
        return
        # Called on every game tick


    def onPlayerInit(self,player):
        return
    # Called after a player object is constructed


    def onPlayerSpawn(self, gameServer, player):
        # Called when a player is spawned
        player.color = gameServer.getRandomColor() # Random color
        gameServer.spawnPlayer(player, gameServer.randomPos())


    def onCellAdd(self, cell):
        return
        # Called when a player cell is added


    def onCellRemove(self, cell):
        return
    # Called when a player cell is removed


    def onCellMove(cell, gameServer):
        return
    # Called when a player cell is moved


    def updateLB(self, gameServer):
        # Called when the leaderboard update function is called
        gameServer.leaderboardType = self.packetLB
