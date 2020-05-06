from .utils import println


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
        if longest <= shortest:
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

    def findCollisions(self, agt1, pos1, time1):
        #println(f"pos {pos1}, time {time} has the these values {self.timeTable[pos1]}")
        #println(any(occupiedTimes == 10))
        
        extracted = self.extractFromHash(self.timeTable[pos1], agt1)
        if extracted:
            agents, times = extracted
        else: 
            return None

        timesWithOffset = times
        for agentIndex, agt2 in enumerate(agents):
            timesWithOffset[agentIndex] = self.getOffsetTime(agt2, times[agentIndex])

        if type(time1) == list:
            time1, time2 = time1
            println(f"time is list {time1, time2}")
            collisions = None
        else:
            
            time1WithOffset = self.getOffsetTime(agt1, time1)
            collisions = [
                # find proper time condition!
                #            collision                     chase
                #(abs(time1WithOffset - time2WithOffset) <= 1) for time2WithOffset in timesWithOffset
                # fore some reason this one doesn't work the way intended:
                (time2WithOffset == time1WithOffset) or (time2WithOffset == time1WithOffset + 1) for time2WithOffset in timesWithOffset
                # TODO remove agt2 from above?
            ]
        
        #println((collisions, self.offsetTable, agents, times, self.pos[agt2][times[0]], agt1, time1, self.pos[agt1][time1]))
        
        collisionData = [collisions, agents, times]
        actualCollisions = []
        if collisionData and any(collisionData[0]):
            for collision, agt2, time2 in list(zip(*collisionData)):
                if collision:
                    time2WithOffset = self.getOffsetTime(agt2, time2)
                    println(f"collision for agts: {(agt1, agt2)} at time: {(time1WithOffset, time2WithOffset)} and position {(self.pos[agt1][time1],self.pos[agt2][time2],)}")
                    actualCollisions.append([agt2, time2WithOffset])
                    #println(f"collisionData: {actualCollisions}, times {(time1, time2)}/{(len(self.pos[agt1]),len(self.pos[agt2]))}")
                    if time1 >= len(self.pos[agt1]) or time2 >= len(self.pos[agt2]):
                        # TODO VERY IMPORTANT, make solution if time is out of bounds!
                        raise Exception("out of bounds!")
                        # maybe fix length and then rehash?
                    
        return actualCollisions

    def fixPos(self):
        for agent in self.offsetTable.keys():
            for offsetTime, offsetValue in self.offsetTable[agent]:
                for i in range(offsetValue):
                    self.pos[agent].insert(offsetTime, self.pos[agent][offsetTime])
                    pass
                #println((offsetTime, offsetValue, self.pos[agent][offsetTime]))

    def addOffset(self, agt, time, offset=1):
        println(f"offset added at time {time} is {offset}")
        # comment this out when you need to see if it detects collisions
        if agt in self.offsetTable:
            self.offsetTable[agt].append([time, offset])
        else:
            self.offsetTable[agt] = [[time, offset]]
        return

    def tracebackChase(self, agt1, agt2, time1, time2):
        iterations = time1 + 1
        traceback = 1
        
        # Checking and fixing if one is chasing the other
        for time1 in reversed(range(-1, iterations)):
            traceback -= 1
            collided = False
            if time1 < 0:
                println(f"Out of bounds: {time1}/{0}. Adding delay to agent {agt2}")
                self.addOffset(agt2, time2 + traceback)
                break
            
            for pos1 in self.pos[agt1][time1]:
                collisionData = self.findCollisions(agt1, pos1, time1)
                if collisionData and any(collisionData):
                    for agt2_temp, time2_temp in collisionData:
                        
                        if agt2_temp == agt2:
                            collided = True
                            break
                        else:
                            self.tracebackChase(agt1, agt2_temp, time1, time2_temp)
                            println("########## nested traceback not implemented yet###########")
                            # raise Exception("nested traceback not implemented yet")
                            # TODO probably do a traceback if new agent is colliding
                            pass
                    else:
                        continue
                    break

            if collided:
                continue
            else:

                println(f"collision stopped. Adding delay to agent {agt2}")
                #println(f"{pos1,pos2}is swap and not collision")

                #delayTime = time2
                #println((self.pos[agt2][time2], self.pos[agt1][time1]))
                
                # println((int((time1 + time2) / 2),time1, time2,self.getOffsetTime(agt1, time1),self.getOffsetTime(agt2, time2)))
                self.addOffset(agt2, time1)
                break
            #println((time1, self.pos[agt1][time1], time2, self.pos[agt2][time2]))
            
            pass

        return True

    def handleInitialCollisionData(self, collisionData, agt1, time1):
        for agt2, time2 in collisionData:
            # if time2 >= len(self.pos[agt2]):
            #     for i in range(time2 - len(self.pos[agt2]) + 1):
            #         self.pos[agt2].append(self.pos[agt2][-1])
            '''  
            # Old solution
            self.tracebackChase(agt1, agt2, time1, time2)
            # old solution
            ''' 
            self.collisionPoints.append(
                [
                    agt1,
                    agt2,
                    self.pos[agt1][time1],
                    self.pos[agt2][time2]
                ]
            )

            if (self.detectCollisionType(agt1, agt2, time1, time2) == "swap"):
                self.solveSwap(agt1, agt2, time1, time2)
            else:
                self.solveChase(agt1, agt2, time1, time2)




    def solveChase(self, agt1, agt2, time1, time2):
        iterations = time1
        traceback = 0
        
        for index1 in reversed(range(-1, time1)):
            traceback -= 1
            collided = False
            if index1 < 0:
                println("out of bounds")
                self.addOffset(agt2, 0)
                return

            next_poses = self.pos[agt1][index1]
            for next_pos1 in next_poses:
                collisionData = self.findCollisions(agt1, next_pos1, time1)
                if collisionData:
                    for agt2_temp, time2_temp in collisionData:
                        if agt2_temp != agt2:
                            index2 = time2_temp + traceback
                            println(f"New collision needs to be fixed agt {agt1, agt2, agt2_temp}")
                            if self.detectCollisionType(agt1, agt2_temp, index1, index2) == "swap":
                                pass
                            else:
                                self.solveChase(agt1, agt2_temp, index1, index2)
                                break
                        pass
                else:
                    println("No collision anymore, adding chase delay")
                    self.addOffset(agt2, time1 - 1)
                    return True
                    

        

    def solveSwap(self, agt1, agt2, time1, time2):
        pass

    def detectCollisionType(self, agt1, agt2, time1, time2):
        pos11 = self.pos[agt1][time1]
        pos12 = self.pos[agt1][time1 + 1]
        pos21 = self.pos[agt2][time1]
        pos22 = self.pos[agt2][time1 + 1]
        if type(pos11) == list:
            pos11 = pos11[0]
        if type(pos12) == list:
            pos12 = pos12[0]
        if type(pos21) == list:
            pos21 = pos21[0]
        if type(pos22) == list:
            pos22 = pos22[0]
        
        dist1 = abs((pos11[0] - pos12[0]) + (pos21[0] - pos22[0]))
        dist2 = abs((pos11[1] - pos12[1]) + (pos21[1] - pos22[1]))
        #println((f"swap values is {dist1+dist2 == 0}", dist1, dist2))
        if dist1 + dist2 == 0:
            return "swap"
        else:
            return "chase"













    def minimalRep(self):
        return str(self.collisionPoints)

    def addVisitedState(self):
        self.visitedStates.add(self.minimalRep())
        println(f"\nvisited states {self.visitedStates}\n")
        return

    def deadlock(self):
        return self.minimalRep() in self.visitedStates

    def findAndResolveCollision(self):
        # TODO just call the function traceback in a nest then no deadlock detection is needed
        # get next pos and check if someone is there

        # TODO make every pos an object attribute
        # TODO TODO TODO, reimplement the way it's done, if a collision is found
        # every agent moves away from the other agents path and gets + points for
        # moving away from the object and for not standing in the path. Probably use astar for this!
        # +100 for being on the path and -1 for being outside the path
        sorted_agents = self.manager.sort_agents()
        self.paths = self.manager.solutions
        println(self.manager.solutions)
        
        initpos = [[[self.manager.agents[agent].init_pos]] for agent in sorted_agents]
        self.pos = convert2pos(self.manager, initpos, self.paths)

        # for pos in self.pos:
        #     for i in range(len(pos)):
        #         pos.append(pos[-1])
        println(self.pos)

        # TODO TODO TODO if there is a collision the non priorities agent warps back in time,
        # and finds a new path. keeping in mind that it shouldn't occupy that spot at that time

        # sorted goals according to first agent
        # for goal in self.manager.agent_to_status.keys():
        #     if self.manager.agent_to_status[goal] == agt:
        #         pass
        #         # do things with goal
        self.generateTimeTable()
        println(self.timeTable)
        self.unsolvableReason = None
        

        # TODO try and solve only with first one if in goal try the next one if error try the next one and save it for later
        

        # TODO remove tb from indicies or find another way to.
        # TODO hash with position as key, and the time this position is occupied
        # TODO if no positions are available at the traceback (out of bounds) explore nearby tiles
        agentOrder = self.prioritiedAgents()
        while not self.deadlock():
            self.addVisitedState()
            self.collisionPoints = []
            #println(agentOrder)
            for agt1 in agentOrder:
                println(f"\nNewagent {agt1}")
                if agt1 in self.offsetTable:
                    println(f"offset table for agt {agt1}: {self.offsetTable[agt1]}")
                for time1, poses in (list(enumerate(self.pos[agt1]))):
                    # Find a way to implement so the next iteration of agents get's the correct time
                    # could be to rehash or to simply add the time offset and fix bounds
                    # if agt in self.offsetTable:
                    #     for offsetTime, offsetValue in self.offsetTable[agt]:
                    #         if time >= offsetTime:
                    #             newTime += offsetValue

                    for pos in poses:
                        
                        collisionData = self.findCollisions(agt1, pos, time1)
                        #println((collisionData, self.offsetTable, agt, time, self.pos[agt][time]))
                        
                        #println(f"collision: {collisionData[0]}, agts: {(agt, agt2)}, time: {(time, time2)}")
                        if collisionData:
                            self.handleInitialCollisionData(collisionData, agt1, time1)
                                
                                # self.tracebackChase(agt1, agt2, time1, time2)
                                
                                #self.tracebackSwap(agt1, agt2, time1, time2)
                                # println(self.offsetTable)
                                    #deadlock = False
                                    # fixPos shouldn't be called here
                                    # self.fixPos()
                            # TODO
                            # make traceback here, it should traceback and if it collides with a agent.
                            # the second agent should traceback until it can't or collides with a new one:
                            # if 1 collides with 2, 2 is traced back, if it collides with 3, 3 is traced back
                            # and if it doesn't collide 2 i traced back and at last 1.
            #println(f"collision points {self.collisionPoints}")
            if not self.collisionPoints:
                println("goal achieved")
                break
            if self.deadlock():
                println(f"\n\n deadlock detected. These are the collisions {self.collisionPoints} \n\n")
                break

        self.fixPos()
        self.fixLength()

        # TODO delete hashtables

        println(f"unsolveable due to: {self.unsolvableReason}")

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
        
        i = 0
        for agtPos in self.pos:
            penalty = 0
            for pos1 in agtPos[0]:
                for pos2 in agtPos[-1]:
                    occupiedA = self.timeTable[pos1]
                    occupiedB = self.timeTable[pos2]

                    agentsA = [self.color2agt(agtA) for agtA, _ in occupiedA]
                    agentsB = [self.color2agt(agtB) for agtB, _ in occupiedB]
                    aliensA = len(agentsA) - agentsA.count(i)
                    aliensB = len(agentsB) - agentsB.count(i)
                    
                    penalty += -aliensA + aliensB

                    #println((occupiedA, penalty, occupiedB))
                    
            penalties.append(penalty)
            i += 1
        println(f"penalties on agents(0-x): {penalties}")
        order = sorted(range(len(penalties)), key=lambda k: penalties[k])
        println(f"order of agents: {order}")
        return order

