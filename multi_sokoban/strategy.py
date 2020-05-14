"""Astar search."""
from abc import ABC, abstractmethod
from queue import PriorityQueue
from typing import Callable

from heuristics import EasyRule
from multi_sokoban import actions

from utils import println


class BestFirstSearch(ABC):
    """Abstract class for BFS."""

    def __init__(self, init_state: actions.StateInit, heuristic: Callable = None):
        """Initialize strategy."""
        self.frontier = PriorityQueue()
        self.leaf = init_state
        self.count = 0
        self.heuristic = heuristic if heuristic else EasyRule()

    def get_and_remove_leaf(self):
        """Depend on the heuristic method."""
        self.leaf = self.frontier.get()[2]

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
        self.heuristic(explored_states)

        for state in explored_states:
            self.count += 1
            self.frontier.put((state.h, self.count, state))

    def __str__(self):
        """Printable description."""
        return "greedy Best First Search"


class aStarSearch(BestFirstSearch):
    """BFS with A*."""

    def explore_and_add(self):
        """Apply the heuristic and update the frontier."""
        explored_states = self.leaf.explore()
        self.heuristic(explored_states)
        #println(" ")
        for state in explored_states:
            self.count += 1
            #println(self.count, state.f, state.h, state.g)
            self.frontier.put((state.f, self.count, state))

    def __str__(self):
        """Printable description."""
        return "A* Best First Search"
