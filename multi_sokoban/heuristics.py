"""Heuristics for Best First Search."""
from abc import ABC, abstractmethod
from typing import List
import numpy as np
import networkx as nx
from utils import println
import copy


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
                        if goal_color in state.agentColor:
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


class GoAway(Heuristics):
    """GoAway heuristics.

    The distance from a box to a box is weigthed more (used for communication).
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
                        agent_keys = state.agents.keys()

                        if manha_dist(goal_pos, box_pos) == 0:
                            continue

                        for agent_key in agent_keys:
                            agentPos = state.getAgentsByKey(agent_key)[0][0]
                            agt_box_costs.append(-10*manha_dist(agentPos, box_pos))

                        box_goal_costs.append(manha_dist(box_pos, goal_pos))

                        box_goal_cost += min(box_goal_costs)
                if len(agt_box_costs) > 0:
                    agt_box_cost += sum(agt_box_costs)

            state.h = box_goal_cost + agt_box_cost
            state.f = state.h * 25


class dGraph(Heuristics):
    def __init__(self, state: np.array):
        """Initialize object by building the VIS(V,E) graph."""
        self.dirs = [np.array([0, 1]), np.array([1, 0]), np.array([0, -1]), np.array([-1, 0]), np.array([0, 1]), np.array([1, 0]), np.array([0, -1]), np.array([-1, 0])]
        #self.weight = weight
        self.cornerSet = []
        self.map = state.map
        self.uniqueCorners = set()
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
        self.cornerSets = []
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
                            self.cornerSets.append(corners)

        G = self.generateGraph(copy.copy(map))

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

    def generateGraph(self, map):
        cornerSets = self.cornerSets
        for corners in cornerSets:
            println("corner set", corners)
            if type(corners) != list:
                corners = [corners]
            for corner in corners:
                self.uniqueCorners.add(corner)
                map[corner] = "O"
        println(map)

        self.uniqueCorners = list(self.uniqueCorners)


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
                    dist = manha_dist((corner1[0], corner1[1]), (corner2[0], corner2[1]))
                    println(corner1, corner2, dist)
                    G.add_edge(corner1, corner2, weight=dist)
                    G.add_edge(corner2, corner1, weight=dist)
                    pass

        return G



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
        # TODO add a new corner here probably
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

    def closestValidNode(self, pos):
        # TODO optimize this!
        # By nature of how the corners are generated the nearst point, if reachable
        # will always be reachable from all directions minimizing the distance
        # between the pos and keypoint
        map = self.map
        corners = np.asarray(self.uniqueCorners)
        #println(list([np.linalg.norm(pos - kp, 1), kp] for kp in corners))
        sortedKp = sorted(corners, key=lambda kp: np.linalg.norm(pos - kp, 1))
        println(pos)
        

        for kp in sortedKp:
            validKp = True
            tempPos = copy.copy(pos)
            #println("keypoint:", kp, pos)
            diff = (tempPos - kp)
            dir = [0, 0]
            if diff[0] < 0: dir[0] = 1
            else: dir[0] = -1

            while tempPos[0] != kp[0]:
                tempPos[0] += dir[0]
                if map[tuple(tempPos)] == "+":
                    validKp = False
                    println("wall detected")
                    break

            if diff[1] < 0: dir[1] = 1
            else: dir[1] = -1

            while tempPos[1] != kp[1]:
                tempPos[1] += dir[1]
                #println(tempPos)
                if map[tuple(tempPos)] == "+":
                    validKp = False
                    println("wall detected")
                    break
            
            if validKp:
                println("best keypoint for pos", pos,"is:", kp)
                break
        
        #import sys; sys.exit()
        return tuple(kp)  # sort by age
        
        #return sorted(corners, key=lambda p: p)

    def findBestKeyPoint(self, agtPos, boxPos, goalPos):
        # TODO make a hash of each position but only once?
        # TODO Check if is valid by go E to see if wall
        # if wall, go S until wall or Keypoint
        # if wall, go W until wall or Keypoint
        # if wall, go N until wall or Keypoint
        # if wall, go E and if same position as first, use other heuristic
        agtKp = self.closestValidNode(np.asarray(agtPos))
        boxKp = self.closestValidNode(np.asarray(boxPos))
        goalKp = self.closestValidNode(np.asarray(goalPos))
        #println(self.uniqueCorners, agtKp, boxKp, goalKp)

        # println(self.uniqueCorners)
        return agtKp, boxKp, goalKp  # tuple([3, 1]), None, tuple([1, 6])

    def findPaths(self, state, agtPos, boxPos, goalPos):
        # TODO when calculating new dijkstras maybe just look at the changing parts
        # TODO make it work for more boxes and goals
        # TODO test performace difference between deepcopy and copy
        GTemp = copy.deepcopy(self.graph)
        #println(agtPos,boxPos,goalPos, state.currentPath)
        if state.currentPath:  # and #TODO find if inbetween two points! #G.has_node(state.currentPath[0]):
            # TODO don't re calculate the path
            # TODO do the same at the endPoint
            agtKp, boxKp, goalKp = state.prevKeypoints

            println(state.currentPath)
            #println(agtKp, boxKp, goalKp)
            #println(state.currentPath.index(agtKp), boxKp, goalKp)

            if state.currentPath[0] == agtPos and len(state.currentPath) > 1:
                agtKp = state.currentPath[1]
            # dist = manha_dist(agtPos, state.currentPath[0])
            # GTemp.add_edge(agtPos, state.currentPath[0], weight=dist)
            # dist = manha_dist(agtPos, state.currentPath[1])
            # GTemp.add_edge(agtPos, state.currentPath[1], weight=dist)

            dist = manha_dist(agtPos, agtKp)
            GTemp.add_edge(agtPos, agtKp, weight=dist)
            GTemp.add_edge(agtKp, agtPos, weight=dist)
            #println(agtKp, agtPos)

            dist = manha_dist(boxPos, boxKp)
            GTemp.add_edge(boxPos, boxKp, weight=dist)
            GTemp.add_edge(boxKp, boxPos, weight=dist)

            if len(state.currentPath) > 1:
                dist = manha_dist(state.currentPath[-2], goalPos)
                GTemp.add_edge(state.currentPath[-2], goalPos, weight=dist)
            else:
                dist = manha_dist(state.currentPath[0], goalPos)
                GTemp.add_edge(state.currentPath[0], goalPos, weight=dist)
            # dist = manha_dist(agtPos, boxPos)
            # GTemp.add_edge(agtPos, boxPos, weight=dist)

            # TODO do some magic for endPos
            println("is neighbor", agtPos, agtKp, boxPos, boxKp, goalPos, goalKp)
            if abs(agtPos[0] - boxPos[0]) + abs(agtPos[1] - boxPos[1]) == 1:
                #println("is neighbor")
                lengthBox, pathBox = 0, []
                
                # TODO try and fix this
                boxKp = agtKp
                GTemp.add_edge(boxPos, boxKp, weight=dist)
            lengthBox, pathBox = nx.bidirectional_dijkstra(GTemp, agtPos, boxKp)
            lengthGoal, pathGoal = nx.bidirectional_dijkstra(GTemp, boxPos, goalPos)
            println(lengthBox, pathBox[1::], lengthGoal, pathGoal[2::])
            #self.draw(GTemp)
            #println(agtKp, agtPos, boxKp, boxPos, goalKp, goalPos)
            
            state.prevKeypoints = [agtKp, boxKp, goalKp]
            
            # println(lengthBox,lengthGoal, pathBox, pathGoal)
        else:
            
            #println(agtPos, endPos)
            agtKp, boxKp, goalKp = self.findBestKeyPoint(agtPos, boxPos, goalPos)
            state.prevKeypoints = [agtKp, boxKp, goalKp]

            dist = manha_dist(agtPos, agtKp)
            GTemp.add_edge(agtPos, agtKp, weight=dist)

            dist = manha_dist(goalKp, goalPos)
            GTemp.add_edge(goalKp, goalPos, weight=dist)

            dist = manha_dist(boxKp, boxPos)
            GTemp.add_edge(boxKp, boxPos, weight=dist)
            GTemp.add_edge(boxPos, boxKp, weight=dist)
            
            lengthBox, pathBox = nx.bidirectional_dijkstra(GTemp, agtPos, boxKp)
            lengthGoal, pathGoal = nx.bidirectional_dijkstra(GTemp, boxPos, goalPos)
        
        del GTemp
        return lengthBox, lengthGoal, pathBox[1::], pathGoal[2::]

    def __call__(self, states: List):
        """Calculate heuristic for states in place."""
        if type(states) is not list:
            states = [states]
        if len(states) == 0:
            return None


        length = None
        G = self.graph
        for state in states:
            agtPos = (list(state.agents.values())[0][0][0])
            boxPos = (list(state.boxes.values())[0][0][0])
            goalPos = (list(state.goals.values())[0][0][0])
            
            lengthBox, lengthGoal, pathBox, pathGoal = self.findPaths(state, agtPos, boxPos, goalPos)
            
            length = lengthBox + lengthGoal
            path = pathBox + pathGoal
            
            state.currentPath = path
            state.h = length
            state.f = state.h*2 + state.g
            #println(state, state.h, state.g, state.f)
            
            
            #println(state.h, state.f, state.g)

        # import sys; sys.exit()

        # for state in states:
        #     box_goal_cost = 0
        #     agt_box_cost = 0
        #     agt_box_costs = []
        #     for key in state.getGoalKeys():
        #         goal_params = state.getGoalsByKey(key)
        #         box_params = state.getBoxesByKey(key)
        #         # maybe add some temporary costs here for each key

        #         # find every position of goals and boxes with the given key
        #         for goal_pos, goal_color in goal_params:
        #             box_goal_costs = []
        #             for box_pos, _ in box_params:
        #                 # only take agents with the same color as goalColor
        #                 if goal_color in state.agentColor:
        #                     agent_keys = state.getAgentsByColor(goal_color)

        #                     if manha_dist(goal_pos, box_pos) == 0:
        #                         continue

        #                     for agent_key in agent_keys:
        #                         agentPos = state.getAgentsByKey(agent_key)[0][0]
        #                         agt_box_costs.append(manha_dist(agentPos, box_pos))

        #                 box_goal_costs.append(manha_dist(box_pos, goal_pos))

        #             if len(box_goal_costs) > 0:
        #                 box_goal_cost += min(box_goal_costs)
        #         if len(agt_box_costs) > 0:
        #             agt_box_cost += sum(agt_box_costs)

        #     state.h = box_goal_cost + agt_box_cost
        #     state.f = state.h * 5 + state.g
