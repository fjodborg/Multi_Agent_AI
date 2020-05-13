from .utils import println
import copy
import numpy as np


class Resultsharing:
    def __init__(self, manager, inbox):
        """Initialize with the whole problem definition `top_problem`."""
        self.pos = []
        self.paths = []
        self.manager = manager
        self.timeTable = {}
        self.offsetTable = {}
        self.traceback = 0
        self.unsolvableReason = [None]
        self.isNotBound = 0
        self.inbox = inbox
        self.visitedStates = set()
        self.collisionPoints = []

    def addToTimeTable(self, pos, time, identity):
        key = (pos)
        value = (identity, time)
        if key in self.timeTable:
            self.timeTable[key].append(value)
        else:
            self.timeTable[key] = [value]

    def generateTimeTable(self):
        for key in self.manager.top_problem.boxes:
            boxPos, boxColor = self.manager.top_problem.boxes[key][0]
            self.addToTimeTable(boxPos, 0, boxColor)

        for agtIdx in range(len(self.paths)):
            for time in range(len(self.pos[agtIdx])):
                posAtTime = self.pos[agtIdx][time]
                if len(posAtTime) > 1:
                    self.addToTimeTable(posAtTime[1], time, agtIdx)
                self.addToTimeTable(posAtTime[0], time, agtIdx)
        return None

    def fixLength(self):
        lengths = [len(self.pos[agt]) for agt in range(len(self.pos))]
        longest = max(lengths)
        shortest = min(lengths)
        if longest < shortest:
            return None

        for pos in self.pos:
            for i in range(longest - len(pos)):
                pos.append(pos[-1])
                pass

        for agt in range(len(self.pos)):
            for i in range(len(self.pos[agt]) - 1):
                if self.pos[agt][i] == self.pos[agt][i + 1]:
                    if len(self.paths[agt]) > 0:
                        self.paths[agt].insert(i, "NoOp")
                    else:
                        self.paths[agt].append("NoOp")

    def extractFromHash(self, hash, agt):
        '''Not in use at the moment'''
        params = hash
        #println(f"before {params}, {agt}")
        params = list(filter(lambda x: self.color2agt(x[0]) != agt, params))
        params = list(map(list, zip(*params)))
        #println(f"after {params}")
        if params:
            return params[0], params[1]
        return None

    def getOffsetTime(self, agt2, time):
        '''Not in use at the moment'''
        timeWithOffset = time
        if agt2 in self.offsetTable:
            for offsetTimes, offsetValues in self.offsetTable[agt2]:
                if offsetTimes <= time:
                    timeWithOffset += offsetValues

        return timeWithOffset

    def isSwap(self, agt1, agt2, time1, time2, pos1):
        if time1 + 1 < len(self.pos[agt1]):
            pos12 = self.pos[agt1][time1 + 1]
        else:
            pos12 = pos1

        if time2 + 1 < len(self.pos[agt2]):
            pos22 = self.pos[agt2][time2 + 1]
        else:
            pos22 = pos1

        if type(pos12) == list:
            pos12 = pos12[0]
        if type(pos22) == list:
            pos22 = pos22[0]

        dist1 = abs((pos1[0] - pos12[0]) + (pos1[0] - pos22[0]))
        dist2 = abs((pos1[1] - pos12[1]) + (pos1[1] - pos22[1]))
        #println((f"swap values is {dist1+dist2 <= 1}", dist1, dist2))
        if dist1 + dist2 <= 1:
            return True
        else:
            return False

    def fixPos(self):
        for agent in self.offsetTable.keys():
            for offsetTime, offsetValue in self.offsetTable[agent]:
                for i in range(offsetValue):
                    self.pos[agent].insert(offsetTime, self.pos[agent][offsetTime])
                    pass
                #println((offsetTime, offsetValue, self.pos[agent][offsetTime]))

    def findCollisionsNew(self, agt1, agentsOrder, pos1, time1, traceback=0):
        limit = 2


        potentialCollisions = []
        for agt2 in reversed(agentsOrder):
            poses2 = self.pos[agt2]
            time2 = time1 - traceback - 1

            for time2New in range(time2, time2 + limit + 1):
                artificialFix = False
                if time2New < 0:
                    time2New = 0
                if time2New >= len(poses2):
                    artificialFix = True
                    time2New = len(poses2) - 1
                if len(poses2) <= time2New or time2New < 0:
                    println("time2 out of bounds", time2New)
                    break
                for pos2 in poses2[time2New]:
                    #println(f"collision occured {agt1, agt2, pos1, pos2, time1, time2New}")
                    if pos2 == pos1:
                        isSwap = self.isSwap(agt1, agt2, time1, time2New, pos1)
                        potentialCollisions.append((isSwap, agt2, time2New, artificialFix))
                        println(f"collision occured {agt1, agt2, pos1, pos2, time1, time2New}")
        return potentialCollisions

    def solveAgt1(self, agt1, agentOrder, pos1, time1, collisionData):
        if collisionData:
            agt2 = collisionData[0][1]
            #println(collisionData)
            if not collisionData[0][3]:
                if collisionData[0][0]:
                    self.pos[agt2].insert(0, self.pos[agt2][0])
                else:
                    self.pos[agt2].insert(0, self.pos[agt2][0])
                return True
        return False

    def isStillCollided(self, agt1):
        otherAgents = []
        for agt2 in range(len(self.pos)):
            #println(agt2)
            if agt2 != agt1:
                otherAgents.append(agt2)
        for time1, poses1 in enumerate(self.pos[agt1]):
            for pos1 in poses1:
                collisionData = self.findCollisionsNew(agt1, otherAgents, pos1, time1)
                if collisionData:
                    println(f"####################{collisionData}, {time1}, {otherAgents}")
                    println(f"$$$$$$$$$$$$$$$$$$$#{agt1}, {collisionData[0][1]}")
                    return (agt1, collisionData[0][1])
        return False

    def findAndSolveAgt1(self, agt1, agentOrder):
        otherAgents = copy.deepcopy(agentOrder)
        otherAgents.remove(agt1)
        time1 = 0
        while time1 < len(self.pos[agt1]):
            poses1 = self.pos[agt1][time1]
            #println(time1, agt1, otherAgents)
            for pos1 in poses1:
                collisionData = self.findCollisionsNew(agt1, otherAgents, pos1, time1)
                collision = self.solveAgt1(agt1, otherAgents, pos1, time1, collisionData)
                if collision:
                    time1 -= 1
                #try:
                #isHandled = self.handleCollisionData(collisionData, agt1, agentOrder, time1)
                # except Exception:
                #     println(f"something went wrong {self.collisionPoints}")
                #     return None
                # if isHandled:
                #     agentOrder.remove(agt1)
                #     println(agentOrder)
                #     break
            time1 += 1

        collidedAgents = self.isStillCollided(agt1)
        return collidedAgents

    def findAndResolveCollision(self):
        sorted_agents = self.manager.sort_agents()
        self.paths = self.manager.solutions
        println(self.manager.solutions)

        initpos = [[[self.manager.agents[agent].init_pos]] for agent in sorted_agents]
        self.pos = convert2pos(self.manager, initpos, self.paths)

        println(self.pos)

        self.generateTimeTable()
        println(self.timeTable)
        self.unsolvableReason = None

        agentOrder = self.prioritiedAgents()
        otherAgents = copy.copy(agentOrder)
        solvedPos = copy.deepcopy(self.pos)
        println(solvedPos)
        couldntBeSolved = False
        for agt1 in agentOrder:
            println(f"\nNewagent {agt1}")
            collidedAgents = self.findAndSolveAgt1(agt1, otherAgents)
            if collidedAgents:
                self.pos = copy.deepcopy(solvedPos)
                couldntBeSolved = True
                println(f"Something went wrong with agt {collidedAgents}")
                break
            else:
                solvedPos = copy.deepcopy(self.pos)
                println("solved agt", agt1)

        println(solvedPos)
        self.pos = solvedPos
        self.fixLength()

        if couldntBeSolved:
            println("agents colliding", (collidedAgents[1], collidedAgents[0]))
            return (collidedAgents[1], collidedAgents[0])
        else:
            return None


    def color2agt(self, objid):
        if type(objid) == str:
            for agtKey in self.manager.top_problem.agents:
                _, agtColor = self.manager.top_problem.agents[agtKey][0]
                if agtColor == objid:
                    return int(agtKey)
        return objid

    def prioritiedAgents(self):
        order = []
        penalties = []
        safeZone = []
        safe = True

        i = 0
        for agt, agtPoses in enumerate(self.pos):
            penalty = 0
            hasFreeSpot = 0
            for poses in agtPoses:
                for pos in poses:
                    pass
            for pos1 in agtPoses[0]:
                for pos2 in agtPoses[-1]:
                    occupiedA = self.timeTable[pos1]
                    occupiedB = self.timeTable[pos2]

                    agentsA = [self.color2agt(agtA) for agtA, _ in occupiedA]
                    agentsB = [self.color2agt(agtB) for agtB, _ in occupiedB]
                    aliensA = len(agentsA) - agentsA.count(i)
                    aliensB = len(agentsB) - agentsB.count(i)

                    penalty += -aliensA + aliensB

            penalty += hasFreeSpot
            penalties.append(penalty)
            i += 1
        println(f"penalties on agents(0-x): {penalties}")
        order = sorted(range(len(penalties)), key=lambda k: penalties[k])
        println(f"order of agents: {order}")
        return order

