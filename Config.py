class Config:
    def __init__(self):
        self.logVerbosity= 4 # Console log level (0=NONE 1=FATAL 2=ERROR 3=WARN 4=INFO 5=DEBUG)
        self.logFileVerbosity= 5 # File log level

        #SERVER
        self.serverTimeout= 300 # Seconds to keep connection alive for non-responding client
        self.serverWsModule= 'ws' # WebSocket module= 'ws' or 'uws' (install npm package before using uws)
        self.serverMaxConnections= 500 # Maximum number of connections to the server. (0 for no limit)
        self.serverPort= 443 # Server port which will be used to listen for incoming connections
        self.serverBind= "0.0.0.0" # Server network interface which will be used to listen for incoming connections (0.0.0.0 for all IPv4 interfaces)
        self.serverTracker= 0 # Set to 1 if you want to show your server on the tracker http=#ogar.mivabe.nl/master (check that your server port is opened for external connections first!)
        self.serverGamemode= 0 # Gamemodes= 0 = FFA 1 = Teams 2 = Experimental 3 = Rainbow
        self.serverBots= 0 # Number of player bots to spawn (Experimental)
        self.serverViewBaseX= 1920 # Base view distance of players. Warning= high values may cause lag! Min value is 1920x1080
        self.serverViewBaseY= 1080 # min value is 1920x1080
        self.serverMinScale= 0.15 # Minimum viewbox scale for player (low value leads to lags due to large visible area for big cell)
        self.serverSpectatorScale= 0.4 # Scale (field of view) used for free roam spectators (low value leads to lags vanilla = 0.4 old vanilla = 0.25)
        self.serverStatsPort= 88 # Port for stats server. Having a negative number will disable the stats server.
        self.serverStatsUpdate= 60 # Update interval of server stats in seconds
        self.mobilePhysics= 0 # Whether or not the server uses mobile agar.io physics
        self.badWordFilter= 1 # Toggle whether you want the bad word filter on (0 to disable 1 to enable)
        self.serverRestart= 0 # Toggle whether you want your server to auto restart in minutes. (0 to disable)

        # CLIENT
        self.serverMaxLB= 10 # Controls the maximum players displayed on the leaderboard.
        self.serverChat= 1 # Allows the usage of server chat. 0 = no chat 1 = use chat.
        self.serverChatAscii= 1 # Set to 1 to disable non-ANSI letters in the chat (english only)
        self.separateChatForTeams= 0 # Set to 1 to separate chat for game modes with teams like 'Teams'
        self.serverName= 'MultiOgar-Edited #1' # Server name
        self.serverWelcome1= 'Welcome to MultiOgar-Edited!' # First server welcome message
        self.serverWelcome2= '' # Second server welcome message (optional for info etc)
        self.clientBind= '' # Only allow connections to the server from specified client (eg= http=#agar.io - http=#mywebsite.com - http=#more.com) [Use ' - ' to seperate different websites]

        # ANTI-BOT
        self.serverIpLimit= 4 # Controls the maximum number of connections from the same IP (0 for no limit)
        self.serverMinionIgnoreTime= 30 # minion detection disable time on server startup [seconds]
        self.serverMinionThreshold= 10 # max connections within serverMinionInterval time period which l not be marked as minion
        self.serverMinionInterval= 1000 # minion detection interval [milliseconds]
        self.serverScrambleLevel= 1 # Toggles scrambling of coordinates. 0 = No scrambling 1 = lightweight scrambling. 2 = full scrambling (also known as scramble minimap) 3 - high scrambling (no border)
        self.playerBotGrow= 0 # Cells greater than 625 mass cannot grow from cells under 17 mass (set to 1 to disable)

        # BORDER
        rate = 4 / 1.128
        self.borderWidth= 14142.135623730952 / rate # Map border radius (Vanilla value= 14142)
        self.borderHeight= 14142.135623730952 / rate # Map border radius (Vanilla value= 14142)
        self.r = self.borderWidth / 2 
        # FOOD # change here 1.25
        self.foodMinRadius= 10 # Minimum food radius (vanilla 10)
        self.foodMaxRadius= 20 # Maximum food radius (vanilla 20)
        self.foodMinAmount= 1000 // rate ** 2 # Minimum food cells on the map
        self.foodMaxAmount= 2000 // rate ** 2 # Maximum food cells on the map
        self.foodSpawnAmount= 30 // rate ** 2 # The number of food to spawn per interval
        self.foodMassGrow= 1 # Enable food mass grow ?
        self.spawnInterval= 20 # The interval between each food cell spawn in ticks (1 tick = 40 ms)

        # VIRUSES
        self.virusMinRadius= 100 # Minimum virus radius. (vanilla= mass = val*val/100 = 100 mass)
        self.virusMaxRadius= 141.421356237 # Maximum virus radius (vanilla= mass = val*val/100 = 200 mass)
        self.virusMaxPoppedRadius= 60 # Maximum radius a popped cell can have
        self.virusEqualPopRadius= 0 # Whether popped cells have equal radius or not (1 to enable)
        self.virusMinAmount= 50 // rate ** 2# Minimum number of viruses on the map.
        self.virusMaxAmount= 100 // rate ** 2 # Maximum number of viruses on the map. If self number is reached then ejected cells will pass through viruses.
        self.motherCellMaxMass= 0 # Maximum amount of mass a mothercell is allowed to have (0 for no limit)
        self.virusVelocity= 780 # Velocity of moving viruses (speed and distance)
        self.virusMaxCells= 16 # Maximum cells a player can have from viruses.

        # EJECTED MASS
        self.ejectRadius= 36.06 # vanilla= mass = val*val/100 = 13 mass?
        self.ejectRadiusLoss= 42.43 # Eject radius which will be substracted from player cell (vanilla= mass = val*val/100 = 18 mass?)
        self.ejectCooldown= 3 # Tick count until a player can eject mass again in ticks (1 tick = 40 ms)
        self.ejectSpawnPercent= 0.5 # Chance for a player to spawn from ejected mass. 0.5 = 50% (set to 0 to disable)
        self.ejectVirus= 0 # Whether or not players can eject viruses instead of mass
        self.ejectVelocity= 780 # Velocity of ejecting cells (speed and distance)

        # PLAYERS # change here 1.25
        self.playerMinRadius= 31.6227766017 # Minimum radius a player cell can decay too. (vanilla= val*val/100 = 10 mass)
        self.playerMaxRadius= 1500 # Maximum radius a player cell can achive before auto-splitting. (vanilla= mass = val*val/100 = 22500 mass)
        self.playerMinSplitRadius= 59.16079783 # Mimimum radius a player cell has to be to split. (vanilla= mass = val*val/100 = 35 mass)
        self.playerMinEjectRadius= 59.16079783 # Minimum radius a player cell has to be to eject mass. (vanilla= mass = val*val/100 = 35 mass)
        self.playerStartRadius= 31.6227766017 * 2 # Start radius of the player cell. (vanilla= mass = val*val/100 = 10 mass)
        self.playerMaxCells= 16 # Maximum cells a player is allowed to have.
        self.playerSpeed= 1 # Player speed multiplier (1 = normal speed 2 = twice the normal speed)
        self.playerDecayRate= 0.002 # Amount of player cell radius lost per second
        self.playerDecayCap= 0 # Maximum mass a cell can have before it's decayrate multiplies by 10. (0 to disable)
        self.playerRecombineTime= 30 // 2 # Base time in seconds before a cell is allowed to recombine
        self.playerDisconnectTime= -1 # Time in seconds before a disconnected player's cell is removed (Set to -1 to never remove)
        self.playerMaxNickLength= 15 # Maximum nick length
        self.splitVelocity= 780 # Velocity of splitting cells (speed and distance)

        # MINIONS
        self.minionStartRadius= 31.6227766017 # Start radius of minions (mass = 32*32/100 = 10.24)
        self.minionMaxStartRadius= 31.6227766017 # Maximum value of random start radius for minions (set value higher than minionStartRadius to enable)
        self.minionCollideTeam= 0 #Determines whether minions colide with their team in the Teams gamemode (0 = OFF 1 = ON)
        self.disableERTP= 1 # Whether or not to disable ERTP controls for minions. (must use ERTPcontrol script in /scripts) (Set to 0 to enable)
        self.disableQ= 0 # Whether or not to disable Q controls for minions. (Set 0 to enable)
        self.serverMinions= 0 # Amount of minions each player gets once they spawn
        self.collectPellets= 0 # Enable collect pellets mode. To use just press P or Q. (Warning= self disables Q controls so make sure that disableERT is 0)
        self.defaultName= "minion" # Default name for all minions if name is not specified using command (put <r> before the name for random skins!)
        self.minionsOnLeaderboard= 0 # Whether or not to show minions on the leaderboard. (Set 0 to disable)

        # TOURNAMENT
        self.tourneyMaxPlayers= 12 # Maximum number of participants for tournament style game modes
        self.tourneyPrepTime= 10 # Number of ticks to wait after all players are ready (1 tick = 1000 ms)
        self.tourneyEndTime= 30 # Number of ticks to wait after a player wins (1 tick = 1000 ms)
        self.tourneyTimeLimit= 20 # Time limit of the game in minutes.
        self.tourneyAutoFill= 0 # If set to a value higher than 0 the tournament match will automatically fill up with bots after self amount of seconds
        self.tourneyAutoFillPlayers= 1 # The timer for filling the server with bots will not count down unless there is self amount of real players
        self.tourneyLeaderboardToggleTime= 10 #Time for toggling the leaderboard in seconds.If value set to 0 leaderboard will not toggle.
