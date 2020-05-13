"""Heuristics for Best First Search."""
from abc import ABC, abstractmethod
from typing import List
import numpy as np
import pyvisgraph as vg
from utils import println

def manha_dist(a, b):
    """Measure Manhattan distance."""
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


class Heuristics(ABC):
    """Class for defining heuristics."""

    @abstractmethod
    def __call__(self, states: List):
        """Call method, compute `heuristics` of List `states`."""
        return


class EasyRule(Heuristics):
    """Simple heuristics.

    Computes Manhattan distance for:
    * Boxes to goals.
    * Agents to boxes.
    """

    def __call__(self, states: List):
        """Calculate heuristic for states in place."""
        if type(states) is not list:
            states = [states]
        if len(states) == 0:
            return None

        for state in states:
            box_goal_cost = 0
            agt_box_cost = 0
            agt_box_costs = []
            for key in state.getGoalKeys():
                goal_params = state.getGoalsByKey(key)
                box_params = state.getBoxesByKey(key)
                # maybe add some temporary costs here for each key

                # find every position of goals and boxes with the given key
                for goal_pos, goal_color in goal_params:
                    box_goal_costs = []
                    for box_pos, _ in box_params:
                        # only take agents with the same color as goalColor
                        agent_keys = state.getAgentsByColor(goal_color)

                        if manha_dist(goal_pos, box_pos) == 0:
                            continue

                        for agent_key in agent_keys:
                            agentPos = state.getAgentsByKey(agent_key)[0][0]
                            agt_box_costs.append(manha_dist(agentPos, box_pos))

                        box_goal_costs.append(manha_dist(box_pos, goal_pos))

                    if len(box_goal_costs) > 0:
                        box_goal_cost += min(box_goal_costs)
                if len(agt_box_costs) > 0:
                    agt_box_cost += sum(agt_box_costs)

            state.h = box_goal_cost + agt_box_cost
            state.f = state.h * 5 + state.g


class WeightedRule(Heuristics):
    """Weighted heuristics.

    The distance from a box to a box is weigthed more (used for communication).
    Computes Manhattan distance for:
    * Boxes to goals.
    * Agents to boxes.
    """

    def __init__(self, weight: str):
        """Initialize object with state and `string` of box to weight more."""
        self.weight = weight

    def __call__(self, states: List):
        """Calculate heuristic for states in place."""
        if type(states) is not list:
            states = [states]
        if len(states) == 0:
            return None

        for state in states:
            box_goal_cost = 0
            agt_box_cost = 0
            agt_box_costs = []
            for key in state.getGoalKeys():
                goal_params = state.getGoalsByKey(key)
                box_params = state.getBoxesByKey(key)
                # maybe add some temporary costs here for each key

                # find every position of goals and boxes with the given key
                for goal_pos, goal_color in goal_params:
                    box_goal_costs = []
                    for box_pos, _ in box_params:
                        # only take agents with the same color as goalColor
                        agent_keys = state.getAgentsByColor(goal_color)

                        if manha_dist(goal_pos, box_pos) == 0:
                            continue

                        for agent_key in agent_keys:
                            agentPos = state.getAgentsByKey(agent_key)[0][0]
                            agt_box_costs.append(manha_dist(agentPos, box_pos))

                        box_goal_costs.append(manha_dist(box_pos, goal_pos))

                    if len(box_goal_costs) > 0:
                        box_cost = min(box_goal_costs)
                        if key.lower() == self.weight:
                            box_cost *= 10
                        box_goal_cost += box_cost
                if len(agt_box_costs) > 0:
                    agt_box_cost += sum(agt_box_costs)

            state.h = box_goal_cost + agt_box_cost
            state.f = state.h * 5 + state.g


class L1Clarkson(Heuristics):
    """L1 path finding heuristics.

    Outside corners are calculated and a visual graph is built where the edges
    are the manhattan distance from visual corner to visual corner.

    The algorithm computes the distance to the object to the min visual corner
    and then use the distances in the graph to calculate the heuristic.

    Reference
    ---------
    https://dl.acm.org/doi/10.1145/41958.41985
    """

    def __init__(self, state: np.array, weight: int = 1):
        """Initialize object by building the VIS(V,E) graph."""
        self.graph = self.build_graph(state.map)
        self.weight = weight

    def build_graph(self, map: np.array) -> List:
        """Build VIS graph."""
        rows, cols = map.shape
        polys = []
        for row in range(1, rows):
            lining = False
            for col in range(1, cols-1):
                if map[row, col] == "+" and not lining:
                    lining = True
                    left = vg.Point(row+1, col+1)
                elif map[row, col] == " " and lining:
                    lining = False
                    polys.append([left, vg.Point(row, col-2)])
                elif map[row, col] == "+" and col == cols-2 and lining:
                    lining = False
                    polys.append([left, vg.Point(row+1, col+1)])
        g = vg.VisGraph()
        g.build(polys)
        return g

    def distance(self, pos1: List, pos2: List) -> List:
        """Distance from vertice to vertice."""
        dist = 0
        path = self.graph.shortest_path(vg.Point(*pos1), vg.Point(*pos2))
        for p in range(1, len(path)):
            this = path[p]
            prev = path[p-1]
            dist += manha_dist((this.x, this.y), (prev.x, prev.y))
        return dist

    def __call__(self, states: List):
        """Calculate heuristic for states in place."""
        if type(states) is not list:
            states = [states]
        if len(states) == 0:
            return None

        for state in states:
            box_goal_cost = 0
            agt_box_cost = 0
            agt_box_costs = []
            for key in state.getGoalKeys():
                goal_params = state.getGoalsByKey(key)
                box_params = state.getBoxesByKey(key)
                # maybe add some temporary costs here for each key

                # find every position of goals and boxes with the given key
                for goal_pos, goal_color in goal_params:
                    box_goal_costs = []
                    for box_pos, _ in box_params:
                        # only take agents with the same color as goalColor
                        agent_keys = state.getAgentsByColor(goal_color)

                        if manha_dist(goal_pos, box_pos) == 0:
                            continue

                        for agent_key in agent_keys:
                            agentPos = state.getAgentsByKey(agent_key)[0][0]
                            agt_box_costs.append(self.distance(agentPos, box_pos))

                        box_goal_costs.append(self.distance(box_pos, goal_pos))

                    if len(box_goal_costs) > 0:
                        box_cost = min(box_goal_costs)
                        if key.lower() == self.weight:
                            box_cost *= 10
                        box_goal_cost += box_cost
                if len(agt_box_costs) > 0:
                    agt_box_cost += sum(agt_box_costs)

            state.h = box_goal_cost + agt_box_cost
            state.f = state.h * 5 + state.g


