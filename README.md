# Agar.io

<p align="center"><img src="https://github.com/staghuntrpg/agar/blob/main/gif/agar_demo.gif" align="middle" /></p>

 [*Agar*](http://en.wikipedia.org/wiki/Agar.io) is a popular multi-player online game. Players control one or more cells in a Petri dish. The goal is to gain as much mass as possible by eating cells smaller than the player's cell while avoiding being eaten by larger ones. Larger cells move slower. Each player starts with one cell but can split a sufficiently large cell into two, allowing them to control multiple cells. The control is performed by mouse motion: all the cells of a player move towards the mouse position. We transform the Free-For-All (FFA) mode of Agar (https://agar.io/) into an Reinforcement Learning (RL) environment and we believe it can be utilized as a new Multi-agent RL testbed for a wide range of problems, such as cooperation, team formation, intention modeling, etc.

This is the source code of Agar.io, which is used in the paper "Discovering Diverse Multi-agent Strategic Behavior via Reward Randomization" [arxiv](arxiv link). This repository is developed from the original environment code [(https://github.com/buoyancy99/PyAgar)](https://github.com/buoyancy99/PyAgar), but has been slightly modified to fit the algorithms used in [RPG (Reward-Randomized Policy Gradient)](https://github.com/staghuntrpg/RPG).

## 1. Installation

Agar.io is easy to install,  see the following command. If you encounter visualization problems with pyglet, we would suggest you to seek help from [official pyglet URL](https://github.com/pyglet/pyglet).

```
pip install pillow gym pyglet
```

## 2. User Guide

1. The Reinforcement Learning (RL) environment is defined in `Env.py`. This implementation supports multi-agent tasks, so you can specify any number of players (i.e. hyperparameter `num_controlled_agent`),  which means you are allowed to control multiple agents by passing a `[N, 3]` 2D array, where `N` is numbers of controlled agents, `3` is the dimension of action space. The action space for each agent can be described as `[mouse.x, mouse.y, Split/Feed/Non-operation]`, where `mouse.x, mouse.y` are continuous, while `Split/Feed/Non-operation` is discrete. There are two options for reward setting: `std` and `agg`, which correspond to the standard setting and aggressive setting of the paper. Note that this implementation only supports FFA mode (i.e. hyperparameter`gamemode=0`) 

2. The game configuration is defined in `Config.py`, we would suggest you to keep the default parameters.

## 3. Enjoy

We provide `HumanControl.py` for quick check and sample use.  You can use the following command to play with mouse and keyboard. There are 2 agents by default, and you can change `num_agents` to any number you want.  Hope you enjoy this game:)

```
python HumanControl.py
```

## 4. Citation

If you use Agar.io in your research, you can cite us with: TODO

## 5. License

Agar.io is released under the [MIT license](https://github.com/staghuntrpg/agar/blob/main/LICENSE).


