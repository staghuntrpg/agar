# Author: Boyuan Chen (Berkeley Artifical Intelligence Research)
#         Zhenggang Tang (Peking University)

# The project is largely based on m-byte918's javascript implementation of the game with a lot of bug fixes and optimization for python
# Original Ogar-Edited project https://github.com/m-byte918/MultiOgar-Edited

import gym
from gym import spaces
from .GameServer import GameServer
from .players import Player, Bot
from . import rendering
import numpy as np
from copy import deepcopy
import random

def max(a, b):

    if a>b:return a
    return b

def rand(a, b):

    return random.random() * (b - a) + a


class AgarEnv(gym.Env):
    '''
    function __init__ 
        param:
            args:
                args.eval: bool, when args.eval = True, script agent speed will be 1x and reward settings will be "original settings" (alpha = 1, beta = 0) otherwise a curriculum learning which changes script agent speed will be executed.                
                args.total_step: number of training steps at the beginning, if it's set to None, it will be regarded as 0. 
                args.num_processes: int, number of environments, only used to calculate total_steps
                args.gamma: real, discount rate of RL, only used to calculate summation of rewards, can be set to None if rewards calculation is not necessary
                args.action_repeat: int, times of action should be repeated
                args.num_controlled_agent: int, number of agent controlled outside
            gamemode:
                FFA: gamemode = 0
                Team: gamemode = 1 (not implemented yet)
            reward_settings:
                str: two options, "std" means standard settings, "agg" means aggressive settings.
    '''
    def __init__(self, args, gamemode = 0, reward_settings = "std"):
        super(AgarEnv, self).__init__()
        self.alpha = args.r_alpha
        self.beta = args.r_beta
        self.reward_settings = reward_settings
        self.args = args
        if args.total_step is None:args.total_step = 0
        self.total_step = args.total_step
        self.eval = args.eval
        if args.gamma is None:args.gamma = 1
        self.g = args.gamma # discount rate of RL (gamma)
        self.num_agents = args.num_controlled_agent # number of agents controlled outside
        self.action_space = spaces.Box(low = -1, high = 1, shape=(3,)) # action = [x(real), y(real), split(bool) 
        obs_size = 578
        self.observation_space = spaces.Dict( {'t'+str(i):spaces.Box(low=-100, high=100, shape=(578,)) for i in range(self.num_agents)}  )
        self.viewer = None
        self.gamemode = gamemode # We only implemented FFA (gamemode = 0)
        self.last_mass = [None for i in range(self.num_agents)]
        self.sum_r = np.zeros((self.num_agents, )) # summation or reward
        self.sum_r_g = np.zeros((self.num_agents, )) # summation of discounted reward
        self.sum_r_g_i = np.zeros((self.num_agents, )) # summation of discounted reward using standard reward settings (alpha = 1, beta = 0)
        self.dir = []
        # factors for reward
        self.action_repeat = args.action_repeat
    '''
    function step:

        param:
            actions:
                actions = [x_0, y_0, split_0, x1, y1, split_1, ..., x_n-1, y_n-1, split_n-1], n = the number of agents controlled outside
                x_i, y_i are real and belong to [0, 1]. They mean a point on the screen that all balls will move to
                split_i is bool, means whether the agent will choose to split
    
        the action will be executed repeatedly for self.action_repeat steps (if split_i = True, agent_i will only split at the 1st step)

        return: 
            observations:
                observations = {'t0': obs_0, 't1': obs_1, ..., 't_n-1': obs_n-1} details of obs_i can be seen at explanation of function parse_obs
            rewards:
                rewards = [reward_0, reward_1, ..., rewards_n-1] rewards_i is real.
            dones:
                dones = [done_0, done_1, ..., done_n-1] rewards_i is real.
            infos:
                infos = [info_0, info_1, ..., info_n-1]
                info_i = {'high_masks':bool, 'bad_transition':bool}
                when high_masks is False, the state at this step is meaningless(when a outside agent dies, it will still receive meaningless observations until all outside agents die or the episode ends)
                when bad_transition is False, the state and the next state has no transition relationship
    '''
    def step(self, actions_):
        
        actions = deepcopy(actions_)
        reward = np.zeros((self.num_agents, ))
        done = np.zeros((self.num_agents, ))
        info = [{} for i in range(self.num_agents)]
        first = True
        for i in range(self.action_repeat):
        
            if not first:
                for j in range(self.num_agents):
                    actions[j * 3 + 2] = -1.
            first = False
            o,r = self.step_(actions)
            reward += r
        
        self.m_g *= self.g
        done = (done != 0)
        self.total_step += self.args.num_processes
        
        self.killed += (self.t_killed != 0)
        for i in range(self.num_agents):
          
            info[i]['high_masks'] = True
            info[i]['bad_transition'] = False
            if self.killed[i] >= 1:
                done[i] = True
                info[i]['high_masks'] = False
                if self.killed[i] == 1:
                    info[i]['episode'] = {'r':self.sum_r[i], 'r_g': self.sum_r_g[i], 'r_g_i': self.sum_r_g_i[i], 'hit':self.hit[i], 'dis': self.sum_dis / self.s_n}
                else:info[i]['bad_transition'] = True
            elif self.s_n >= self.stop_step:
                done[i] = True
                info[i]['episode'] = {'r':self.sum_r[i], 'r_g': self.sum_r_g[i], 'r_g_i':self.sum_r_g_i[i], 'hit':self.hit[i], 'dis': self.sum_dis / self.s_n}

        if np.sum(done) == self.num_agents:
            for i in range(self.num_agents):
                info[i]['high_masks'] = True
                if self.killed[i] == 0 and self.s_n >= self.stop_step:info[i]['bad_transition']=True
                elif self.killed[i] == 1:info[i]['bad_transition'] = False
                else:info[i]['bad_transition'] = True
        
        return o, reward, done, info
    
    def step_(self, actions_):
        actions = deepcopy(actions_)
        act = []
        for i in range(self.num_agents):
            act.extend([actions[i * 3 + 0], actions[i * 3 + 1], actions[i * 3 + 2]])
            if actions[i * 3 + 2] > 0.5:act[-1] = 0
            else:act[-1] = 2
        actions = np.array(act).reshape(-1,3)
        for action, agent in zip(actions, self.agents):
            agent.step(deepcopy(action))
        for i in range(self.num_agents, len(self.server.players)):
            self.server.players[i].step()

        self.server.Update()
        t_rewards, t_rewards2 = [], []
        for i in range(self.num_agents):
            a, b = self.parse_reward(self.agents[i], i)
            t_rewards.append(a)
            t_rewards2.append(b)
        t_rewards, t_rewards2 = np.array(t_rewards), np.array(t_rewards2)
        rewards = np.zeros(self.num_agents)
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if i == j:
                    rewards[i] += t_rewards[j]
                else:
                    rewards[i] += t_rewards[j] * self.coop_eps[i]

        self.split = np.zeros(self.num_agents)
        observations = [self.parse_obs(self.agents[i], i, actions) for i in range(self.num_agents)]
        t_dis = self.agents[0].centerPos.clone().sub(self.agents[1].centerPos).sqDist() / self.server.config.r
        self.sum_dis += t_dis
        self.near = (t_dis <= 0.5)
        if self.killed[0] + self.killed[1] > 0:self.near = False
        self.last_action = deepcopy(actions.reshape(-1))
        self.sum_r += rewards
        self.sum_r_g += rewards * self.m_g
        self.sum_r_g_i += t_rewards2 * self.m_g
        observations = np.array(observations)
        self.s_n += 1
         
        observations = {'t'+str(i): observations[i] for i in range(self.num_agents)}
        return observations, rewards

    '''
    function reset:

        no param

        return: observations
    '''
    def reset(self):
        
        while 1:
            self.num_bots = 5
            self.num_players = self.num_bots +self.num_agents
            self.rewards_forced = [0 for i in range(self.num_agents)]
            self.stop_step = 2000 - random.randint(0, 100) * self.action_repeat
            self.last_mass = [None for i in range(self.num_agents)]
            self.killed = np.zeros(self.num_agents)
            self.t_killed = np.zeros(self.num_agents)
            self.sum_r = np.zeros((self.num_agents, ))
            self.sum_r_g = np.zeros((self.num_agents, ))
            self.sum_r_g_i = np.zeros((self.num_agents, ))
            self.sum_dis = 0.
            self.m_g = 1.
            self.last_action = [0 for i in range(3 * self.num_players)]
            self.s_n = 0
            self.kill_reward_eps = np.ones(self.num_agents) * 0.33 * (1 - self.alpha)
            self.coop_eps = np.ones(self.num_agents) * self.beta
            self.mass_reward_eps = 0.33
            self.killed_reward_eps = 0.
            self.split = np.zeros(self.num_agents)
            self.hit = np.zeros((self.num_agents, 4))
            self.near = False
            if self.eval:
                self.kill_reward_eps = np.zeros(self.num_agents)
                self.coop_eps = np.zeros(self.num_agents)
                self.bot_speed = 1.0
            else:
                up  = min(1.0, max(0.0, (self.total_step - 5e6) / 5e6)) # script agent speed curriculum is set here.
                low = min(1.0, max(0.0, (self.total_step - 1e7) / 5e6))
                self.bot_speed = rand(low, up)
            self.server = GameServer(self)
            self.server.start(self.gamemode)
            self.agents = [Player(self.server) for _ in range(self.num_agents)]
            self.bots = [Bot(self.server) for _ in range(self.num_bots)]
            self.players = self.agents + self.bots
            self.server.addPlayers(self.players)
            self.viewer = None
            self.server.Update()
            observations = [self.parse_obs(self.agents[i], i) for i in range(self.num_agents)]
            success = True
            for i in range(self.num_agents):
                if np.sum(observations[i]) == 0.: # sometimes the agent dies just after initialization, we should avoid this.
                    success = False
            observations = np.array(observations)
            observations = {'t'+str(i): observations[i] for i in range(self.num_agents)}
            if success:break
        return observations

    def parse_obs(self, player, id, action = None):
        
        '''

        function parse_obs will return obs_id
        obs_id is a 578D array, first 560D is information of all entities around agent_id, last 28D is global information

        '''
        n = [10, 5, 5, 10, 10, 10, 5, 5, 10, 10] # the agent can observe at most 10 self-cells, 5 foods, 5 virus, 10 other script agent cells, 10 other outside agent cells
        s_glo = 28 # global information size
        s_size_i = [15, 7, 5, 15, 15, 1, 1, 1, 1, 1] # information size of self-cell, food, virus, script agent cell and other outside agent cells.
        s_size = np.sum(np.array(n) * np.array(s_size_i)) + s_glo
        if len(player.cells) == 0:return np.zeros(s_size)
        obs = [[], [], [], [], []]
        for cell in player.viewNodes:
            t, feature = self.cell_obs(cell, player, id)
            obs[t].append(feature)
            
        for i in range(len(obs)):
            obs[i].sort(key = lambda x:x[0] ** 2 + x[1] ** 2)
        obs_f = np.zeros(s_size)
        bound = self.players[id].get_view_box()
        b_x = (bound[1] - bound[0]) / self.server.config.serverViewBaseX
        b_y = (bound[3] - bound[2]) / self.server.config.serverViewBaseY
        base = 0
        for j in range(10):
            lim = min(len(obs[j % 5]), n[j % 5])
            if j >= 5:
                for i in range(lim):
                    obs_f[base + i] = 1. # reserved function, it can be used for different visibility of policy or value, but I didn't use it.
            else:
                for i in range(lim):
                    obs_f[base + i * s_size_i[j]:base + (i + 1)* s_size_i[j]] = obs[j][i] 
            base += s_size_i[j] * n[j]

        position_x = (player.centerPos.x) / self.server.config.borderWidth * 2 # [-1, 1]
        position_y = (player.centerPos.y) / self.server.config.borderHeight * 2 # [-1, 1]
        #obs_f[-28:] are global information
        obs_f[-1] = 0 # all zeros are reserved bit
        obs_f[-2] = 0
        obs_f[-4] = position_x
        obs_f[-3] = position_y
        obs_f[-5] = 0
        obs_f[-6] = 0
        obs_f[-7] = player.centerPos.sqDist() / self.server.config.r
        obs_f[-8] = b_x
        obs_f[-9] = b_y
        obs_f[-10] = len(obs[0])
        obs_f[-11] = len(obs[1])
        obs_f[-12] = len(obs[2])
        obs_f[-13] = len(obs[3])
        obs_f[-14] = len(obs[4])
        obs_f[-15] = player.maxcell().radius / 400
        obs_f[-16] = player.mincell().radius / 400
        obs_f[-19:-16] = self.last_action[id * 3 : id * 3 + 3]
        obs_f[-20] = self.bot_speed
        obs_f[-21] = (self.killed[id] != 0)
        obs_f[-22] = (self.killed[1 - id] != 0)
        obs_f[-23] = sum([c.mass for c in player.cells]) / 50
        obs_f[-24] = sum([c.mass for c in self.agents[1 - id].cells]) / 50
        obs_f[-25] = 0
        obs_f[-26] = 0
        obs_f[-27] = 0
        obs_f[-28] = 0
                
        return deepcopy(obs_f)

    def cell_obs(self, cell, player, id):
        if cell.cellType == 0:
            # player features
            boost_x = (cell.boostDistance * cell.boostDirection.x) / self.server.config.splitVelocity # [-1, 1]
            boost_y = cell.boostDistance * cell.boostDirection.y / self.server.config.splitVelocity # [-1, 1]
            radius = cell.radius / 400
            log_radius = np.log(cell.radius / 100)
            position_x = (cell.position.x) / self.server.config.borderWidth * 2 # [-1, 1]
            position_y = (cell.position.y) / self.server.config.borderHeight * 2 # [-1, 1]
            relative_position_x = (cell.position.x - player.centerPos.x) / self.server.config.serverViewBaseX * 2 # [-1, 1]
            relative_position_y = (cell.position.y - player.centerPos.y) / self.server.config.serverViewBaseY * 2 # [-1, 1]
            v_x = (cell.position.x - cell.last_position.x) / self.server.config.serverViewBaseX * 2 * 30
            v_y = (cell.position.y - cell.last_position.y) / self.server.config.serverViewBaseY * 2 * 30
            features_player = [relative_position_x, relative_position_y, position_x, position_y, boost_x, boost_y, radius, log_radius, float(cell.canRemerge == True), relative_position_x ** 2 + relative_position_y ** 2, v_x, v_y, float(cell.radius * 1.15 > player.maxcell().radius), float(cell.radius * 1.15 > player.mincell().radius), cell.position.sqDist() / self.server.config.r]
            if cell.owner == player:
                c_t = 0
                if boost_x or boost_y:self.split[id] = True
            elif cell.owner.pID < self.num_agents:c_t = 4
            else:c_t = 3
            return c_t, features_player

        elif cell.cellType == 1:
            # food features
            radius = (cell.radius - (self.server.config.foodMaxRadius + self.server.config.foodMinRadius) / 2) / (self.server.config.foodMaxRadius - self.server.config.foodMinRadius) * 2
            log_radius = np.log(cell.radius / ((self.server.config.foodMaxRadius + self.server.config.foodMinRadius) / 2))
            position_x = (cell.position.x) / self.server.config.borderWidth * 2  # [-1, 1]
            position_y = (cell.position.y) / self.server.config.borderHeight * 2  # [-1, 1]
            relative_position_x = (cell.position.x - player.centerPos.x) / self.server.config.serverViewBaseX * 2  # [-1, 1]
            relative_position_y = (cell.position.y - player.centerPos.y) / self.server.config.serverViewBaseY * 2  # [-1, 1]
            features_food = [relative_position_x, relative_position_y, position_x, position_y,  radius, log_radius, relative_position_x ** 2 + relative_position_y ** 2]
            return cell.cellType, features_food

        elif cell.cellType == 2:
            # virus features
            boost_x = (cell.boostDistance * cell.boostDirection.x) / self.server.config.splitVelocity  # [-1, 1]
            boost_y = cell.boostDistance * cell.boostDirection.y / self.server.config.splitVelocity  # [-1, 1]
            radius = (cell.radius - (self.server.config.virusMaxRadius + self.server.config.virusMinRadius) / 2) / (self.server.config.virusMaxRadius - self.server.config.virusMinRadius) * 2
            log_radius = np.log(cell.radius / ((self.server.config.virusMaxRadius + self.server.config.virusMinRadius) / 2))
            position_x = (cell.position.x) / self.server.config.borderWidth * 2  # [-1, 1]
            position_y = (cell.position.y) / self.server.config.borderHeight * 2  # [-1, 1]
            relative_position_x = (cell.position.x - player.centerPos.x) / self.server.config.serverViewBaseX * 2  # [-1, 1]
            relative_position_y = (cell.position.y - player.centerPos.y) / self.server.config.serverViewBaseY * 2  # [-1, 1]
            features_virus = [relative_position_x, relative_position_y, position_x, position_y, relative_position_x ** 2 + relative_position_y ** 2]
            return cell.cellType, features_virus

        elif cell.cellType == 3:
            return None # I didn't consider action and observation of ejection also I still implement it.
            # ejected mass features
            boost_x = (cell.boostDistance * cell.boostDirection.x) / self.server.config.splitVelocity  # [-1, 1]
            boost_y = cell.boostDistance * cell.boostDirection.y / self.server.config.splitVelocity  # [-1, 1]
            position_x = (cell.position.x - self.server.config.borderWidth / 2) / self.server.config.borderWidth * 2  # [-1, 1]
            position_y = (cell.position.y - self.server.config.borderHeight / 2) / self.server.config.borderHeight * 2  # [-1, 1]
            relative_position_x = (cell.position.x - player.centerPos.x + 0 * self.server.config.serverViewBaseX / 2) / self.server.config.serverViewBaseX * 2  # [-1, 1]
            relative_position_y = (cell.position.y - player.centerPos.y + 0 * self.server.config.serverViewBaseY / 2) / self.server.config.serverViewBaseY * 2  # [-1, 1]
            features_ejected = [boost_x, boost_y, position_x, position_y, relative_position_x, relative_position_y]            
            return cell.cellType, features_ejected

    def parse_reward(self, player, id):
        mass_reward, kill_reward, killed_reward = self.calc_reward(player, id)
        if mass_reward < 0 and self.reward_settings == "agg":mass_reward = 0 # no death penalty.
        if mass_reward > 0:
            if kill_reward:
                self.hit[id][2] += 1
            elif self.split[id]:self.hit[id][0] += 1
            elif self.near:self.hit[id][3] += 1
            else:self.hit[id][1] += 1 # numbers of 4 events
                
        if len(player.cells) == 0:
            self.t_killed[id] += 1
        # reward for being big, not dead, eating part of others, killing all of others, not be eaten by someone
        # when the agent eats another outside agent, kill_reward will be mass_reward * (-1)
        reward = mass_reward * self.mass_reward_eps + \
                 kill_reward * self.kill_reward_eps[id] + \
                 killed_reward * self.killed_reward_eps
        reward2 = mass_reward * self.mass_reward_eps + \
                 killed_reward * self.killed_reward_eps
        return reward, reward2

    def calc_reward(self, player, id):
        mass_reward = sum([c.mass for c in player.cells])
        if self.last_mass[id] is None:
            mass_reward = 0
        else:mass_reward -= self.last_mass[id]
        self.last_mass[id] = sum([c.mass for c in player.cells])
        kill_reward = player.killreward
        killedreward = player.killedreward
        return mass_reward, kill_reward, killedreward

    def add_dir(self, a): # can be used to add multiple directions of the agent to render, add_dir should be used before render. a = [direction_x_0, direction_y_0, direction_x_1, direction_y_1, ... , direction_x_m-1, direction_y_m-1], m = number of different directions.

        self.dir = deepcopy(a)

    '''    
    function render

        param:

            playeridx: int, id of players to be rendered
            mode: str, two options: rgb_array": render will return rgb_array, "human": render will only return whether window is still open.
            name: str, the name of saved gif file
    '''
    def render(self, playeridx, mode = 'human', name = ""):

        if self.viewer is None:
            self.viewer = rendering.Viewer(self.server.config.serverViewBaseX, self.server.config.serverViewBaseY)
            self.render_border()
            self.render_grid()

        bound = self.players[playeridx].get_view_box()
        self.viewer.set_bounds(*bound)

        self.geoms_to_render = []
        self.render_dir(self.players[playeridx].centerPos)
        for node in self.players[playeridx].viewNodes:
            self.add_cell_geom(node)

        self.geoms_to_render = sorted(self.geoms_to_render, key=lambda x: x.order)
        for geom in self.geoms_to_render:
            self.viewer.add_onetime(geom)

        return self.viewer.render(return_rgb_array=mode == 'rgb_array', name = name)

    def render_border(self):
        map_left = - self.server.config.borderWidth / 2
        map_right = self.server.config.borderWidth / 2
        map_top = - self.server.config.borderHeight / 2
        map_bottom = self.server.config.borderHeight / 2
        line_top = rendering.Line((map_left, map_top), (map_right, map_top))
        line_top.set_color(0, 0, 0)
        self.viewer.add_geom(line_top)
        line_bottom = rendering.Line((map_left, map_bottom), (map_right, map_bottom))
        line_bottom.set_color(0, 0, 0)
        self.viewer.add_geom(line_bottom)
        line_left = rendering.Line((map_left, map_top), (map_left, map_bottom))
        line_left.set_color(0, 0, 0)
        self.viewer.add_geom(line_left)
        map_right = rendering.Line((map_right, map_top), (map_right, map_bottom))
        map_right.set_color(0, 0, 0)
        self.viewer.add_geom(map_right)
        cellwall = rendering.make_circle(radius = self.server.config.r, res = 50, filled = False)
        cellwall.set_color(0, 0, 0)
        self.viewer.add_geom(cellwall)

    def render_grid(self):
        map_left = - self.server.config.borderWidth / 2
        map_right = self.server.config.borderWidth / 2
        map_top = - self.server.config.borderHeight / 2
        map_bottom = self.server.config.borderHeight / 2
        for i in range(0, int(map_right), 100):
            line = rendering.Line((i, map_top), (i, map_bottom))
            line.set_color(0.8, 0.8, 0.8)
            self.viewer.add_geom(line)
            line = rendering.Line((-i, map_top), (-i, map_bottom))
            line.set_color(0.8, 0.8, 0.8)
            self.viewer.add_geom(line)

        for i in range(0, int(map_bottom), 100):
            line = rendering.Line((map_left, i), (map_right, i))
            line.set_color(0.8, 0.8, 0.8)
            self.viewer.add_geom(line)
            line = rendering.Line((map_left, -i), (map_right, -i))
            line.set_color(0.8, 0.8, 0.8)
            self.viewer.add_geom(line)

    def render_dir(self, center):

        for i in range(len(self.dir)):
            line = rendering.Line((0, 0), (self.dir[i][0] * 500, self.dir[i][1] * 500))
            line.set_color((len(self.dir) - i) / len(self.dir), i / len(self.dir), 0)
            line.order = i
            xform = rendering.Transform()
            line.add_attr(xform)
            xform.set_translation(center.x, center.y)
            self.geoms_to_render.append(line)

    def add_cell_geom(self, cell):
        if cell.cellType == 0:
            cellwall = rendering.make_circle(radius=cell.radius)
            cellwall.set_color(cell.color.r * 0.75 / 255.0, cell.color.g * 0.75 / 255.0 , cell.color.b * 0.75 / 255.0)
            xform = rendering.Transform()
            cellwall.add_attr(xform)
            xform.set_translation(cell.position.x, cell.position.y)
            cellwall.order = cell.radius
            self.geoms_to_render.append(cellwall)

            geom = rendering.make_circle(radius=cell.radius - max(10, cell.radius * 0.1))
            geom.set_color(cell.color.r / 255.0, cell.color.g / 255.0, cell.color.b / 255.0)
            xform = rendering.Transform()
            geom.add_attr(xform)
            xform.set_translation(cell.position.x, cell.position.y)
            if cell.owner.maxradius < self.server.config.virusMinRadius:
                geom.order = cell.owner.maxradius + 0.0001
            elif cell.radius < self.server.config.virusMinRadius:
                geom.order = self.server.config.virusMinRadius - 0.0001
            else:
                geom.order = cell.owner.maxradius + 0.0001
            self.geoms_to_render.append(geom)

        elif cell.cellType == 2:
            geom = rendering.make_circle(radius=cell.radius)
            geom.set_color(cell.color.r / 255.0, cell.color.g / 255.0, cell.color.b / 255.0, 0.6)
            xform = rendering.Transform()
            geom.add_attr(xform)
            xform.set_translation(cell.position.x, cell.position.y)
            geom.order = cell.radius
            self.geoms_to_render.append(geom)

        else:
            geom = rendering.make_circle(radius=cell.radius)
            geom.set_color(cell.color.r / 255.0, cell.color.g / 255.0, cell.color.b / 255.0)
            xform = rendering.Transform()
            geom.add_attr(xform)
            xform.set_translation(cell.position.x, cell.position.y)
            geom.order = cell.radius
            self.geoms_to_render.append(geom)


    def close(self):
            if self.viewer is not None:
                self.viewer.close()
                self.viewer = None

def onehot(d, ndim):
    v = [0. for i in range(ndim)]
    v[d] = 1.
    return v
