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
