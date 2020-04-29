"""Task sharing MA communication."""
from copy import deepcopy
from typing import List

from .actions import StateInit
from .bdi import Agent
from .emergency_aStar import BestFirstSearch
from .resultsharing import Resultsharing
from .utils import STATUS, println


class Manager:
    """Top manager that performs problem subdivision and task broadcasting."""

    def __init__(self, top_problem: StateInit, strategy: BestFirstSearch):
        """Initialize with the whole problem definition `top_problem`."""
        self.top_problem = top_problem
        self.strategy = strategy
        self.agents = {}
        self.solutions = None
        self.nodes_explored = 0

    def run(self) -> List:
        """Perform the task sharing."""
        self.divide_problem()
        self.solve_world()

        self.solveCollision()
        # println(new_paths)

        return self.join_tasks()

    def bidding(self, task: StateInit, agents) -> str:
        """Request heuristic from the agents to solve a particular task."""
        raise NotImplementedError
        min_marginal_cost = float("inf")
        for agent in agents:
            # WARNING: could be implemented now but let's wait for BDI
            marginal_cost = agent.marginal_cost(task)
            # greater or equal to guarantee a selected agent
            if min_marginal_cost >= marginal_cost:
                min_marginal_cost = marginal_cost
                selected_agent = agent
        return selected_agent

    def divide_problem(self):
        """Subdivide the problem in terms of box colors."""
        for goal in self.top_problem.goals:
            # create subproblem and remove other goals
            task = deepcopy(self.top_problem)
            ext_goals = list(task.goals.keys())
            for external_goal in ext_goals:
                if external_goal != goal:
                    task.deleteGoal(external_goal)

            # select best agent and remove other agents
            agent = self.broadcast_task(task)
            ext_agents = list(task.agents.keys())
            for external_agent in ext_agents:
                if external_agent != agent:
                    # del task.agents[external_agent]
                    task.deleteAgent(external_agent)
            if agent in self.agents:
                self.agents[agent].add_task(task)
            else:
                self.agents[agent] = Agent(task, self.strategy)

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
        return sorted(self.agents)

    def solveCollision(self):
        # findAndResolveCollisionOld(self) # This function can be found in resultsharing.py

        # TODO check for empty frontiers
        # check for traceback possiblities
        #

        rs = Resultsharing(self)
        rs.findAndResolveCollision()  # This function can be found in resultsharing.py
        # println(pos)
        # println(self.tasks['a'][0].map)

    def solve_world(self):
        """Solve the top problem."""
        paths = {}
        while len(paths) != len(self.agents):
            for name, agent in self.agents.items():
                solution = agent.solve()
                if agent.status == STATUS.fail:
                    ok_agent = self.broadcast_task(solution)
                    println(f"Agent {name} broadcasted task for {solution.goals}")
                    self.agents[ok_agent].add_task(solution)
                else:
                    paths[name] = solution
        self.solutions = [paths[agent_name] for agent_name in self.sort_agents()]

    def join_tasks(self) -> List:
        """Join all the task in one big path.

        Returns
        -------
        list of actions to the best solution

        """
        paths = self.solutions
        println(paths)
        return [";".join(actions) for actions in zip(*paths)]
