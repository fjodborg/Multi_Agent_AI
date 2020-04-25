"""Task sharing MA communication."""
from copy import deepcopy
from typing import List

from .actions import StateInit
from .emergency_aStar import BestFirstSearch, calcHuristicsFor
from .memory import MAX_USAGE, get_usage
from .utils import ResourceLimit, println


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
        self.nodes_explored = 0

    def run(self) -> List:
        """Perform the task sharing."""
        self.divide_problem()
        self.solve_world()
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

    def bidding(self, task: StateInit, agents) -> str:
        """Request a heuristic from the agents to solve a particular task."""
        raise NotImplementedError
        min_marginal_cost = float("inf")
        for agent in agents:
            # WARNING: could be implemented now but let's wait for BDI
            marginal_cost = marginal_task_cost(agent.tasks, task)
            # greater or equal to guarantee a selected agent
            if min_marginal_cost >= marginal_cost:
                min_marginal_cost = marginal_cost
                selected_agent = agent
        return selected_agent

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
        self.nodes_explored += strategy.count
        return path, strategy.leaf

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
                task.explored = set()
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
        # WARNING: ths fails if there are more than 10 agents
        sorted_agents = sorted(
            list(self.status.keys()), key=lambda a: self.agent_to_status[a]
        )
        paths = [self.status[agent] for agent in sorted_agents]
        println(paths)
        return [";".join(actions) for actions in zip(*paths)]


# Members of Manager
def search(strategy: BestFirstSearch) -> List:
    """Search function.

    Returns
    -------
    Path to the solutions (in actions) or none.

    """

    #  Legacy function, but it takes a strategy rather than a leaf as argument
    # return aStarSearch_func(strategy)

    # This version gives an errors in some scenareos
    iterations = 0
    while not strategy.leaf.isGoalState():
        if iterations == 1000:
            println(f"{strategy.count} nodes explored")
            iterations = 0

        if get_usage() > MAX_USAGE:
            raise ResourceLimit("Maximum memory usage exceeded.")
            return None, strategy

        strategy.get_and_remove_leaf()
        """
        if strategy.frontier_empty():
            println("Frontier empty!")
            return None, strategy
        """

        if strategy.leaf.isGoalState():
            println(
                f"(Subproblem) Solution found with "
                f"{len(strategy.leaf.explored)} nodes explored"
            )
            return strategy.walk_best_path(), strategy

        iterations += 1


def marginal_task_cost(ongoing_tasks: List, broadcasted_task: StateInit) -> float:
    """Compute cost of adding task `broadcasted_task` to current `ongoing_tasks`.

    Should consider t.
    """
    c_ts = calcHuristicsFor(broadcasted_task)
    # the broadcasted task is guaranteed to have only one goal
    pos, color = list(broadcasted_task.goals.values())[0][0]
    c_union = float("inf")
    # of the ongoing tasks, always pick the one with the least joint heurisitic
    for task in ongoing_tasks:
        joint_task = deepcopy(task)
        joint_task.addGoal(list(broadcasted_task.keys())[0], pos, color)
        c_union = min(c_union, calcHuristicsFor(joint_task))
    return c_union - c_ts