def convert2pos(manager, initPos, paths):
    pos = initPos

    i = 0
    # println(f"pos: {pos}")
    for agt in paths:
        if agt is None:
            continue
        for action in agt:
            prefix = action[0]
            # println(f"pos: {pos[i][-1]}")
            if type(pos[i][-1]) == list:
                [row, col] = pos[i][-1][0]
            else:
                [row, col] = pos[i][-1]
            # println(f"row:{row},col:{col}")
            if prefix == "N":
                pos[i].append([(row, col)])
            elif prefix == "M":
                [drow, dcol] = manager.top_problem.dir[action[-2:-1]]
                pos[i].append([(row + drow, col + dcol)])
            elif prefix == "P":
                if action[0:4] == "Push":
                    [drow1, dcol1] = manager.top_problem.dir[action[-4:-3]]
                    [drow2, dcol2] = manager.top_problem.dir[action[-2:-1]]
                    # println(f"{row},{drow1}")

                    [row1, col1] = (row + drow1, col + dcol1)
                    [row2, col2] = (row1 + drow2, col1 + dcol2)
                    pos[i].append([(row1, col1), (row2, col2)])
                else:
                    [drow1, dcol1] = manager.top_problem.dir[action[-4:-3]]
                    [drow2, dcol2] = manager.top_problem.dir[action[-2:-1]]
                    # println(f"{row},{drow1}")

                    [row1, col1] = (row + drow1, col + dcol1)
                    [row2, col2] = (row, col)
                    pos[i].append([(row1, col1), (row2, col2)])

        i += 1

    return pos
