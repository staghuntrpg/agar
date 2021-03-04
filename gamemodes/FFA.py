from .Mode import Mode

class FFA(Mode):
    def __init__(self):
        Mode.__init__(self)
        self.ID = 0
        self.name = "Free For All"
        self.specByLeaderboard = True


    def onPlayerSpawn(self, gameServer, player):
        player.color = gameServer.getRandomColor()
        # Spawn player
        gameServer.spawnPlayer(player, gameServer.randomPos2())
