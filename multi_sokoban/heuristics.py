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
                            agt_box_costs.append(-10 * manha_dist(agentPos, box_pos))

                        box_goal_costs.append(manha_dist(box_pos, goal_pos))

                        box_goal_cost += min(box_goal_costs)
                if len(agt_box_costs) > 0:
                    agt_box_cost += sum(agt_box_costs)

            state.h = box_goal_cost + agt_box_cost
            state.f = state.h * 25


class dGraph(Heuristics):
    def __init__(self, state: np.array):
        """Initialize object by building the VIS(V,E) graph."""
        self.dirs = [
            np.array([0, 1]),
            np.array([1, 0]),
            np.array([0, -1]),
            np.array([-1, 0]),
            np.array([0, 1]),
            np.array([1, 0]),
            np.array([0, -1]),
            np.array([-1, 0]),
        ]
        # self.weight = weight
        self.cornerSet = []
        self.map = state.map
        self.uniqueCorners = set()
        self.poses = []
        self.graph = self.build_graph(state.map)
        self.boxes = {}

        # self.dir = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}

    def build_graph(self, map: np.array) -> List:
        explored = set()

        # add boundry wall
        rows, cols = map.shape
        for col in range(0, cols):
            explored.add(tuple([0, col]))
            explored.add(tuple([rows - 1, col]))
        for row in range(0, rows):
            explored.add(tuple([row, 0]))
            # explored.add(tuple(np.array([row, cols - 1])))

        # find contours
        self.cornerSets = []
        println(explored)
        for col in range(1, cols):
            for row in range(1, rows):
                pos = np.array([row, col])
                if map[row, col] == "+":
                    freePos = np.array([row, col - 1])
                    # println(freePos, tuple(freePos) in explored)
                    if map[row, col - 1] != "+" and tuple(pos) not in explored:
                        # println("first spot", freePos)
                        corners = self.findEdges(freePos, map, explored)
                        if corners:
                            self.cornerSets.append(corners)

        G = self.generateGraph(copy.copy(map))

        return G

    def draw(self, G):
        import matplotlib.pyplot as plt

        elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0.5]
        esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0.5]
        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, node_size=700)
        nx.draw_networkx_edges(G, pos, edgelist=elarge, width=6)
        nx.draw_networkx_edges(
            G, pos, edgelist=esmall, width=6, alpha=0.5, edge_color="b", style="dashed"
        )

        nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")

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
        # cornerSets[0] = cornerSets[0][-1::] + cornerSets[0][:-1:]

        G = nx.DiGraph()

        println(cornerSets)

        for corners in cornerSets:
            # First position is always at the end
            for i in range(len(corners)):
                # println(corners[i - 1], corners[i])
                if not np.array_equal(corners[i - 1], corners[i]):
                    if self.getValidKeypoint(map, corners[i - 1], corners[i], []):

                        corner1 = corners[i - 1]
                        corner2 = corners[i]
                        dist = manha_dist(
                            (corner1[0], corner1[1]), (corner2[0], corner2[1])
                        )
                        println(corner1, corner2, dist)
                        G.add_edge(corner1, corner2, weight=dist)
                        G.add_edge(corner2, corner1, weight=dist)

        if len(cornerSets) > 1:
            raise Exception("####### No edge fusion implemented yet")

        println(cornerSets)
        # self.draw(G)

        # import sys; sys.exit()

        # for corners in cornerSets:
        #     for i in range(len(corners) - 1):
        #         if not np.array_equal(corners[i], corners[i + 1]):
        #             corner1 = corners[i]
        #             corner2 = corners[i + 1]
        #             dist = manha_dist(
        #                 (corner1[0], corner1[1]), (corner2[0], corner2[1])
        #             )
        #             println(corner1, corner2, dist)
        #             G.add_edge(corner1, corner2, weight=dist)
        #             G.add_edge(corner2, corner1, weight=dist)
        #             pass

        return G

    def checkAndAddCorner(self, map, corners, cornerPos):
        if map[tuple(cornerPos)] == "+":
            return False
        corners.append(tuple(cornerPos))
        return True

    def addCorner(self, map, newPos, pos, dir, prevDir, explored, corners):
        if map[tuple(newPos)] != "+" and tuple(newPos) not in explored:
            # tempExplored.add(tuple(newPos))
            cornerType = dir - prevDir
            if cornerType == -1:
                # println(pos, cornerType)
                self.checkAndAddCorner(map, corners, pos)

            # println("moving here:", (newPos, prevDir, dir))
            return True
        elif map[tuple(newPos)] == "+":
            # println("wall added", tuple(newPos))
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
                dir = dir + 1
                newPos = pos + self.dirs[dir]
                if self.addCorner(map, newPos, pos, dir, prevDir, explored, corners):
                    prevDir = dir % 4  # 4 directions
                    if np.array_equal(initPos, pos) and prevDir == initDir:
                        isDone = True
                    pos = newPos
                    if initDir == -999:
                        initDir = prevDir
                    break
            dir = prevDir - 2

        return corners

    def getValidKeypoint(self, map, pos, kp, validKps):

        tempPos = np.array(pos)
        # println("keypoint:", kp, pos)
        diff = np.array(tempPos) - kp
        dir = [0, 0]
        if diff[0] < 0:
            dir[0] = 1
        else:
            dir[0] = -1

        while tempPos[0] != kp[0]:
            tempPos[0] += dir[0]
            # print(tempPos)
            if map[tuple(tempPos)] == "+" or tuple(tempPos) in validKps:
                return False

        if diff[1] < 0:
            dir[1] = 1
        else:
            dir[1] = -1

        while tempPos[1] != kp[1]:
            tempPos[1] += dir[1]
            # println(tempPos)
            if map[tuple(tempPos)] == "+" or tuple(tempPos) in validKps:
                return False

        # TODO, if it passes a corner point skip to next

        # println("best keypoint for pos", pos,"is:", kp)
        validKps.append(tuple(kp))
        return True
        # return kp

    def findBestKeyPoint(self, pos, pos2):
        # TODO optimize this!
        # By nature of how the corners are generated the nearst point, if reachable
        # will always be reachable from all directions minimizing the distance
        # between the pos and keypoint
        map = self.map
        corners = np.asarray(self.uniqueCorners)
        # println(list([np.linalg.norm(pos - kp, 1), kp] for kp in corners))
        sortedKp = sorted(corners, key=lambda kp: np.linalg.norm(pos - kp, 1))
        # println(pos)
        validKps = []
        for kp in sortedKp:

            self.getValidKeypoint(map, pos, kp, validKps)
            if len(validKps) >= 4:
                break

        # println(validKps)
        if np.linalg.norm(np.asarray(validKps[0]) - np.asarray(pos)) >= np.linalg.norm(
            np.asarray(pos) - np.asarray(pos2)
        ):
            self.getValidKeypoint(map, pos, pos2, validKps)
        # println(validKps)

        return list(validKps)  # sort by age

        # return sorted(corners, key=lambda p: p)

    def findPathPart(self, state, pathId, combId):
        # (State, pathIndex)
        # TODO when calculating new dijkstras maybe just look at the changing parts
        # TODO make it work for more boxes and goals
        # TODO test performace difference between deepcopy and copy

        # TODO TODO TODO only recalculate new parts of the shorest path. e.g.
        # calculate the distance from pos to Kp, and then simply calculate the distance from
        # Kp to Kp and add them together
        # maybe precalculate every keypoint?

        GTemp = copy.deepcopy(self.graph)
        # println(self.poses, self.poses[combId][pathId])
        startPos, endPos = self.poses[combId][pathId]
        currentPath = state.currentPath[combId][pathId]
        prevKeypoints = state.prevKeypoints[combId][pathId]
        #  println(" start", startPos,endPos, state.currentPath, startId, endId)
        if (
            currentPath is not None
        ):  # and #TODO find if inbetween two points! #G.has_node(state.currentPath[0]):
            # TODO don't re calculate the path
            # TODO do the same at the endPoint
            startKps, endKps = prevKeypoints
            # println(endKps, startKps)
            # println(state.currentPath)
            # println(startKp, boxKp, goalKp)
            # println(state.currentPath.index(startKp), boxKp, goalKp)

            if len(currentPath) > 2 and currentPath[1] == startPos:
                startKps = [currentPath[1], currentPath[2]]
            if len(currentPath) == 2:
                # println(endPos, startKps)
                startKps.append(endPos)

            # dist = manha_dist(startPos, state.currentPath[0])
            # GTemp.add_edge(startPos, state.currentPath[0], weight=dist)
            # dist = manha_dist(startPos, state.currentPath[1])
            # GTemp.add_edge(startPos, state.currentPath[1], weight=dist)

            for kp in startKps:
                dist = manha_dist(startPos, kp)
                GTemp.add_edge(startPos, kp, weight=dist)
            # GTemp.add_edge(startKp, startPos, weight=dist)
            # println(startKp, startPos)

            for kp in endKps:
                dist = manha_dist(endPos, kp)
                GTemp.add_edge(kp, endPos, weight=dist)

            # TODO do some magic for endPos
            # println("is neighbor", startPos, startKp, endPos, boxKp, goalPos, goalKp)
            println("if", startPos, startKps, endPos, endKps)
            self.draw(GTemp)
            length, newPath = nx.bidirectional_dijkstra(GTemp, startPos, endPos)

            # println(lengthBox, pathBox[1::], lengthGoal, pathGoal[2::])
            # println(startKp, startPos, boxKp, endPos, goalKp, goalPos)
            prevKeypoints = [startKps, endKps]

            # println(lengthBox,lengthGoal, pathBox, pathGoal)
        else:

            # println(startPos, endPos)
            startKps = self.findBestKeyPoint(startPos, endPos)
            endKps = self.findBestKeyPoint(endPos, startPos)
            # println(startKps, endKps)
            prevKeypoints = [startKps, endKps]
            # println(state.prevKeypoints, endKps)

            for kp in startKps:
                dist = manha_dist(startPos, kp)
                GTemp.add_edge(startPos, kp, weight=dist)

            for kp in endKps:
                dist = manha_dist(kp, endPos)
                GTemp.add_edge(kp, endPos, weight=dist)
            # GTemp.add_edge(endPos, endKp, weight=dist)

            # println("else", startPos, startKps, endPos, endKps)
            # self.draw(GTemp)
            length, newPath = nx.bidirectional_dijkstra(GTemp, startPos, endPos)

        del GTemp
        currentPath = newPath
        return length  # path[1:-1]

    def initializeGraphAttributes(self, state, subGoal, i):
        self.poses[i] = subGoal
        if state.currentPath[i] is None:
            state.currentPath[i] = [None] * len(subGoal)
            state.prevKeypoints[i] = [None] * len(subGoal)

    def initializeGraphSizes(self, state, size):
        self.poses = [None] * size
        state.currentPath = [None] * size
        state.prevKeypoints = [None] * size

    def __call__(self, states: List):
        """Calculate heuristic for states in place."""
        if type(states) is not list:
            states = [states]
        if len(states) == 0:
            return None

        length = None
        for state in states:
            # Subproblems just have one agent
            agt_pos, color = list(state.agents.values())[0][0]
            length_boxes = 0
            length_goals = 0
            for goal, vals in state.goals.items():
                for v in vals:
                    goal_pos, goal_color = v

                    if color != goal_color:
                        continue

                    box_poses = [
                        p_c[0][0]
                        for box, p_c in state.boxes.items()
                        if box.lower() == goal.lower()
                    ]
                    if any(goal_pos == box_pos for box_pos in box_poses):
                        continue

                    # (State, partsToSolve)
                    this_boxes = []
                    this_goals = []

                    self.initializeGraphSizes(state, len(box_poses))

                    for i, box_pos in enumerate(box_poses):
                        if (goal, box_pos, agt_pos) in self.boxes:
                            this_goal = self.boxes[(goal, box_pos, agt_pos)]
                            h_box = this_goal[0]
                            h_goal = this_goal[1]
                        else:
                            self.initializeGraphAttributes(
                                state, [[agt_pos, box_pos], [box_pos, goal_pos]], i
                            )
                            h_box = self.findPathPart(state, 0, i)
                            h_goal = self.findPathPart(state, 1, i)
                            self.boxes[(goal, box_pos, agt_pos)] = h_box, h_goal

                        # (State, partIndex)
                        this_boxes.append(h_box)
                        this_goals.append(h_goal)
                    length_boxes += min(this_boxes)
                    length_goals += sum(this_goals)

            length = length_boxes + length_goals
            state.h = length
            state.f = state.h * 1.1 + state.g
            # println(state, state.h, state.g, state.f)
