import math
from .Config import Config
import random
from .modules import *
from .entity import *
from .gamemodes import *
from .players import Player, Bot
import numpy as np

# noinspection PyAttributeOutsideInit
class GameServer:
    def __init__(self, env):
        self.srcFiles = "../src"
        self.env = env
        # Startup
        self.run = True
        self.version = '1.6.1'
        self.httpServer = None
        self.lastNodeId = 1
        self.lastPlayerId = -1
        self.players = []
        self.socketCount = 0
        self.largestPlayer = None
        self.nodes = []  # Total nodes
        self.nodesVirus = []  # Virus nodes
        self.nodesFood = []  # Food nodes
        self.nodesEjected = []  # Ejected nodes
        self.nodesPlayer = []  # Player nodes

        self.movingNodes = []  # For move engine
        self.leaderboard = []  # For leaderboard
        self.leaderboardType = -1  # No type

        # Main loop tick
        self.stepDateTime = 0
        self.timeStamp = 0
        self.updateTime = 0
        self.updateTimeAvg = 0
        self.timerLoopBind = None
        self.mainLoopBind = None
        self.tickCounter = 0
        self.disableSpawn = False

        # Config
        self.config = Config()
        self.food_rate = 0.0 + 0.0 * random.random()
        self.foodMaxAmount = int(self.config.foodMaxAmount * self.food_rate)
        self.foodMinAmount = int(self.config.foodMinAmount * self.food_rate)

        self.ipBanList = []
        self.minionTest = []
        self.userList = []
        self.badWords = []

        # Set border, quad-tree
        self.setBorder(self.config.borderWidth, self.config.borderHeight)
        self.quadTree = QuadNode(self.border, 64, 32)

    def start(self, gamemode=1):
        # Set up gamemode(s)
        self.gameMode = Get_Game_Mode(gamemode)
        self.gameMode.onServerInit(self)

    def addPlayers(self, players):
        self.players = players
        for i in range(len(self.players)):
            self.players[i].id = i

    def addNode(self, node):
        # Add to quad-tree & node list
        x = node.position.x
        y = node.position.y
        s = node.radius
        node.quadItem = QuadItem(node, Bound(x - s, y - s, x + s, y + s))
        self.quadTree.insert(node.quadItem)
        self.nodes.append(node)
        # Special on-add actions
        node.onAdd(self)

    def setBorder(self, width, height):
        hw = width / 2
        hh = height / 2
        self.border = Bound(-hw, -hh, hw, hh)

    def getRandomColor(self):
        colorRGB = [0xff, 0x07, random.randint(0, 256)]
        random.shuffle(colorRGB)
        # return random
        return Color(*colorRGB)

    def removeNode(self, node):
        # Remove from quad-tree
        node.isRemoved = True
        self.quadTree.remove(node.quadItem)
        node.quadItem = None

        # Remove from node lists
        if node in self.nodes:
            self.nodes.remove(node)

        if node in self.movingNodes:
            self.movingNodes.remove(node)

        # Special on-remove actions
        node.onRemove(self)

    def updatePlayers(self):
        # check dead players
        i = 0
        while i < len(self.players):
            if not self.players[i]:
                i += 1
                continue

            if self.players[i].isRemoved:
                id = self.players[i].pID
                # remove and recreate dead player
                self.players.pop(i)
                if i < self.env.num_agents:
                    pass
                    #self.players.insert(i, Player(self, id = id))
                    #self.env.players[i] = self.players[i]
                    #self.env.agents[i] = self.players[i] # reborn of outside agent
                else:self.players.append(Bot(self, id = id))
            else:
                i += 1
        # update
        for player in self.players:
            if not player:
                continue
            player.updateView()

    def Update(self):
        # Loop main functions
        if self.run:
            # Move moving nodes first
            for cell in self.nodesPlayer:
                cell.last_position = cell.position.clone()
            for cell in self.movingNodes:
                if cell.isRemoved:
                    continue
                # Scan and check for ejected mass / virus collisions
                self.boostCell(cell)
                self.updateNodeQuad(cell)
                def callback_fun(check):
                    collision = self.checkCellCollision(cell, check)
                    if cell.cellType == 3 and check.cellType == 3 and not self.config.mobilePhysics:
                        self.resolveRigidCollision(collision)
                    else:
                        self.resolveCollision(collision)

                self.quadTree.find(cell.quadItem.bound, callback_fun)
                if not cell.isMoving:
                    self.movingNodes.remove(cell)

            # Update players and scan for collisions
            eatCollisions = []
            for cell in self.nodesPlayer:
                if cell.isRemoved:
                    continue
                # Scan for eat/rigid collisions and resolve them
                def callback_fun(check):
                    collision = self.checkCellCollision(cell, check)
                    if self.checkRigidCollision(collision):
                        self.resolveRigidCollision(collision)

                    elif check != cell:
                        eatCollisions.insert(0, collision)

                self.movePlayer(cell, cell.owner)
                self.boostCell(cell)
                self.autoSplit(cell, cell.owner)
                self.updateNodeQuad(cell)
                self.quadTree.find(cell.quadItem.bound, callback_fun)
                # Decay player cells once per second
                if ((self.tickCounter + 3) % 25) == 0:
                    # print('decay')
                    self.updateRadiusDecay(cell)
                # Remove external minions if necessary


            for m in eatCollisions:
                self.resolveCollision(m)

            if (self.tickCounter % self.config.spawnInterval) == 0:
                # Spawn food & viruses
                self.spawnCells()

            self.gameMode.onTick(self)
            self.tickCounter += 1

        if not self.run and self.gameMode.IsTournament:
            self.tickCounter += 1
        self.updatePlayers()

    # update remerge first
    def limit_cell(self, cell):

        dis = cell.position.sqDist()
        if dis > self.config.r:
            cell.position.scale(self.config.r / dis)

    def limit_pos(self, pos):

        dis = np.sqrt(pos[0] * pos[0] + pos[1] * pos[1])
        if dis > self.config.r:
            pos *= self.config.r / dis
        return pos
    
    def limit_pos2(self, pos):

        dis = pos.sqDist()
        if dis > self.config.r:
            pos.scale(self.config.r / dis)
        return pos

    def movePlayer(self, cell, player):
        # get movement from vector
        d = player.mouse.clone().sub(cell.position)
        move = cell.getSpeed(d.sqDist())  # movement speed
        if not move:
            return  # avoid jittering
        cell.position.add(d, move)
        self.limit_cell(cell)
        # self.updateNodeQuad(cell)
        
        # update remerge
        time = self.config.playerRecombineTime
        base = max(time, cell.radius * 0.2) * 25
        # instant merging conditions
        if not time or player.rec or player.mergeOverride:
            cell.canRemerge = cell.boostDistance < 100
            return  # instant merge

        # regular remerge time
        cell.canRemerge = cell.getAge() >= base

    # decay player cells
    def updateRadiusDecay(self, cell):
        rate = self.config.playerDecayRate
        cap = self.config.playerDecayCap

        if not rate or cell.radius <= self.config.playerMinRadius:
            return

        # remove radius from cell at decay rate
        if cap and cell.mass > cap:
            rate *= 10
        decay = 1 - rate * self.gameMode.decayMod
        cell.setRadius(math.sqrt(cell.size * decay))
        # self.updateNodeQuad(cell)

    def boostCell(self, cell):
        if cell.isMoving and cell.boostDistance < 1 or cell.isRemoved:
            cell.boostDistance = 0
            cell.isMoving = False
            return
        # decay boost-speed from distance
        speed = cell.boostDistance / 9  # val: 87
        cell.boostDistance -= speed  # decays from speed
        cell.position.add(cell.boostDirection, speed)

        # update boundries
        cell.checkBorder(self.border)


    def autoSplit(self, cell, player):
        # get radius limit based off of rec mode
        if player.rec:
            maxRadius = 1e9  # increase limit for rec (1 bil)
        else:
            maxRadius = self.config.playerMaxRadius

        # check radius limit
        if player.mergeOverride or cell.radius < maxRadius:
            return
        if len(player.cells) >= self.config.playerMaxCells or self.config.mobilePhysics:
            # cannot split => just limit
            cell.setRadius(maxRadius)
        else:
            # split in random direction
            angle = random.random() * 2 * math.pi
            self.splitPlayerCell(player, cell, angle, cell.mass * .5)

    def updateNodeQuad(self, node):
        # update quad tree
        item = node.quadItem.bound
        item.minx = node.position.x - node.radius
        item.miny = node.position.y - node.radius
        item.maxx = node.position.x + node.radius
        item.maxy = node.position.y + node.radius
        self.quadTree.update(node.quadItem)

    # Checks cells for collision
    def checkCellCollision(self, cell, check):
        p = check.position.clone().sub(cell.position)
        # create collision manifold
        return Collision(cell, check, p.sqDist(), p)

    # Checks if collision is rigid body collision
    def checkRigidCollision(self, m):
        if not m.cell.owner or not m.check.owner:
            return False
        if m.cell == m.check:
            return False

        if m.cell.owner != m.check.owner:
            # Minions don't collide with their team when the config value is 0
            return self.gameMode.haveTeams and m.cell.owner.team == m.check.owner.team # Different owners => same team

        r = 1 if self.config.mobilePhysics else 13
        if m.cell.getAge() < r or m.check.getAge() < r:
            return False  # just splited => ignore

        return not m.cell.canRemerge or not m.check.canRemerge

    # Resolves rigid body collisions

    def resolveRigidCollision(self, m):
        if m.d == 0:
            rand_angle = random.random() * math.pi * 2
            m.p = Vec2(math.cos(rand_angle) * 1, math.sin(rand_angle) * 1)
            m.d = 1

        push = min((m.cell.radius + m.check.radius - m.d) / m.d, m.cell.radius + m.check.radius - m.d)
        if push <= 0:
            return

        if m.d < m.cell.radius + m.check.radius and m.cell.radius + m.check.radius >= 0:
            # body impulse
            rt = m.cell.size + m.check.size
            r1 = push * m.cell.size / rt
            r2 = push * m.check.size / rt

            # apply extrusion force
            m.cell.position.sub2(m.p, r2)
            m.check.position.add(m.p, r1)

    # Resolves non-rigid body collision
    def resolveCollision(self, m):
        cell = m.cell
        check = m.check
        if cell.radius > check.radius:
            cell = m.check
            check = m.cell

        # Do not resolve removed
        if cell.isRemoved or check.isRemoved:
            return

        # check eating distance
        div = 20 if self.config.mobilePhysics else 3
        div = 20 if m.cell.cellType == 2 and m.check.cellType == 3 else div
        if m.d >= check.radius - cell.radius / div:
            return  # too far => can't eat

        # collision owned => ignore, resolve, or remerge
        if cell.owner and cell.owner == check.owner:
            if cell.getAge() < 13 or check.getAge() < 13:
                return  # just splited => ignore
        elif check.radius < cell.radius * 1.15 or not check.canEat(cell):
            return  # Cannot eat or cell refuses to be eaten

        # Consume effect
        check.onEat(cell)
        cell.onEaten(check)
        cell.killedBy = check

        # Remove cell
        self.removeNode(cell)

    def splitPlayerCell(self, player, parent, angle, mass):
        radius = math.sqrt(mass * 100)
        radius1 = math.sqrt(parent.size - radius * radius)

        # Too small to split
        if not radius1 or radius1 < self.config.playerMinRadius:
            return

        # Remove radius from parent cell
        parent.setRadius(radius1)

        # Create cell and add it to node list
        newCell = PlayerCell(self, player, parent.position, radius)
        newCell.setBoost(self.config.splitVelocity, angle)
        self.addNode(newCell)

    def randomPos(self):
        theta = np.pi * 2 * random.random()
        r = np.sqrt(self.config.r ** 2 * random.random())
        return Vec2(r * np.cos(theta), r * np.sin(theta))

    def randomPos2(self):
        if len(self.players) == 0:return self.randomPos()
        id = random.randint(0, self.env.num_agents - 1)
        box = self.players[id].viewBox
        pos = Vec2(box.minx + random.random() * (box.maxx - box.minx),
                   box.miny + random.random() * (box.maxy - box.miny))
        pos = self.limit_pos2(pos)
        return pos

    def spawnCells(self):
        # spawn food at random radius
        maxCount = self.foodMaxAmount - len(self.nodesFood)
        minCount = self.foodMinAmount - len(self.nodesFood)
        spawnCount = max(min(maxCount, self.config.foodSpawnAmount), minCount)
        for i in range(spawnCount):
            cell = Food(self, None, self.randomPos(), self.config.foodMinRadius)
            if self.config.foodMassGrow:
                maxGrow = self.config.foodMaxRadius - cell.radius
                cell.setRadius(cell.radius + maxGrow * random.random())

            cell.color = self.getRandomColor()
            self.addNode(cell)

        # spawn viruses (safely)
        if len(self.nodesVirus) < self.config.virusMinAmount:
            virus = Virus(self, None, self.randomPos(), self.config.virusMinRadius)
            if not self.willCollide(virus):
                self.addNode(virus)

    def spawnPlayer(self, player, pos):
        if self.disableSpawn:
            return

        # Check for special starting radius
        if player.name == 'dummy':
            radius = self.config.playerStartRadius * (0.6 + 0.6 * random.random())
            p_c = 70 + player.pID * 70 # outside agent are all grey or black
            player.color = Color(p_c, p_c, p_c)
        else:radius = self.config.playerStartRadius * (0.4 + 0.2 * random.random())

        if player.spawnmass:
            radius = player.spawnmass

        # Check if can spawn from ejected mass
        if self.nodesEjected:
            eject = random.choice(self.nodesEjected)  # Randomly selected
            if random.random() <= self.config.ejectSpawnPercent and eject and eject.boostDistance < 1:
                # Spawn from ejected mass
                pos = eject.position.clone()
                player.color = eject.color
                radius = max(radius, eject.radius * 1.15)

        # Spawn player safely (do not check minions)
        cell = PlayerCell(self, player, pos, radius)
        if self.willCollide(cell):
            pos = self.randomPos()  # Not safe => retry
        self.addNode(cell)

        # Set initial mouse coords
        player.mouse = pos

    def willCollide(self, cell):
        notSafe = False  # Safe by default
        sqRadius = cell.size
        pos = self.randomPos()
        d = cell.position.clone().sub(pos)
        if d.dist() + sqRadius <= sqRadius * 2:
            notSafe = True

        def callback_fun(n):
            nonlocal notSafe
            if n.cellType == 0:
                notSafe = True

        self.quadTree.find(Bound(cell.position.x - cell.radius, cell.position.y - cell.radius, cell.position.x + cell.radius,
                                 cell.position.y + cell.radius), callback_fun)

        return notSafe

    def splitCells(self, player):
        # Split cell order decided by cell age
        # cellToSplit = [cell for cell in player.cells]
        cellToSplit = sorted(player.cells, key=lambda x : -x.getAge())

        for cell in cellToSplit:
            d = player.mouse.clone().sub(cell.position)
            if d.dist() < 1:
                d.x = 1
                d.y = 0

            if cell.radius < self.config.playerMinSplitRadius:
                continue  # cannot split

            # Get maximum cells for rec mode
            if player.rec:
                max_cell_rec = 200  # rec limit
            else:
                max_cell_rec = self.config.playerMaxCells
            if len(player.cells) >= max_cell_rec:
                return

            # Now split player cells
            self.splitPlayerCell(player, cell, d.angle(), cell.mass * .5)

    def canEjectMass(self, player):
        if player.lastEject is None:
            # first eject
            player.lastEject = self.tickCounter
            return True

        dt = self.tickCounter - player.lastEject
        if dt < self.config.ejectCooldown:
            # reject (cooldown)
            return False

        player.lastEject = self.tickCounter
        return True

    def ejectMass(self, player):
        if not self.canEjectMass(player) or player.frozen:
            return
        for cell in player.cells:
            if cell.radius < self.config.playerMinEjectRadius:
                continue  # Too small to eject

            d = player.mouse.clone().sub(cell.position)
            sq = d.sqDist()
            d.x = d.x / sq if sq > 1 else 1
            d.y = d.y / sq if sq > 1 else 0

            # Remove mass from parent cell first
            loss = self.config.ejectRadiusLoss
            loss = cell.size - loss * loss
            cell.setRadius(math.sqrt(loss))

            # Get starting position
            pos = Vec2(cell.position.x + d.x * cell.radius, cell.position.y + d.y * cell.radius)
            angle = d.angle() + (random.random() * .6) - .3

            # Create cell and add it to node list
            if not self.config.ejectVirus:
                ejected = EjectedMass(self, None, pos, self.config.ejectRadius)
            else:
                ejected = Virus(self, None, pos, self.config.ejectRadius)

            ejected.color = cell.color
            ejected.setBoost(self.config.ejectVelocity, angle)
            self.addNode(ejected)

    def shootVirus(self, parent, angle):
        # Create virus and add it to node list
        pos = parent.position.clone()
        newVirus = Virus(self, None, pos, self.config.virusMinRadius)
        newVirus.setBoost(self.config.virusVelocity, angle)
        self.addNode(newVirus)
