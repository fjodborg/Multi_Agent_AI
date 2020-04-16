"""Astar search."""
from queue import PriorityQueue

from multi_sokoban import actions

from abc import ABC, abstractmethod

from typing import List, Callable

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
                # print(goalPositions,boxParams, state.getAgentByKey('0'))
                for goalPos in goalPositions:
                    for boxPos, _color in boxParams:
                        # boxPos = state.getAgentByKey(key)
                        # goalPos = state.getBoxesByKey(key)
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


def aStarSearch_func(initState):
    """Functional legacy approach."""
    global count
    # count = 0 should be static and only initialized in the start, it's needed for unique hashes
    frontier = PriorityQueue()
    leaf = initState
    calcHuristicsFor(leaf)

    while not leaf.isGoalState():
        exploredStates = leaf.explore()
        calcHuristicsFor(exploredStates)
        for state in exploredStates:
            count += 1
            # print(state.h, count)
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
            # print(goalPositions,boxParams, state.getAgentByKey('0'))
            for goalPos in goalPositions:
                for boxPos, _color in boxParams:
                    # boxPos = state.getAgentByKey(key)
                    # goalPos = state.getBoxesByKey(key)
                    totalCost += default_heuristic(boxPos, goalPos)
        state.h = state.g + totalCost


def test(nr):
    if nr == 0:
        # remember to make walls, otherwise it isn't bound to the matrix!
        state = actions.StateInit()
        # state2 = state.copy()
        state.addMap(
            [
                ["+", "+", "+", "+", "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", "+", "+", "+", "+"],
            ]
        )

        state.addAgent("0", (1, 2), "b")
        # state.addBox("B", (2, 2), "c")
        state.addBox("B", (2, 2), "c")
        state.addBox("B", (3, 2), "b")
        # state.addGoal("b", (2, 2))
        state.addGoal("b", (3, 1))
        # state.addGoal("c", (1, 3))
        # state.addGoal("c", (2, 1))
        print(state.map)
        path, goalState = aStarSearch(state)
        print(path, "\n", goalState.map, goalState.goals, goalState.boxes)
