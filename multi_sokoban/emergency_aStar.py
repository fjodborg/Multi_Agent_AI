"""Astar search."""
from abc import ABC, abstractmethod
from queue import PriorityQueue
from typing import Callable, List

from multi_sokoban import actions

count = 0


def default_heuristic(a, b):
    """Apply simple heuristic."""
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


class BestFirstSearch(ABC):
    """Abstract class for BFS."""

    def __init__(
        self,
        init_state: actions.StateInit,
        heuristic: Callable = default_heuristic,
    ):
        """Initialize strategy."""
        self.frontier = PriorityQueue()
        self.heuristic = heuristic
        self.leaf = init_state
        self.count = 0
        self.calc_heuristic_for(self.leaf)

    @abstractmethod
    def get_and_remove_leaf(self):
        """Depend on the heuristic method."""
        raise NotImplementedError

    def calc_heuristic_for(self, states: List[actions.StateInit]):
        """Calculate heuristic for states in place."""
        if type(states) is not list:
            states = [states]

        for state in states:
            total_cost = 0
            keys = state.getGoals()
            for key in keys:
                goalPositions = state.getGoalsByKey(key)
                boxParams = state.getBoxesByKey(key)
                for goalPos in goalPositions:
                    for boxPos, _color in boxParams:
                        total_cost += self.heuristic(boxPos, goalPos)
            state.h = state.g + total_cost

    def walk_best_path(self):
        """Return the solution."""
        return self.leaf.bestPath()

    def frontier_empty(self):
        """Return if solution couldn't be solved."""
        return self.frontier.empty()


class aStarSearch(BestFirstSearch):
    """BFS with A*."""

    def get_and_remove_leaf(self):
        """Apply the heuristic and update the frontier."""
        explored_states = self.leaf.explore()
        self.calc_heuristic_for(explored_states)

        for state in explored_states:
            self.count += 1
            self.frontier.put((state.h, self.count, state))
        self.leaf = self.frontier.get()[2]

    def __str__(self):
        """Printable descriptuion."""
        return "A* Best First Search"


def aStarSearch_func(initState):
    """Functional legacy approach."""
    global count
    # count = 0 should be static and only initialized in the start,
    # it's needed for unique hashes
    frontier = PriorityQueue()
    leaf = initState
    calcHuristicsFor(leaf)

    while not leaf.isGoalState():
        exploredStates = leaf.explore()
        calcHuristicsFor(exploredStates)
        for state in exploredStates:
            count += 1
            frontier.put((state.h, count, state))
        leaf = frontier.get()[2]

    return leaf.bestPath(), leaf


def calcHuristicsFor(states):
    """Functional legacy approach."""
    if type(states) is not list:
        states = [states]

    for state in states:
        totalCost = 0
        keys = state.getGoals()
        for key in keys:
            goalPositions = state.getGoalsByKey(key)
            boxParams = state.getBoxesByKey(key)
            for goalPos in goalPositions:
                for boxPos, _color in boxParams:
                    totalCost += default_heuristic(boxPos, goalPos)
        state.h = state.g + totalCost
