"""Astar search."""
from abc import ABC, abstractmethod
from queue import PriorityQueue
from typing import Callable, List

from multi_sokoban import actions

from .utils import println

count = 0


def default_heuristic(a, b):
    """Apply simple heuristic."""
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


class BestFirstSearch(ABC):
    """Abstract class for BFS."""

    def __init__(
        self, init_state: actions.StateInit, heuristic: Callable = default_heuristic,
    ):
        """Initialize strategy."""
        self.frontier = PriorityQueue()
        self.heuristic = heuristic
        self.leaf = init_state
        self.count = 0
        calcHuristicsFor(self.leaf)

    def get_and_remove_leaf(self):
        """Depend on the heuristic method."""
        self.leaf = self.frontier.get()[2]

    '''
        #try and use maps instead of for loops!!

        def stateMethod(state, goalKey):

        def keyMethod(key):

        def posMethod1(a):

        def posMethod2(a):

        def agentMethod1(state, agentKey, boxPos, goalPos):
    '''

    @abstractmethod
    def explore_and_add(self):
        """Explore leaf, calc heursitic and add to frontier."""
        raise NotImplementedError

    def walk_best_path(self):
        """Return the solution."""
        return self.leaf.bestPath()

    def frontier_empty(self):
        """Return if solution couldn't be solved."""
        return self.frontier.empty()


class greedySearch(BestFirstSearch):
    """BFS with greedy."""

    def explore_and_add(self):
        """Apply the heuristic and update the frontier."""
        explored_states = self.leaf.explore()
        calcHuristicsFor(explored_states)

        for state in explored_states:
            self.count += 1
            self.frontier.put((state.h, self.count, state))

    def __str__(self):
        """Printable descriptuion."""
        return "greedy Best First Search"


class aStarSearch(BestFirstSearch):
    """BFS with A*."""

    def explore_and_add(self):
        """Apply the heuristic and update the frontier."""
        explored_states = self.leaf.explore()
        calcHuristicsFor(explored_states)

        for state in explored_states:
            self.count += 1
            self.frontier.put((state.f, self.count, state))

    def __str__(self):
        """Printable descriptuion."""
        return "A* Best First Search"


def aStarSearch_func(strategy):
    """Functional legacy approach."""
    global count
    # count = 0 should be static and only initialized in the start,
    # it's needed for unique hashes

    frontier = PriorityQueue()
    leaf = strategy.leaf
    calcHuristicsFor(leaf)
    while not leaf.isGoalState():
        exploredStates = leaf.explore()
        calcHuristicsFor(exploredStates)

        for state in exploredStates:
            count += 1
            frontier.put((state.f, count, state))

        leaf = frontier.get()[2]

    return leaf.bestPath(), strategy


def calcHuristicsFor(states):
    """Calculate heuristic for states in place."""
    if type(states) is not list:
        states = [states]
    if len(states) == 0:
        return None

    goalKeys = states[0].getGoalKeys()

    for state in states:
        boxGoalCost = 0
        agtBoxCost = 0
        agtBoxCosts = []
        for key in goalKeys:
            goalParams = state.getGoalsByKey(key)
            boxParams = state.getBoxesByKey(key)
            # maybe add some temporary costs here for each key

            # find every position of goals and boxes with the given key
            for goalPos, goalColor in goalParams:
                boxGoalCosts = []
                # agtBoxCosts = []
                for boxPos, _ in boxParams:
                    # only take agents with the same color as goalColor
                    agentKeys = state.getAgentsByColor(goalColor)

                    if default_heuristic(goalPos, boxPos) == 0:
                        continue

                    for agentKey in agentKeys:
                        agentPos = state.getAgentsByKey(agentKey)[0][0]
                        agtBoxCosts.append(default_heuristic(agentPos, boxPos))

                    boxGoalCosts.append(default_heuristic(boxPos, goalPos))

                if len(boxGoalCosts) > 0:
                    boxGoalCost += min(boxGoalCosts)
            if len(agtBoxCosts) > 0:
                agtBoxCost += sum(agtBoxCosts)
                # Min doesn't work with SAFirefly
                # agtBoxCost += min(agtBoxCosts)
                #print(boxGoalCost, sum(boxGoalCosts), file=sys.stderr, flush=True)



        #print(agtBoxCost, boxGoalCost, file=sys.stderr, flush=True)
        state.h = boxGoalCost + agtBoxCost
        state.f = state.h + state.g
