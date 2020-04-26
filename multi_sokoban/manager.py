"""Task sharing MA communication."""
from copy import deepcopy
from typing import List

from .actions import StateInit
from .emergency_aStar import (BestFirstSearch, aStarSearch_func,
                              calcHuristicsFor)
from .memory import MAX_USAGE, get_usage
from .utils import ResourceLimit, println
from .resultsharing import (findAndResolveCollision, findAndResolveCollisionOld)


class Manager:
    """Top manager that performs problem subdivision and task broadcasting."""

    def __init__(self, top_problem: StateInit, strategy: BestFirstSearch):
        """Initialize with the whole problem definition `top_problem`."""
        self.top_problem = top_problem
        self.strategy = strategy
        self.tasks = {}
        # TODO: move status to BFS class
        self.status = {}
        self.freed_agents = {}
        self.agent_to_status = {}

    def run(self) -> List:
        """Perform the task sharing."""
        self.divide_problem()
        self.solve_world()

        new_paths = self.choose_priority_path()
        # println(new_paths)

        return self.join_tasks()

    def divide_problem(self):
        """Subdivide the problem in terms of box colors."""
        for goal in self.top_problem.goals:
            # create subproblem and remove other goals
            task = deepcopy(self.top_problem)
            ext_goals = list(task.goals.keys())
            for external_goal in ext_goals:
                if external_goal != goal:
                    del task.goals[external_goal]
            # select best agent and remove other agents
            agent = self.broadcast_task(task)
            ext_agents = list(task.agents.keys())
            for external_agent in ext_agents:
                if external_agent != agent:
                    del task.agents[external_agent]

            self.tasks[goal] = (task, agent)
            self.status[goal] = None
            self.agent_to_status[goal] = agent

    def bidding(self, task: StateInit, agents):
        """Request a heuristic from the agents to solve a particular task."""
        raise NotImplementedError

    def broadcast_task(self, task: StateInit) -> str:
        """Request task for agents."""
        # a task is guaranteed to have exactly one goal
        # color_of = list(task.goals)[0][1]
        color_of = list(task.goals.values())[0][0][1]
        ok_agents = [k for k, v in task.agents.items() if color_of == v[0][1]]
        if len(ok_agents) > 1:
            selected_agent = self.bidding(task, ok_agents)
        else:
            selected_agent = ok_agents[0]
        return selected_agent

    def sort_agents(self):
        """Return sorted agents by name of agent (0-10)."""
        # WARNING: ths fails if there are more than 10 agents
        return sorted(list(self.status.keys()), key=lambda a: self.agent_to_status[a])

    def solve_task(self, task) -> List:
        """Search for task.

        Returns
        -------
        Path to the solutions (in actions) or none.

        """
        searcher = self.strategy(task)
        println(
            f"goals -> {task.goals}\n"
            f"agents -> {task.agents}\nboxes -> {task.boxes}\n"
        )
        path, strategy = search(searcher)
        if path is None:
            task.forget_exploration()
        return path, strategy.leaf

    def convert2pos(self, initPos, paths):
        pos = initPos

        i = 0
        # println(f"pos: {pos}")
        for agt in paths:
            if agt is None:
                continue
            for action in agt:
                prefix = action[0]
                # println(f"pos: {pos[i][-1]}")
                if type(pos[i][-1]) == list:
                    [row, col] = pos[i][-1][0]
                else:
                    [row, col] = pos[i][-1]
                # println(f"row:{row},col:{col}")
                if prefix == "N":
                    pos[i].append((row, col))
                elif prefix == "M":
                    [drow, dcol] = self.top_problem.dir[action[-2:-1]]
                    pos[i].append((row + drow, col + dcol))
                elif prefix == "P":
                    if action[0:4] == "Push":
                        [drow1, dcol1] = self.top_problem.dir[action[-4:-3]]
                        [drow2, dcol2] = self.top_problem.dir[action[-2:-1]]
                        # println(f"{row},{drow1}")

                        [row1, col1] = (row + drow1, col + dcol1)
                        [row2, col2] = (row1 + drow2, col1 + dcol2)
                        pos[i].append([(row1, col1), (row2, col2)])
                    else:
                        [drow1, dcol1] = self.top_problem.dir[action[-4:-3]]
                        [drow2, dcol2] = self.top_problem.dir[action[-2:-1]]
                        # println(f"{row},{drow1}")

                        [row1, col1] = (row + drow1, col + dcol1)
                        [row2, col2] = (row, col)
                        pos[i].append([(row1, col1), (row2, col2)])

            i += 1

        return pos


    def addToHash(self, timeTable, pos, time, identity):
        if (pos, time) in timeTable:
            timeTable[pos, time].append(identity)
        else:
            timeTable[pos, time] = [identity]

    def generateHash(self, pos, paths):
        timeTable = {}

        agtColor = self.sort_agents()
        for agtIdx in range(len(paths)):
            for time in range(len(pos[agtIdx])):
                posAtTime = pos[agtIdx][time]
                if type(posAtTime) == list:
                    self.addToHash(timeTable, posAtTime[0], time, agtIdx)
                    # TODO find a solution to figure out how to identify the box
                    self.addToHash(timeTable, posAtTime[1], time, agtIdx)#agtColor[agtIdx])
                else:
                    self.addToHash(timeTable, posAtTime, time, agtIdx)
        return timeTable


    def choose_priority_path(self):
        sorted_agents = self.sort_agents()

        # initpos = [[agent[0][0]] for agent in self.top_problem.agents.values()]
        paths = [self.status[agent] for agent in sorted_agents if self.status[agent]]

        initpos = [
            [self.top_problem.agents[self.agent_to_status[agent]][0][0]]
            for agent in sorted_agents
        ]
        pos = self.convert2pos(initpos, paths)
        timeTable = self.generateHash(pos, paths)
        findAndResolveCollisionOld(pos, paths) # This function can be found in resultsharing.py
        #findAndResolveCollision(pos, paths, timeTable) # This function can be found in resultsharing.py
        # println(pos)
        # println(self.tasks['a'][0].map)

        for agt in range(len(pos)):
            for i in range(len(pos[agt]) - 1):
                if pos[agt][i] == pos[agt][i + 1]:
                    if len(paths[agt]) > 0:
                        paths[agt].insert(i, "NoOp")
                    else:
                        paths[agt].append("NoOp")
            # while len(paths[agt]) < len(pos[agt])-1:
            # paths[agt].append("NoOp")

        # println(paths)

        return paths

    def solve_world(self):
        """Solve the top problem."""
        to_del = []
        for goal, val in self.tasks.items():
            task, agent = val
            if agent in self.freed_agents:
                # substitute this task with previous task using the agent
                prev_task = self.freed_agents[agent]
                pos, color = list(task.goals.values())[0][0]
                prev_task.addGoal(goal, pos, color)
                task = prev_task
                task.forget_exploration()
                to_del.append(goal)
            path, last_state = self.solve_task(task)
            if path is not None:
                self.freed_agents[agent] = last_state
                if goal not in to_del:
                    self.tasks[goal] = (last_state, self.tasks[goal][1])
                prev_goal = list(last_state.goals.keys())[0]
                self.status[prev_goal] = path
                # make sure that we are not removing the correct one
                if prev_goal in to_del:
                    to_del.remove(prev_goal)

        for goal in to_del:
            del self.status[goal]
            del self.tasks[goal]

    def join_tasks(self) -> List:
        """Join all the task in one big path.

        Returns
        -------
        list of actions to the best solution

        """
        sorted_agents = self.sort_agents()

        paths = [self.status[agent] for agent in sorted_agents]
        println(paths)
        return [";".join(actions) for actions in zip(*paths)]


def search(strategy: BestFirstSearch) -> List:
    """Search function.

    Returns
    -------
    Path to the solutions (in actions) or none.

    """
    iterations = 0
    while not strategy.leaf.isGoalState():
        if iterations == 1000:
            println(f"{strategy.count} nodes explored")
            iterations = 0

        if get_usage() > MAX_USAGE:
            raise ResourceLimit("Maximum memory usage exceeded.")
            return None, strategy

        strategy.explore_and_add()

        if strategy.frontier_empty():
            println(f"Frontier empty! ({strategy.count} nodes explored)")
            return None, strategy

        strategy.get_and_remove_leaf()

        if strategy.leaf.isGoalState():
            println(f"Solution found with {len(strategy.leaf.explored)} nodes explored")
            return strategy.walk_best_path(), strategy

        iterations += 1

