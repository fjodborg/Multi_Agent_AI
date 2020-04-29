"""Components of the BDI loop."""
from copy import deepcopy
from typing import Callable, List

from .actions import StateInit
from .emergency_aStar import BestFirstSearch, calcHuristicsFor
from .memory import MAX_USAGE, get_usage
from .utils import STATUS, println, ResourceLimit, IncorrectTask


class Agent:
    """Implement the belief and backtrack cost."""

    def __init__(
        self,
        task: StateInit,
        strategy: BestFirstSearch,
        heuristic: Callable = calcHuristicsFor,
    ):
        """Initialize the agent wit a task."""
        self.task = task
        self.strategy = strategy
        self.heuristic = heuristic
        self.color = list(task.goals.values())[0][0][1]
        self.name = list(task.agents.keys())[0]
        self.init_pos = list(task.agents.values())[0][0][0]
        # status can be ok, fail or init
        self.status = STATUS.init

    def solve(self) -> List:
        """Solve the tasks by search."""
        searcher = self.strategy(self.task)
        println(
            f"goals -> {self.task.goals}\n"
            f"agents -> {self.task.agents}\nboxes -> {self.task.boxes}\n"
        )
        path = self.search(searcher)
        if path is None:
            self.task.forget_exploration()
            self.status = STATUS.fail
            return self.broadcast()
        else:
            self.status = STATUS.ok
            return path

    def add_task(self, task):
        """Merge task with previous task."""
        color = list(task.goals.values())[0][0][1]
        if color != self.color:
            IncorrectTask(f"Agent {self.name}: I'm {self.color}, not {color}.")
        self.task.goals = {**self.task.goals, **task.goals}

    def marginal_task_cost(self, broadcasted_task: StateInit) -> float:
        """Compute cost of adding task `broadcasted_task`."""
        color = list(broadcasted_task.goals.values())[0][0][1]
        if color != self.color:
            return float("Inf")
        c_ts = calcHuristicsFor(broadcasted_task)
        # the broadcasted task is guaranteed to have only one goal
        pos, color = list(broadcasted_task.goals.values())[0][0]
        c_union = float("inf")
        # TODO: Should consider t!!!!
        for task in self.tasks:
            joint_task = deepcopy(task)
            joint_task.addGoal(list(broadcasted_task.keys())[0], pos, color)
            c_union = min(c_union, calcHuristicsFor(joint_task))
        return c_union - c_ts

    def broadcast(self) -> StateInit:
        """Identify problem and formulate solution."""
        pass

    def search(self, strategy: BestFirstSearch) -> List:
        """Search function.

        Returns
        -------
        Path to the solutions (in actions) or None.

        """
        iterations = 0
        while not strategy.leaf.isGoalState():
            if iterations == 1000:
                println(f"{strategy.count} nodes explored")
                iterations = 0

            if get_usage() > MAX_USAGE:
                raise ResourceLimit("Maximum memory usage exceeded.")
                return None

            strategy.explore_and_add()

            if strategy.frontier_empty():
                println(f"Frontier empty! ({strategy.count} nodes explored)")
                return None

            strategy.get_and_remove_leaf()

            if strategy.leaf.isGoalState():
                println(
                    f"(Subproblem) Solution found with "
                    f"{len(strategy.leaf.explored)} nodes explored"
                )
                return strategy.walk_best_path()

            iterations += 1
