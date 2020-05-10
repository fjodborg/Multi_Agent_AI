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
            # timeTable[self.pos, identity].append(time)
            # timeTable[self.pos, time].append(identity)
            self.timeTable[key].append(value)
        else:
            # timeTable[self.pos, identity] = [time]
            # timeTable[self.pos, time] = [identity]
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

        # TODO fix frontier empty problem
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
        params = hash
        #println(f"before {params}, {agt}")
        params = list(filter(lambda x: self.color2agt(x[0]) != agt, params))
        params = list(map(list, zip(*params)))
        #println(f"after {params}")
        if params:
            return params[0], params[1]
        return None

    def getOffsetTime(self, agt2, time):
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


    def findCollisions(self, agt1, pos1, time1, traceback=0):
        #println(f"pos {pos1}, time {time} has the these values {self.timeTable[pos1]}")
        #println(any(occupiedTimes == 10))

        limit = 2

        potentialCollisions = []
        for agt2, poses2 in enumerate(self.pos):
            if agt2 == agt1:
                continue
            time2 = time1 - traceback
            if len(self.pos[agt2]) <= time2 + limit:
                continue
            for time2New in range(time2, time2 + limit):
                for pos2 in poses2[time2New]:
                    #println(f"collision occured {agt1, agt2, pos1, pos2, time1, time2New}")
                    if pos2 == pos1:
                        isSwap = self.isSwap(agt1, agt2, time1, time2New, pos1)
                        potentialCollisions.append((isSwap, agt2, time2New))
                        println(f"collision occured {agt1, agt2, pos1, pos2, time1, time2New}")
        #println(potentialCollisions)
        return potentialCollisions

    def fixPos(self):
        for agent in self.offsetTable.keys():
            for offsetTime, offsetValue in self.offsetTable[agent]:
                for i in range(offsetValue):
                    self.pos[agent].insert(offsetTime, self.pos[agent][offsetTime])
                    pass
                #println((offsetTime, offsetValue, self.pos[agent][offsetTime]))

    def addOffset(self, agt, time, offset=1):
        println(f"offset for agt {agt} added at time {time} is {offset}")
        # comment this out when you need to see if it detects collisions
        for i in range(offset):
            self.pos[agt].insert(time, self.pos[agt][time])

    def handleCollisionData(self, collisionData, agt1, time1):
        if collisionData:
            for isSwap, agt2, time2 in collisionData:
                self.collisionPoints.append(
                    [
                        agt1,
                        agt2,
                        self.pos[agt1][time1],
                        self.pos[agt2][time2]
                    ]
                )
                if (isSwap):
                    isSolved = self.solveSwapNew(agt1, agt2, time1, time2)
                    return isSolved
                # else:
                #     isSolved = self.solveChaseNew(agt1, agt2, time1)
                #     return isSolved
        return False

    def checkDepth(self, depth, time):
        if depth > 10:
            raise Exception("too deep")
        if time > len(self.paths[0]) * 100:
            raise Exception("pos expanded too much")
        

    def solveChase(self, agt1, agt2, time1, depth=0):
        println("chasing")
        self.checkDepth(depth, time1)
        traceback = 0
        nextPos1 = (-2, -2)
        for index1 in reversed(range(-1, time1 - 1)):
            traceback += 1
            if index1 < 0:
                println("agtA out of lower bound in chase")
                self.addOffset(agt2, 0, 2)
                return False

            nextPoses = self.pos[agt1][index1]
            for nextPos1 in nextPoses:
                collisionData = self.findCollisions(agt1, nextPos1, index1)
                if collisionData:
                    for isSwap, agt2_temp, time2_temp in collisionData:
                        if agt2_temp != agt2:
                            index2 = time2_temp - traceback
                            #println(f"New collision needs to be fixed agt {agt1, agt2, agt2_temp}")
                            if isSwap:
                                if self.solveSwap(agt1, agt2_temp, index1, index2, depth + 1):
                                    break
                                # else:
                                #     raise Exception(f"no solution for this swap between{(agt1, agt2_temp)} at time {(index1, index2)}")
                            else:
                                if self.solveChase(agt1, agt2_temp, index1, depth + 1):
                                    break
                                # else:
                                #     raise Exception(f"no solution for this chase between{(agt1, agt2_temp)} at time {(index1, index2)}")
                        pass
                else:
                    println("No collision anymore, adding chase delay")
                    self.addOffset(agt2, index1, 1)
                    return True
        return None

    def solveSwap(self, agt1, agt2, time1, time2, depth=0):
        println("Doing swap")
        self.checkDepth(depth, time1)
        traceback = 0
        for index1 in range(time1 + 1, len(self.pos[agt1])):
            traceback += 1
            index2 = time2 - traceback
            if index2 - traceback < 0:
                println("out of lower bound")
                self.addOffset(agt2, 0, traceback)
                return True
            if index1 >= len(self.pos[agt1]):
                println("out of upper bound")
                return None 

            next_poses = self.pos[agt1][index1]
            for next_pos1 in next_poses:
                collisionData = self.findCollisions(agt1, next_pos1, index1, index1 - index2)
                if collisionData:
                    for isSwap, agt2_temp, time2_temp in collisionData:
                        if agt2_temp != agt2:
                            if isSwap:
                                if self.solveSwap(agt1, agt2_temp, index1, index2, depth + 1):
                                    break
                                # else:
                                #     raise Exception(f"no solution for this swap between{(agt1, agt2_temp)} at time {(index1, index2)}")
                            else:
                                if self.solveChase(agt1, agt2_temp, index1 - 1, depth + 1):
                                    break
                                # else:
                                #     raise Exception(f"no solution for this chase between{(agt1, agt2_temp)} at time {(index1, index2)}")
                        
                else:
                    println("No collision anymore, adding swap delay")
                    totalOffsetValue = index1 - index2 
                    totalOffsetTime = index2
                    
                    self.addOffset(agt2, totalOffsetTime - 1, totalOffsetValue + 2)
                    return True
                        
        return None

    def minimalRep(self):
        return str(self.collisionPoints)

    def addVisitedState(self):
        self.visitedStates.add(self.minimalRep())
        println(f"\nvisited states {self.visitedStates}\n")
        return

    def deadlock(self):
        return self.minimalRep() in self.visitedStates

    def findCollisionsNew(self, agt1, agentsOrder, pos1, time1, traceback=0):
        limit = 3

        potentialCollisions = []
        for agt2 in reversed(agentsOrder):
            poses2 = self.pos[agt2]
            time2 = time1 - traceback - 1
            
            for time2New in range(time2, time2 + limit):
                if len(poses2) <= time2New or time2New < 0:
                    #println("time2 out of bounds")
                    break
                for pos2 in poses2[time2New]:
                    #println(f"collision occured {agt1, agt2, pos1, pos2, time1, time2New}")
                    if pos2 == pos1:
                        isSwap = self.isSwap(agt1, agt2, time1, time2New, pos1)
                        potentialCollisions.append((isSwap, agt2, time2New))
                        println(f"collision occured {agt1, agt2, pos1, pos2, time1, time2New}")
        return potentialCollisions

    def solveAgt1(self, agt1, agentOrder, pos1, time1, collisionData):
        #println(collisionData)                
        if collisionData:
            agt2 = collisionData[0][1]
            if collisionData[0][0]:
                self.pos[agt2].insert(0, self.pos[agt2][0])
            else:
                self.pos[agt2].insert(0, self.pos[agt2][0])
            return True
        return False

    def findAndSolveAgt1(self, agt1, agentOrder):
        foundSolution = False
        otherAgents = copy.deepcopy(agentOrder)
        otherAgents.remove(agt1)
        time1 = 0
        while time1 < len(self.pos[agt1]):
            poses1 = self.pos[agt1][time1]
            println(time1, agt1, otherAgents)
            for pos1 in poses1:
                collisionData = self.findCollisionsNew(agt1, otherAgents, pos1, time1)
                collision = self.solveAgt1(agt1, otherAgents, pos1, time1, collisionData)
                if collision:
                    time1 -= 1
                    foundSolution = False
                else:
                    foundSolution = True
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
        return foundSolution

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
        while not self.deadlock():
            self.addVisitedState()
            self.collisionPoints = []
            for agt1 in agentOrder:
                println(f"\nNewagent {agt1}")
                if not self.findAndSolveAgt1(agt1, otherAgents):
                    println("something wrong here1")
                else:
                    otherAgents.remove(agt1)
                println(otherAgents)
            # if not self.collisionPoints:
            #     println("goal achieved")
            #     break
            # if self.deadlock():
            #     println(f"\n\n deadlock detected. These are the collisions {self.collisionPoints} \n\n")
            #     return None
        self.fixLength()

        println(f"unsolveable due to: {self.unsolvableReason}")

        return True

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
