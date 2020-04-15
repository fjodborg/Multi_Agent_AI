"""Astart priority queue."""
import heapq
from multi_sokoban import actions


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    # this priority queue returns the lowest value first by using heapq.

    # this priority queue returns the lowest value first by using heapq.
    def get(self):
        return heapq.heappop(self.elements)[1]

    # heuristic function that tells us how close we are to the goal, by calculating the cost.
    def heuristic(self, a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    # The A* algorithm uses the actual distance from the start (costThisfar) and the estimated distance to the goal (spaceSearchCost).


def aStarSearch(startState):
    count = 0  # creating an id for every child

    frontier = PriorityQueue()

    startPos = actions.StateInit()
    # The A* algorithm uses the actual distance from the start (costThisfar) and the estimated distance to the goal (spaceSearchCost).
    def aStarSearch(self, searchSpace, start, goal):
        count = 0  # creating an id for every child
        frontier = PriorityQueue()
        frontier.put(start, 0, count)
        cameFrom = {}  # cameFrom keeps track of visited nodes.
        costThisFar = {}
        cameFrom[start] = None
        costThisFar[start] = 0

    frontier.put(startPos, getBestState(startState), count)

    #     cameFrom = {} # cameFrom keeps track of visited nodes.
    #     costThisFar = {}
    #     cameFrom[start] = None
    #     costThisFar[start] = 0

    #    frontier = initialState #(Given by function call)
    # while/for loop:
    #   leaf = getBestState(frontier)
    #   if leaf.IsGoalState():
    #      return leaf.bestPath()
    #   explored_states = leaf.explore()
    #   frontier.add(explored_states)
    # getBestState(frontier)
    #   for all elements in frontier:
    #      pos of box - pos of goals
    #   return shortest distance

    while not frontier.empty():
        count += 1
        leaf = getBestState(frontier)

        # current = frontier.get()

        # Loop ends if goal is found.
        if leaf.isGoalState():
            return leaf.bestPath()

        explored_states = leaf.explore()
        frontier.put(explored_states)

    #         for elements in frontier:
    #
    #            # newCost = costThisFar[current] + searchSpace.cost(current, next)
    #
    #             if elements not in costThisFar or newCost < costThisFar[next]:
    #                 costThisFar[next] = newCost
    #                 newCost + heuristics(goal, next) #priority = actions.explore() #
    #                 frontier.put(next, priority)
    #                 cameFrom[next] = current

    return


def getBestState(frontier):
    i = -1
    hMap = {}
    for element in frontier:
        i += 1
        if element.h is None:
            continue

        keys = element.getGoals()
        for key in keys:
            goalPositions = element.getGoalsByKey(key)
            boxParams = element.getBoxesByKey(key)

            for goalPos in goalPositions:
                for boxPos, _ in boxParams:

                    boxPos = element.getAgentByKey(key)
                    goalPos = frontier.getBoxByKey(key)
                    # storing the distances between boxes and goals for every state
                    hMap[i] = heuristic(boxPos, goalPos)
        # Returns the shortest distance by sorting the smallest value by key
        element.h = min(hMap, k=hMap.get())
        return element.h


#         while not frontier.empty():
#             current = frontier.get()
#
#             # Look ends if goal is found.
#             if current == goal:
#                 break
