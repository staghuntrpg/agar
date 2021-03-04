from .Player import Player
import numpy as np
from ..modules import *
from ..entity.Cell import Cell
import random
from copy import deepcopy
import numpy as np

class Bot(Player):
    def __init__(self, gameServer, name='bot', id = None):
        super().__init__(gameServer, name, id)
        self.actionCooldown = 0
        self.splitCooldown = 0
        self.actionstamp = np.zeros(4)

    def step(self, *kargs, **kwargs):
        if len(self.cells) == 0:
            self.isRemoved = True
        if self.isRemoved:
            return
        if self.actionCooldown:
            self.action[2] = 2
            self.actionCooldown -= 1
            self.action[:2] = self.actionstamp[:2]
            return
        self.actionCooldown = 5 # action_repeat=5

        if self.splitCooldown:
            self.splitCooldown -= 1

        if random.random() < 0.:
            self.peace_step()
        else:
            self.aggressive_step()


        self.mouse = self.centerPos.add(Vec2(self.action[0] * self.gameServer.config.serverViewBaseX, self.action[1] * self.gameServer.config.serverViewBaseY), 1)
        if self.action[2] == 0:
            self.pressSpace()
        elif self.action[2] == 1:
            self.pressW()
        elif self.action[2] == 2:
            pass

    def peace_step(self):
        visible_food = []
        visible_virus = []
        action = np.zeros(3)
        has_enemy = False
        for cell in self.viewNodes:
            if cell.cellType == 1 or cell.cellType == 3: # food and ejected mass as visible_food
                visible_food.append(cell)
            elif cell.cellType == 0:
                if cell.owner is not self and not self.gameServer.gameMode.haveTeams:
                    has_enemy = True
                elif self.gameServer.gameMode.haveTeams and cell.owner.team != self.team:
                    has_enemy = True
            elif cell.cellType ==2:
                visible_virus.append(cell)
        if not has_enemy and random.random() < 0.05:
            action[2] = 0

        if visible_food and self.cells:
            mincell = self.mincell()
            maxcell = self.maxcell()
            if len(self.cells) >= 14 and self.maxradius > self.gameServer.config.virusMinRadius * 1.15 and visible_virus:
                target = sorted(visible_virus, key=lambda c: (abs(c.position.x - maxcell.position.x) + abs(c.position.y - maxcell.position.y)) / c.mass + 10000 * (self.maxradius <= c.radius * 1.15))[0] # 吃最大cell 1.15倍以下的最近最大virus(when i have >= 14 cells)
                relative_position = target.position.clone().sub(maxcell.position)
                action[2] = 2
            elif len(self.cells) >= 4 and self.maxradius > self.gameServer.config.virusMinRadius * 1.15 and visible_virus and not has_enemy:
                target = sorted(visible_virus, key=lambda c: (abs(c.position.x - maxcell.position.x) + abs(c.position.y - maxcell.position.y)) / c.mass + 10000 * (self.maxradius <= c.radius * 1.15))[0]
                relative_position = target.position.clone().sub(maxcell.position) # no enemy then also eat virus
                action[2] = 2
            else:
                target = sorted(visible_food, key=lambda c: (abs(c.position.x - mincell.position.x) + abs(c.position.y - mincell.position.y)) / c.mass)[0]
                # target = sorted(visible_food, key=lambda c: (abs(c.position.x - self.centerPos.x) + abs(c.position.y - self.centerPos.y)) / c.mass)[0]
                relative_position = target.position.clone().sub(mincell.position) # eat food

            action[0] = relative_position.x / max(abs(relative_position.x), abs(relative_position.y))
            action[1] = relative_position.y / max(abs(relative_position.x), abs(relative_position.y))

            self.actionstamp[:2] = action[:2]

        elif self.cells:
            action[:2] = np.random.randint(2, size=(2)) * 2 - 1
            self.actionstamp[:2] = action[:2]

        self.action = action

    def dfs(self, cell, d_list, deep, pos, opt):

        n_p_list = []
        b = 2 * np.pi * random.random()
        b = 0
        for j in range(10):
            theta = b + 2 * np.pi / 10 * j
            next_pos = pos + np.array([np.cos(theta), np.sin(theta)]) * cell.getMoveR()
            next_pos = self.gameServer.limit_pos(next_pos)
            mi = 1e10
            ok = True
            for c in d_list:
                dis = Vec2(c.position.x - next_pos[0], c.position.y - next_pos[1]).sqDist() - c.getMoveR() * (deep + 1) - c.radius
                mi = min(mi, dis)
                if dis + (cell.getMoveR() - c.getMoveR()) * (2 - deep) < opt[0]:
                    ok = False
                    break
            if mi > 0 and ok:
                n_p_list.append([next_pos, mi])
        if len(n_p_list) == 0:
            if deep == 0: #'cannot escape in dfs Bot'
                return -1, [0., 0.]
            return -1
        n_p_list = sorted(n_p_list, key=lambda x: -x[1])
        if deep == 2:
            opt[0] = max(opt[0], n_p_list[0][1])
            return n_p_list[0][1]
        ma = -1
        ans = [0., 0.]
        for x in n_p_list:
            old_opt = opt[0]
            result = self.dfs(cell, d_list, deep + 1, x[0], opt)
            ma = max(ma, result)
            if deep == 0:
                if old_opt != opt[0]:
                    ans = x[0] - pos
        if deep == 0:
            return ma, ans
        return ma

    def aggressive_step(self):
        cell = self.maxcell()
        result = Vec2(0, 0)  # For splitting

        action = np.zeros(3)
        action[2] = 2. # now all agents try to keep their size
        
        ab_x = cell.position.x / (self.config.borderWidth - cell.radius) + 0.5
        ab_y = cell.position.y / (self.config.borderHeight - cell.radius) + 0.5
        gamma = 1.03
        danger = False
        very_danger = False
        danger_list = []
        for check in self.viewNodes:
            if check.cellType == 0 and check.radius > cell.radius * 1.15:
                danger = True
                dis = Vec2(check.position.x - cell.position.x, check.position.y - cell.position.y).sqDist()
                if dis <= self.config.borderWidth / 6.5 and check.pID < self.gameServer.env.num_agents:
                    very_danger = True
                danger_list.append(check)

        if very_danger:

            ma, ans = self.dfs(cell, danger_list, 0, np.array([cell.position.x, cell.position.y]), [-1])
            result.x = ans[0]
            result.y = ans[1]
            self.action = np.zeros(3)
            self.action[2] = 2
            self.action[0] = result.x
            self.action[1] = result.y
            return

        if danger:

            self.viewNodes.append(Cell(self.gameServer, None, Vec2(-gamma * self.config.borderWidth / 2, -gamma * self.config.borderHeight / 2), cell.radius))
            self.viewNodes.append(Cell(self.gameServer, None, Vec2( gamma * self.config.borderWidth / 2, -gamma * self.config.borderHeight / 2), cell.radius))
            self.viewNodes.append(Cell(self.gameServer, None, Vec2(-gamma * self.config.borderWidth / 2,  gamma * self.config.borderHeight / 2), cell.radius))
            self.viewNodes.append(Cell(self.gameServer, None, Vec2( gamma * self.config.borderWidth / 2,  gamma * self.config.borderHeight / 2), cell.radius))
        
        for check in self.viewNodes:
            if check.owner == self:
                continue

            # Get attraction of the cells - avoid larger cells, viruses and same team cells
            influence = 0
            
            if check.cellType == -1:
                if check.owner is None: # corner
                    influence = -check.radius

            elif check.cellType == 0:   # Player cell
                if self.gameServer.gameMode.haveTeams and cell.owner.team == check.owner.team:
                    # Same team cell
                    influence = 0
                elif cell.radius > check.radius * 1.15:
                    # Can eat it
                    influence = check.radius * 2.5
                elif check.radius > cell.radius * 1.15:
                    # Can eat me
                    influence = -check.radius
                else:
                    influence = -(check.radius / cell.radius) / 3
            elif check.cellType == 1:
                # Food
                influence = 1
            elif check.cellType == 2:
                # Virus/Mothercell
                if cell.radius > check.radius * 1.15:
                    # Can eat it
                    if len(self.cells) == self.gameServer.config.playerMaxCells:
                        # Won't explode
                        influence = check.radius * 2.5
                    elif len(self.cells) >= self.gameServer.config.playerMaxCells - 6:
                        influence = check.radius * 2
                    else:
                        # Can explode
                        influence = -1
                elif check.isMotherCell and check.radius > cell.radius * 1.15:
                    # can eat me
                    influence = -1

            elif check.cellType == 3:
                # Ejected mass
                if cell.radius > check.radius * 1.15:
                    influence = check.radius

                # Apply influence if it isn't 0
                if influence == 0:
                    continue

            displacement = Vec2(check.position.x - cell.position.x, check.position.y - cell.position.y)

            # Figure out distance between cells
            distance = displacement.sqDist()
            if distance == 0:
                print('bug in Bot', check.owner, self)
                continue
            if influence < 0:
                # Get edge distance
                distance -= cell.radius + check.radius

            # The farther they are the smaller influnce it is
            if distance < 1:
                distance = 1;  # Avoid NaN and positive influence with negative distance & attraction
            influence /= distance

            # Splitting conditions
            if check.cellType == 0:
                checkmax = check.owner.maxcell()
                selfmin = self.mincell()
                if checkmax and cell.radius / 1.414 > checkmax.radius * 1.15 and selfmin.radius > checkmax.radius and not self.splitCooldown and 820 - cell.radius / 2 - checkmax.radius >= distance:
                    # Splitkill the target
                    self.splitCooldown = 10
                    relative = checkmax.position.clone().sub(cell.position)
                    if relative.sqDist():
                        relative = relative.normalize()
                    action[0] = relative.x
                    action[1] = relative.y
                    action[2] = 0
                    self.action = action
                    return
                else:
                    result.add(displacement.normalize(), influence)
            else:
            # Produce force vector exerted by self entity on the cell
                result.add(displacement.normalize(), influence)
        
        if danger:
            self.viewNodes = self.viewNodes[:-4]
        
        ab_x = cell.position.x / (self.config.borderWidth - cell.radius) + 0.5
        ab_y = cell.position.y / (self.config.borderHeight - cell.radius) + 0.5
        
        def sigmoid(x):

            x -= 5
            return 1. / (1. + np.exp(-x))

        beta = 3
        result.y *= max(1 / (1 - sigmoid(beta / (np.abs(10 * (ab_x - 1)) + 0.03) ** 0.5)), 1 / (1 - sigmoid(beta / (np.abs(10 * (ab_x - 0)) + 0.03) ** 0.5)))
        result.x *= max(1 / (1 - sigmoid(beta / (np.abs(10 * (ab_y - 1)) + 0.03) ** 0.5)), 1 / (1 - sigmoid(beta / (np.abs(10 * (ab_y - 0)) + 0.03) ** 0.5)))

        alpha = 0.1
        result.add(Vec2(-1, 0), alpha * 1 / (np.abs(10 * (ab_x - 1)) + 0.01) ** 0.5)
        result.add(Vec2(+1, 0), alpha * 1 / (np.abs(10 * (ab_x - 0)) + 0.01) ** 0.5)
        result.add(Vec2(0, -1), alpha * 1 / (np.abs(10 * (ab_y - 1)) + 0.01) ** 0.5)
        result.add(Vec2(0, +1), alpha * 1 / (np.abs(10 * (ab_y - 0)) + 0.01) ** 0.5)
        if result.sqDist():
            result = result.normalize()
        action[0] = result.x
        action[1] = result.y
        self.action = action
