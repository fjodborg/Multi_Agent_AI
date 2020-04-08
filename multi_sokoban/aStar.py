import collections
import heapq
from builtins import next

from pip._vendor.cachecontrol import heuristics

from _operator import ne


class Grid:
    def __init__(self, width, hight):
        self.width = width
        self.hight = hight
        self.walls = []

    def in_bounds(self, iD):
        (x, y) = iD
        return 0 <= x < self.width and 0 <= y < self.hight

    def passable(self, iD):
        return iD not in self.walls

    def neighbors(self, iD):
        (x, y) = iD
        results = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)]
        if (x + y) % 2 == 0:
            results.reverse()
            results = filter(self.in_bounds, results)
            results = filter(self.passable, results)
            return results


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

    def heuristic(self, a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    def aStarSearch(self, searchSpace, start, goal):
        count = 0  # creating an id for every child
        frontier = PriorityQueue()
        frontier.put(start, 0, count)
        cameFrom = {}
        costThisFar = {}
        cameFrom[start] = None
        costThisFar[start] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                break

            for next in searchSpace.neighbors(current):
                newCost = costThisFar[current] + searchSpace.cost(current, next)
                if next not in costThisFar or newCost < costThisFar[next]:
                    costThisFar[next] = newCost
                    priority = newCost + heuristics(goal, next)
                    frontier.put(next, priority)
                    cameFrom[next] = current

        return cameFrom, costThisFar
