# Multi_Agent_AI

Multi-agent AI system to solve different Sokoban-like levels written in Python (client side).  
Repository developed for the DTU course _Artificial Intelligence and Multi Agent Systems_.

## Run a level
The server-side environment, provided during the course, runs in **Java**. In a Unix shell:
```bash
java -jar "$SERVER/server.jar" -l "$SERVER/levels/$lvl" -c "python searchclient/searchclient.py $method --max-memory $mem" -g 150 -t 300
```

where
* `$SERVER` is the path to this repository.
* `$method` is the search method (e.g. -bfs).
* `mem` is the memory threshold tu be used the program.

## Objectives
* [ ] Run _lvl1_ without getting an error.
* [ ] Create required maps.
* [ ] Choose a theoretical framework -> PPDL | BDI | POP | HTL.
* [ ] Choose a method of communication -> online-planing, deadlocks avoidance.
* [ ] Find paper for Sokoban-like with the chose framework and multiagent.
* [ ] Solve all the levels with the agent.
* [ ] Papers in AAAI style of 6 pages.
* [ ] Open the repository.
* [ ] Choose a license.

## Code guidelines
[Flake8](https://pypi.org/project/flake8/) and [black](https://github.com/ambv/black) it.
```bash
pip install flake8 black
```
