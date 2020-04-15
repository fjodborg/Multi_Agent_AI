from queue import PriorityQueue
from multi_sokoban import actions

count = 0


def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def aStarSearch(initState):
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
                for boxPos, color in boxParams:
                    # boxPos = state.getAgentByKey(key)
                    # goalPos = state.getBoxesByKey(key)
                    totalCost += heuristic(boxPos, goalPos)
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


test(0)
