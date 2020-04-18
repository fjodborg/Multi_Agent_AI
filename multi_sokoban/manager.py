"""Task sharing MA communication."""
from copy import deepcopy
from typing import List

from .actions import StateInit
from .utils import println, ResourceLimit
from .memory import MAX_USAGE, get_usage
from .emergency_aStar import BestFirstSearch


class Manager:
    """Top manager that performs problem subdivision and task broadcasting."""

    def __init__(self, top_problem: StateInit, strategy: BestFirstSearch):
        """Initialize with the whole problem definition `top_problem`."""
        self.top_problem = top_problem
        self.strategy = strategy
        self.tasks = []
        # TODO: move status to BFS class
        self.status = []

    def run(self) -> List:
        """Perform the task sharing."""
        self.divide_problem()
        return self.solve_world()

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
            ext_agents = list(task.goals.keys())
            for external_agent in ext_agents:
                if external_goal != agent:
                    del task.agents[external_agent]
            self.tasks.append(task)
            self.status.append(None)

    def bidding(self, task: StateInit, agents):
        """Request a heuristic from the agents to solve a particular task."""
        raise NotImplementedError

    def broadcast_task(self, task: StateInit) -> str:
        """Request task for agents."""
        # a task is guaranteed to have exactly one goal
        color_of = list(task.goals)[0][1]
        ok_agents = [k for k, v in task.agents.items() if color_of == v[1]]
        if len(ok_agents) > 1:
            selected_agent = self.bidding(task, ok_agents)
        else:
            selected_agent = ok_agents[0]
        return selected_agent

    def solve_task(self, task) -> List:
        """Search for task.

        Returns
        -------
        Path to the solutions (in actions) or none.

        """
        searcher = self.strategy(task)
        return search(searcher)

    def solve_world(self) -> List:
        """Solve the top problem.

        Returns
        -------
        self.status:
            list of lists. Each sublist is a path of actions.

        """
        for task in self.tasks:
            path = self.solve_task(task)
            if path is not None:
                self.status[self.tasks.index(task)] = path
        return self.status


def search(strategy: BestFirstSearch) -> List:
    """Search function.

    Returns
    -------
    Path to the solutions (in actions) or none.

    """
    iterations = 0
    while not strategy.leaf.isGoalState():
        # println(self.strategy.leaf.h)
        if iterations == 1000:
            println(f"{strategy.count} nodes explored")
            iterations = 0

        if get_usage() > MAX_USAGE:
            raise ResourceLimit("Maximum memory usage exceeded.")
            return None

        strategy.get_and_remove_leaf()

        if strategy.frontier_empty():
            println("Frontier empty!")
            return None

        if strategy.leaf.isGoalState():
            return strategy.walk_best_path()

        iterations += 1
