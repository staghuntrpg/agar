# Agar.io

<div align=center>![Agar.io](./gif/agar_demo.gif)

 [*Agar*](http://en.wikipedia.org/wiki/Agar.io) is a popular multi-player online game. Players control one or more cells in a Petri dish. The goal is to gain as much mass as possible by eating cells smaller than the player's cell while avoiding being eaten by larger ones. Larger cells move slower. Each player starts with one cell but can split a sufficiently large cell into two, allowing them to control multiple cells. The control is performed by mouse motion: all the cells of a player move towards the mouse position. We transform the Free-For-All (FFA) mode of Agar (https://agar.io/) into an Reinforcement Learning (RL) environment and we believe it can be utilized as a new Multi-agent RL testbed for a wide range of problems, such as cooperation, team formation, intention modeling, etc.

This is the source code of Agar.io, which is used in the paper "Discovering Diverse Multi-agent Strategic Behavior via Reward Randomization"[(TODO: arxiv link)](arxiv link). The original repository can be found at [https://github.com/buoyancy99/PyAgar](https://github.com/buoyancy99/PyAgar).

## User Guide

1. The environment is defined in `Env.py`. This implementation supports multi-agent tasks, so you can specify any number of players,  i.e. you are allowed to control multiple agents by passing a `[N, 3]` 2D array. The state space for each agent is `[mouse.x, mouse.y, Split/Feed/Non-operation]`. 
2. The file `HumanControl.py` is for sample use.  You can just run `python HumanControl.py` to play with mouse and keyboard. Hope you enjoy this game:)

## Citation

If you use Agar.io in your research, you can cite us with: TODO

## License

Agar.io is released under the [MIT license](https://github.com/staghuntrpg/agar/blob/main/LICENSE).


