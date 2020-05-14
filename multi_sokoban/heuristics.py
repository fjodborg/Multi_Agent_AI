"""Heuristics for Best First Search."""
from abc import ABC, abstractmethod
from typing import List
import numpy as np
import pyvisgraph as vg
from utils import println
import networkx as nx

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
        explored = set()

        # add boundry wall
        rows, cols = map.shape
        for col in range(0, cols):
            explored.add(tuple([0, col]))
            explored.add(tuple([rows - 1, col]))
        for row in range(0, rows):
            explored.add(tuple([row, 0]))
            #explored.add(tuple(np.array([row, cols - 1])))

        # find contours
        cornerSets = []
        println(explored)
        for col in range(1, cols):
            for row in range(1, rows):
                pos = np.array([row, col])
                if map[row, col] == "+":
                    freePos = np.array([row, col - 1])
                    #println(freePos, tuple(freePos) in explored)
                    if map[row, col - 1] != "+" and tuple(pos) not in explored:
                        #println("first spot", freePos)
                        corners = self.findEdges(freePos, map, explored)
                        if corners:
                            cornerSets.append(corners)

        G = self.generateGraph(cornerSets, map)

        return G

    def draw(self, G):
        import matplotlib.pyplot as plt
        elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > 0.5]
        esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.5]
        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, node_size=700)
        nx.draw_networkx_edges(G, pos, edgelist=elarge, width=6)
        nx.draw_networkx_edges(G, pos, edgelist=esmall, width=6, alpha=0.5, edge_color='b', style='dashed')

        nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')
        
        plt.show()

    def generateGraph(self, cornerSets, map):
        # TODO remove this smal section below, it's just for the lols
        for corners in cornerSets:
            println("corner set", corners)
            if type(corners) != list:
                corners = [corners]
            for corner in corners:
                #println("corner", corner)
                map[corner] = "O"
        println(map)


        # TODO fix order of corners
        cornerSets[0] = cornerSets[0][-1::] + cornerSets[0][:-1:] 
        println(cornerSets)
        
        #G = nx.DiGraph()


        G = nx.DiGraph()
        
        for corners in cornerSets:
            for i in range(len(corners) - 1):
                if not np.array_equal(corners[i], corners[i + 1]):
                    corner1 = corners[i]
                    corner2 = corners[i+1]
                    dist = manha_dist((corner1[0], corner1[1]), (corner2[0], corner2[0]))
                    println(corner1, corner2, dist)
                    G.add_edge(corner1, corner2, weight=dist)
                    G.add_edge(corner2, corner1, weight=dist)
                    pass

        #self.draw(G)
        
        return G

        # uniqueCorners = set()
        # for corners in cornerSets:
        #     if type(corners) != list:
        #         uniqueCorners.add(corners)
        #         continue
        #     for corner in corners:
        #         uniqueCorners.add(corner)

        # done = False 
        # while not done:
        #     for corners in uniqueCorners:
        #         pass
        # println(uniqueCorners)


    def checkAndAddCorner(self, map, corners, cornerPos):
        if map[tuple(cornerPos)] == "+":
            return False
        corners.append(tuple(cornerPos))
        return True

    def addCorner(self, map, newPos, pos, dir, prevDir, explored, corners): 
        if map[tuple(newPos)] != "+" and tuple(newPos) not in explored:
            #tempExplored.add(tuple(newPos))
            cornerType = dir - prevDir
            if cornerType == -1:
                #println(pos, cornerType)
                self.checkAndAddCorner(map, corners, pos)
            
            #println("moving here:", (newPos, prevDir, dir))
            return True
        elif map[tuple(newPos)] == "+":
            #println("wall added", tuple(newPos))
            explored.add(tuple(newPos))
        return False

    def findEdges(self, initPos, map, explored):
        dir = -1
        prevDir = dir + 1
        pos = initPos
        corners = []     
        initDir = -999
        newPos = None
        isDone = False
        while not isDone:
            for j in range(0, 4):
                dir = (dir + 1)
                newPos = pos + self.dirs[dir]
                if self.addCorner(map, newPos, pos, dir, prevDir, explored, corners):
                    prevDir = dir % 4  # 4 directions
                    if np.array_equal(initPos, pos) and prevDir == initDir:
                        isDone = True
                    pos = newPos
                    if initDir == -999:
                        initDir = prevDir
                    break
            dir = (prevDir - 2) 
        
        return corners

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
        raise Exception("Nope")
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
