# Multi_Agent_AI

Multi-agent AI system to solve different Sokoban-like levels written in Python (client side).  
Repository developed for the DTU course _Artificial Intelligence and Multi Agent Systems_.

## Run a level

The server-side environment, provided during the course, runs in **Java**. In a Unix shell:

```bash
java -jar "$SERVER/server.jar" -l "$SERVER/levels/$lvl" -c "python multi_sokoban/searchclient.py $method --max-memory $mem" -g 150 -t 300
```

where

- `$SERVER` is the path to this repository.
- `$method` is the search method (e.g. -astar).
- `mem` is the memory threshold to be used the program.

This command is exposed through a [tiny script](./exe_serve.sh) for convenience. For instance:

```bash
exe_serve.sh SAD1.lvl -astar
```

## Objectives

- [x] Run _lvl1_ without getting an error.
- [ ] Create required maps.
- [x] Choose a theoretical framework -> PPDL | BDI | POP | HTL.
- [x] Choose a method of communication -> online-planing, deadlocks avoidance.
- [x] Find paper for Sokoban-like with the chosen framework and multiagent.
- [ ] Solve all the levels with the agent.
- [ ] Papers in AAAI style of 6 pages.
- [x] Open the repository.
- [ ] Choose a license.

## Installation

The python client was packed as a module to ease its use. Once cloned, it can be
installed from source via `pip`.

```bash
git clone https://github.com/FjodBorg/Multi_Agent_AI.git
cd Multi_Agent_AI
pip install .
```

After that, it should have installed `numpy` and the package is now accessible as
a regular python package.

```python
import multi_sokoban
```

Uninstalling the package can be done via pip.

```bash
pip uninstall multi_sokoban
```

## Code guidelines

[Flake8](https://pypi.org/project/flake8/) and [black](https://github.com/ambv/black) it.

```bash
pip install flake8 black
```
