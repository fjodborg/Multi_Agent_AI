# Communication notes

## 1. Task sharing

BDI.
There is a common goal (top-down).
To solve it, nodes can request tasks. Since task will be limited to colors, the tasks will be assigned
in a directed or limited manner (_directed contract_ and/or _limited broadcasting_).

1. Problem recognition. Check state solution, subdivide into problems (use colors and heuristics).

- Deadlock. Solve when agent is blocked. Agents are blind to boxes/agents that are not their color to find a path. Broadcast new task to unblock and bidding by heuristics.

2. Task broadcasting. Request someone to do the task.
3. Biding. Compare h.
4. Solve problem.

## 2. Result sharing

The common goal is subdivided and assigned to agents (bottom-up).
The smaller subproblems will be solved independently and combined.

1. Problem subdivision.
2. Sub-problem assignment.
3. Solve each subproblem.
4. Combine agents and subproblems.
5. Repeat 3-4 until solution is found for top problem.

## 3. Roadmap IMPLEMENTATION

- [x] Color.
- [x] Initial Problem recognition (subdivide goal state) top manager.
- [ ] Blind path solving.
- [ ] Bidding.
- [ ] Broadcast new tasks (agent-manager) in the way.
- [ ] Task costs.