def convert2pos(manager, initPos, paths):
    pos = initPos

    i = 0
    for agt in paths:
        if agt is None:
            continue
        for action in agt:
            prefix = action[0]
            if type(pos[i][-1]) == list:
                [row, col] = pos[i][-1][0]
            else:
                [row, col] = pos[i][-1]
            if prefix == "N":
                pos[i].append([(row, col)])
            elif prefix == "M":
                [drow, dcol] = manager.top_problem.dir[action[-2:-1]]
                pos[i].append([(row + drow, col + dcol)])
            elif prefix == "P":
                if action[0:4] == "Push":
                    [drow1, dcol1] = manager.top_problem.dir[action[-4:-3]]
                    [drow2, dcol2] = manager.top_problem.dir[action[-2:-1]]

                    [row1, col1] = (row + drow1, col + dcol1)
                    [row2, col2] = (row1 + drow2, col1 + dcol2)
                    pos[i].append([(row1, col1), (row2, col2)])
                else:
                    [drow1, dcol1] = manager.top_problem.dir[action[-4:-3]]
                    [drow2, dcol2] = manager.top_problem.dir[action[-2:-1]]

                    [row1, col1] = (row + drow1, col + dcol1)
                    [row2, col2] = (row, col)
                    pos[i].append([(row1, col1), (row2, col2)])

        i += 1

    return pos
