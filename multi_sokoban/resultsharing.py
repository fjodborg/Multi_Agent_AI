from copy import deepcopy
from typing import List

from .actions import StateInit
from .emergency_aStar import BestFirstSearch, calcHuristicsFor
from .memory import MAX_USAGE, get_usage
from .utils import ResourceLimit, println



class Agent:
    def __init__(self):
        self.id = 0
        self.t1 = 0
        self.t2 = 0
        self.p1 = 0
        self.p2 = 0
        self.poses = []


class Resultsharing:
    def __init__(self, manager, inbox):
        """Initialize with the whole problem definition `top_problem`."""
        self.pos = []
        self.paths = []
        self.manager = manager
        self.timeTable = {}
        self.traceback = 0
        #self.collisionType = None
        self.collidedAgents = None
        self.unsolvableReason = [None]
        self.isNotBound = 0
        self.inbox = inbox
        self.agtA = Agent()
        self.agtB = Agent()

    def addToHash(self, pos, time, identity):
        ''' Not in use at the moment '''
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

    def generateHash(self):
        ''' Not in use at the moment '''
        for key in self.manager.top_problem.boxes:
            boxPos, boxColor = self.manager.top_problem.boxes[key][0]
            self.addToHash(boxPos, 0, boxColor)
            # for agtKey in self.manager.top_problem.agents:
            #     _, agtColor = self.manager.top_problem.agents[agtKey][0]
            #     if agtColor == boxColor:
            #         self.addToHash(boxPos, 0, agtKey)

        agtColor = []
        for goal, val in self.manager.tasks.items():
            agtColor.append(list(val[0].agents.values())[0][0][1])

        for agtIdx in range(len(self.paths)):
            for time in range(len(self.pos[agtIdx])):
                posAtTime = self.pos[agtIdx][time]
                if len(posAtTime) > 1:
                    self.addToHash(posAtTime[1], time, agtIdx) 
                self.addToHash(posAtTime[0], time, agtIdx)

        return None

    def isOutOfBound(self, time, agt):
        # self.inbox.append(Message( object_problem="0", bla bla bla))
        maxLength = len(self.pos[agt])
        # if time >= maxLength:
        #     #println(f"Out of bounds for agent {agt} at time {time}/{len(self.pos[agt])-1}")
        #     self.pos[agt].append(self.pos[agt][-1])
        #     println(f"extending bound for agent {agt} to {len(self.pos[agt])-1}")
        if time < 0 or time >= maxLength:
            self.isNotBound += 1
            troubleMaker = agt #self.collidedAgents[1]
            troubleTime = time #1+self.collidedAgents[3] #-self.traceback
            # TODO make the call back
            self.unsolvableReason = [troubleMaker, troubleTime, "out of bounds/no traceback"]
            println(f"Out of bounds for agent {troubleMaker} at time {time}/{len(self.pos[troubleMaker])-1}")
            return True
        return False


    def isCollision(self, agt1, agt2, pos1, pos2, time1, time2):
        if pos1 == pos2:
            self.collidedAgents = [agt1, agt2, time1, time2, pos1, pos2]
            println(
                f"collision! between {pos1} & {pos2} with time {time1, time2} and agent {agt1, agt2}"
            )
            return True
        return False

    def checkCollisions(self, agtA, agtB):
        
        agtA.t2 = agtA.t1
        agtB.t2 = agtB.t1
        # TODO Write this cleaner
        if self.isOutOfBound(agtB.t2, agtB.id):
            return None
        agtB.poses = self.pos[agtB.id][agtB.t2]
        for agtB.p2 in agtB.poses:
            if self.isCollision(agtA.id, agtB.id, agtA.p1, agtB.p2, agtA.t1, agtB.t2):
                return True
    
        agtB.t2 += 1
        if self.isOutOfBound(agtB.t2, agtB.id):
            return None
        agtB.poses = self.pos[agtB.id][agtB.t2]
        for agtB.p2 in agtB.poses:
            if self.isCollision(agtA.id, agtB.id, agtA.p1, agtB.p2, agtA.t1, agtB.t2):
                return True

        agtB.t2 += 1
        if self.isOutOfBound(agtB.t2, agtB.id):
            return None
        agtB.poses = self.pos[agtB.id][agtB.t2]
        for agtB.p2 in agtB.poses:
            if self.isCollision(agtA.id, agtB.id, agtA.p1, agtB.p2, agtA.t1, agtB.t2):
                return True
        
        
        agtA.t2 += 1
        if self.isOutOfBound(agtA.t2, agtA.id):
            return None
        agtA.poses = self.pos[agtA.id][agtA.t2]
        for agtA.p2 in agtA.poses:
            if self.isCollision(agtA.id, agtB.id, agtA.p2, agtB.p1, agtA.t2, agtB.t1):
                return True
        
        agtA.t2 += 1
        if self.isOutOfBound(agtA.t2, agtA.id):
            return None
        agtA.poses = self.pos[agtA.id][agtA.t2]
        for agtA.p2 in agtA.poses:
            if self.isCollision(agtA.id, agtB.id, agtA.p2, agtB.p1, agtA.t2, agtB.t1):
                return True


        return False
         

    def findCollidingAgt(self, agtA, agtB):
        agtA.Poses = self.pos[agtA.id][agtA.t1]
        for agtA.p1 in agtA.Poses:
            for agtB.id in range(len(self.pos)):
                if agtA.id == agtB.id:
                    continue
                agtB.t1 = agtA.t1
                isCollision = self.checkCollisions(agtA, agtB)
                if isCollision:
                    return True
                elif isCollision is None:
                    self.collidedAgents = None
                    return None
            else:
                continue
            break
        return False

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

    def tracebackCollision(self):
        # TODO take into account if there is multiple agents
        # TODO if out of bounds or no solution found return a new value
        #println(self.collidedAgents)
        agtA = self.agtA
        agtB = self.agtB
        collisionTime = agtA.t1
        
        for i in range(2):
            noSolution = False
            if i == 1:
                agtA2 = deepcopy(agtB)
                agtB2 = deepcopy(agtA)
            else:
                agtB2 = deepcopy(agtB)
                agtA2 = deepcopy(agtA)

            agtB2.t1 = collisionTime + 1
            self.traceback = 0
            self.collidedAgents = None
            println("Traceback collision from now on:")
            collision = True
            for agtA2.t1 in range(collisionTime, len(self.pos[agtA2.id])):
                collision = False
                agtB2.t1 -= 1
                self.traceback += 1
                #println((agtA.poses,agtB.poses,agtA.t1,agtB.t1))
                agtA2.poses = self.pos[agtA2.id][agtA2.t1]
                agtB2.poses = self.pos[agtB2.id][agtB2.t1]
                #println((agtA2.poses,agtB2.poses,agtA2.t1,agtB2.t1, self.collidedAgents))
                
                for agtA2.p1 in agtA2.poses:
                    for agtB2.p2 in agtB2.poses:
                        hasCollided = self.checkCollisions(agtA2, agtB2)
                        if self.isOutOfBound(agtA2.t1 + 1, agtA2.id):
                            println("test")
                            break
                        if hasCollided:
                            collision = True
                            break
                        elif hasCollided is None:
                            println(f"out of bound. Steps back {self.traceback}")
                            noSolution = True
                            break
                            
                    else:
                        continue
                    break  # if collision is True
                if noSolution:
                    println("no solution")
                    break
                if not collision:
                    self.traceback -= 1
                    println(f"Traceback found. Steps back {self.traceback}")
                    self.unsolvableReason = [None]
                    return agtB2.t1, agtB2.id 


        println(f"out of bound. Steps back {self.traceback}")
        return [None, None]
           

    def fixCollision(self):
        backwardTime, agt = self.tracebackCollision()
        if backwardTime is None:
            self.traceback = 0
            return None
        elif backwardTime < 0:
            backwardTime = 0
        
        for i in range(self.traceback * 2):
            # Maybe remove this line, i don't think we need it
            # println((i, agt, backwardTime, self.pos[agt][backwardTime], ))
            self.pos[agt].insert(backwardTime, self.pos[agt][backwardTime])
        
        self.traceback = 0
        return True
        # println(self.pos)
        # println(self.paths)


    def extractFromHash(self, hash, agt):
        params = hash
        #println(f"before {params}, {agt}")
        params = list(filter(lambda x: self.color2agt(x[0]) != agt, params))
        params = list(map(list, zip(*params)))
        #println(f"after {params}")
        if params:
            return params[0], params[1]
        return None

    def findAndResolveCollision(self):
        # TODO make every pos an object attribute
        # TODO TODO TODO, reimplement the way it's done, if a collision is found
        # every agent moves away from the other agents path and gets + points for
        # moving away from the object and for not standing in the path. Probably use astar for this!
        # +100 for being on the path and -1 for being outside the path
        sorted_agents = self.manager.sort_agents()
        self.paths = [
            self.manager.status[agent]
            for agent in sorted_agents
            if self.manager.status[agent]
        ]

        initpos = [
            [
                [
                    self.manager.top_problem.agents[
                        self.manager.agent_to_status[agent]
                    ][0][0]
                ]
            ]
            for agent in sorted_agents
        ]
        self.pos = convert2pos(self.manager, initpos, self.paths)

        # for pos in self.pos:
        #     for i in range(len(pos)):
        #         pos.append(pos[-1])
        println(self.pos)

        # TODO TODO TODO if there is a collision the non priorities agent warps back in time,
        # and finds a new path. keeping in mind that it shouldn't occupy that spot at that time

        # sorted goals according to first agent
        goals = self.manager.sort_agents()  # for now assume len(goals) = len(agents)
        println(self.manager.tasks[goals[0]][0])

        # for goal in self.manager.agent_to_status.keys():
        #     if self.manager.agent_to_status[goal] == agt:
        #         pass
        #         # do things with goal
        self.generateHash()
        println(self.timeTable)
        deadlock = False
        self.unsolvableReason = None
        # TODO remove tb from indicies or find another way to.
        # TODO hash with position as key, and the time this position is occupied
        # TODO if no positions are available at the traceback (out of bounds) explore nearby tiles
        agtA = self.agtA
        agtB = self.agtB

        while not deadlock:
            
            deadlock = True
            agentOrder = self.prioritiedAgents()
            println(agentOrder)
            for agt in agentOrder:
                for time, poses in enumerate(reversed(self.pos[agt])):
                    for pos1 in poses:
                        println(f"pos {pos1} has the these values {self.timeTable[pos1]}")
                        #println(any(occupiedTimes == 10))
                        current_position = pos1
                        current_agent = agt
                        current_time = time
                        position_hash = self.timeTable

                        extracted = self.extractFromHash(self.timeTable[pos1], agt)
                        if extracted:
                            agents, times = extracted
                        else: 
                            continue
                        println(f"pos {pos1} has the these values {agents}, {times}, agt {agt} {time}")

                        
                        #times = [values[1] for values in position_hash[current_position]]
                        #agents = [self.color2agt(values[0]) for values in position_hash[current_position]]
                        #println((agents, agt)) # agents er kun 1 agent?!?!?
                        times_with_offset = times
                        offset_hash = {}
                        offset_hash[0] = [(0,0),(2,3)]
                        offset_hash[1] = [(0,0),(6,7)]
                        #offset_hash.clear()
                        #println(len(times))
                        for agent_index, agent in enumerate(agents):
                            for offset_times, offset_values in offset_hash[agent]:
                                if offset_times <= times[agent_index]:
                                    times_with_offset[agent_index] += offset_values
                        collisions = [
                            abs(current_time - time) <= 1 for agent, time in enumerate(times_with_offset)
                        ]
                        println((collisions, pos1, agents, times))
                        if any(collisions):
                            println("yes")
            # Add offset at time x to hashtable when looking at times 

            # TODO take boxes into account
            
            # for agtA.id in range(len(self.paths)):
            #     # timeTable = self.manager.generateHash(self.pos, [paths])
            #     for agtA.t1 in range(len(self.pos[agtA.id]) - 1):
                    
            #         self.traceback = 0
            #         self.collidedAgents = None
            #         collisionType = self.findCollidingAgt(agtA, agtB)
            #         # println((collisionType, self.collidedAgents))
                    
            #         if self.collidedAgents is not None:
            #             #println((collisionType, self.collidedAgents))
            #             if self.fixCollision() is not None:
            #                 if self.isNotBound:
            #                     deadlock = False
            #                 break
            #         elif self.isNotBound:
            #             println("out of bounds, and no collision detected")
            #             # maybe return here?
            #             break
                    
        self.fixLength()

        println(self.isNotBound)
        if self.isNotBound > 0:
            self.unsolvableReason = [self.collidedAgents, "out of bounds/no traceback"]
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
        println(penalties)
        order = sorted(range(len(penalties)), key=lambda k: penalties[k])
        println(order)
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