class dGraph(Heuristics):
    def __init__(self, state: np.array, weight: int = 1):
        """Initialize object by building the VIS(V,E) graph."""
        self.dirs = [np.array([0, 1]), np.array([1, 0]), np.array([0, -1]), np.array([-1, 0]), np.array([0, 1]), np.array([1, 0]), np.array([0, -1]), np.array([-1, 0])]
        self.weight = weight
        self.graph = self.build_graph(state.map)
        #self.dir = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}


    def build_graph(self, map: np.array) -> List:
        exploredWalls = set()

        # add boundry wall
        rows, cols = map.shape
        for col in range(0, cols):
            exploredWalls.add(str([0, col]))
            exploredWalls.add(str([rows - 1, col]))
        for row in range(0, rows):
            exploredWalls.add(str([row, 0]))
            exploredWalls.add(str([row, cols - 1]))

        # find contours
        for row in range(1, rows - 1):
            for col in range(1, cols - 1):
                pos = np.asarray([row, col])
                if map[row, col] == "+" and str(pos) not in exploredWalls:
                    self.findEdges(pos, map, exploredWalls)
        
        import sys;sys.exit()

        return g

 
    def findEdges(self, initPos, map, exploredWalls):
        # TODO look if the wall goes out of the real walls
        # for self.dir[0]

        dir = -1
        prevDir = dir + 1

        pos = initPos
        newPos = np.array([-1, -1])

        corners = []

        while not np.array_equal(initPos, newPos):
            #println("new iteration")
            
            for j in range(0, 4):
                dir = (dir + 1)
                #println(pos, dir)
                #println(self.dirs[dir])
                newPos = pos + self.dirs[dir]
                if map[tuple(newPos)] == "+":
                    exploredWalls.add(str(newPos))
                    cornerType = dir - prevDir
                    if cornerType == 2:
                        println("here wo go2")
                        corners.append(pos + self.dirs[dir - 2] + self.dirs[prevDir - 1])
                        corners.append(pos + self.dirs[dir - 1] + self.dirs[prevDir - 0])
                    elif cornerType == 1:
                        corners.append(pos + self.dirs[dir - 1] + self.dirs[prevDir - 1])
                        println("here wo go1")
                    println("wall here:", (newPos, prevDir, dir, not np.array_equal(initPos, newPos)))
                    prevDir = dir % 4  # 4 directions
                    pos = newPos
                    break
            dir = (prevDir - 2) 

        println(corners)

    def distance(self, pos1: List, pos2: List) -> List:
        """Distance from vertice to vertice."""
        dist = 0
        path = self.graph.shortest_path(vg.Point(*pos1), vg.Point(*pos2))
        for p in range(1, len(path)):
            this = path[p]
            prev = path[p-1]
            dist += manha_dist((this.x, this.y), (prev.x, prev.y))
        return dist

    def __call__(self, states: List):
        """Calculate heuristic for states in place."""
        if type(states) is not list:
            states = [states]
        if len(states) == 0:
            return None

        for state in states:
            box_goal_cost = 0
            agt_box_cost = 0
            agt_box_costs = []
            for key in state.getGoalKeys():
                goal_params = state.getGoalsByKey(key)
                box_params = state.getBoxesByKey(key)
                # maybe add some temporary costs here for each key

                # find every position of goals and boxes with the given key
                for goal_pos, goal_color in goal_params:
                    box_goal_costs = []
                    for box_pos, _ in box_params:
                        # only take agents with the same color as goalColor
                        agent_keys = state.getAgentsByColor(goal_color)

                        if manha_dist(goal_pos, box_pos) == 0:
                            continue

                        for agent_key in agent_keys:
                            agentPos = state.getAgentsByKey(agent_key)[0][0]
                            agt_box_costs.append(self.distance(agentPos, box_pos))

                        box_goal_costs.append(self.distance(box_pos, goal_pos))

                    if len(box_goal_costs) > 0:
                        box_cost = min(box_goal_costs)
                        if key.lower() == self.weight:
                            box_cost *= 10
                        box_goal_cost += box_cost
                if len(agt_box_costs) > 0:
                    agt_box_cost += sum(agt_box_costs)

            state.h = box_goal_cost + agt_box_cost
            state.f = state.h * 5 + state.g
