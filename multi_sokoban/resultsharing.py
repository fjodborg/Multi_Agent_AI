from copy import deepcopy
from typing import List

from .actions import StateInit
from .emergency_aStar import BestFirstSearch, calcHuristicsFor
from .memory import MAX_USAGE, get_usage
from .utils import ResourceLimit, println


class Resultsharing:
    def __init__(self, manager):
        """Initialize with the whole problem definition `top_problem`."""
        self.pos = []
        self.paths = []
        self.manager = manager
        # self.timeTable = {}
        self.traceback = 0
        self.collisionType = None
        self.collidedAgents = None
        self.collisionTime = None

    def addToHash(self, pos, time, identity):
        key = (pos, time)
        value = identity
        if key in self.timeTable:
            # timeTable[self.pos, identity].append(time)
            # timeTable[self.pos, time].append(identity)
            self.timeTable[key].append(value)
        else:
            # timeTable[self.pos, identity] = [time]
            # timeTable[self.pos, time] = [identity]
            self.timeTable[key] = [value]

    def generateHash(self):
        # agtColor = self.manager.sort_agents()
        # println(agtColor)

        # Add initial positions for boxes
        for key in self.manager.top_problem.boxes:
            # println(self.manager.top_problem.boxes[key][0])
            boxPos, boxColor = self.manager.top_problem.boxes[key][0]
            self.addToHash(boxPos, 0, boxColor)

        agtColor = []
        for goal, val in self.manager.tasks.items():
            agtColor.append(list(val[0].agents.values())[0][0][1])
        println(agtColor)

        for agtIdx in range(len(self.paths)):
            for time in range(len(self.pos[agtIdx])):
                posAtTime = self.pos[agtIdx][time]
                # println(f"{posAtTime}")
                if len(posAtTime) > 1:
                    # println("the value above is the color")
                    # TODO find a solution to figure out how to identify the box
                    self.addToHash(posAtTime[1], time, agtColor[agtIdx])  #
                self.addToHash(posAtTime[0], time, agtIdx)

    def checkPureCollision(self, time, agt1):
        agt1Pos = self.pos[agt1][time]
        for agt2 in range(len(self.pos)):
            if agt1 == agt2:
                continue
            for pos1 in obj1Pos:
                println(agt2)
                for obj2Pos in self.pos[agt2][time]:
                    for pos2 in obj2Pos:
                        println((pos1, pos2, agt1, agt2))

        # if (objPosAtTime1, time) in self.timeTable:

        #     agentsAtTime1 = self.timeTable[objPosAtTime1, time]
        #     #println(f"{time} {agentsAtTime1}")
        #     if len(agentsAtTime1) > 1:
        #         agts = [[agt] for agt in agentsAtTime1]
        #         #println([type(obj) != int for obj in agentsAtTime1])
        #         self.collidedAgents = agts
        #         return True
        #     return False
        return None
        # if (objPosAtTime1, time) in self.timeTable:

        #     agentsAtTime1 = self.timeTable[objPosAtTime1, time]
        #     #println(f"{time} {agentsAtTime1}")
        #     if len(agentsAtTime1) > 1:
        #         agts = [[agt] for agt in agentsAtTime1]
        #         #println([type(obj) != int for obj in agentsAtTime1])
        #         self.collidedAgents = agts
        #         return True
        #     return False
        # return None

    def checkSwap(self, obj1Pos, obj2Pos, time, agtIdx):

        agentsAtTime1Pos1 = self.timeTable[obj1Pos, time]
        agentsAtTime1Pos2 = self.timeTable[obj2Pos, time]
        println(f"{agentsAtTime1Pos2,agentsAtTime1Pos1}")
        pos1AtTime1 = self.pos[agentsAtTime1Pos1[0]][time]
        pos2AtTime1 = self.pos[agentsAtTime1Pos2[0]][time]
        pos1AtTime2 = self.pos[agentsAtTime1Pos1[0]][time + 1]
        pos2AtTime2 = self.pos[agentsAtTime1Pos2[0]][time + 1]
        for pos12 in pos2AtTime1:
            for pos21 in pos1AtTime2:
                if pos12 == pos21:
                    swap1 = True
                    break
            else: 
                continue 
            break 

        for pos11 in pos1AtTime1:
            for pos22 in pos2AtTime2:
                if pos11 == pos22 and swap1 is True:
                    self.collidedAgents = [agentsAtTime1Pos1, agentsAtTime1Pos2]
                    print(
                        f"swap! between {pos11} & {pos12} with time {time+1} & {time+1} and agent {agentsAtTime1Pos1} & {agentsAtTime1Pos2}"
                    )
                    return True

        ''' # doesn't seem to work, but can't figure out why
            
            println(f"{pos11,pos12,pos21,pos22}")
            println(f"{self.pos[agentsAtTime1Pos1[0]][time], self.pos[agentsAtTime1Pos2[0]][time]}")
            println(f"{self.pos[agentsAtTime1Pos1[0]][time+1], self.pos[agentsAtTime1Pos2[0]][time-1]}")

            # println(f"swap1! between {obj1Pos} & {obj2Pos} with time {time} & {time} and agent {agentsAtTime1Pos1} & {agentsAtTime1Pos2}")
            if (obj1Pos, time + 1) in self.timeTable:
                #println(f"{obj1Pos, time+1} in timeTable")
                agentsAtTime2Pos1 = self.timeTable[obj1Pos, time + 1]
            if (obj2Pos, time + 1) in self.timeTable:
                #println(f"{obj2Pos, time+1} in timeTable")
                agentsAtTime2Pos2 = self.timeTable[obj2Pos, time + 1]

            if (
                agentsAtTime2Pos2 == agentsAtTime1Pos1
                and agentsAtTime2Pos1 == agentsAtTime1Pos2
            ):
                println(
                    f"swap! between {obj1Pos} & {obj2Pos} with time {time+1} & {time+1} and agent {agentsAtTime1Pos1} & {agentsAtTime1Pos2}"
                )
                self.collidedAgents = [agentsAtTime1Pos1, agentsAtTime1Pos2]
                return True '''
        return None

    def fixBoxCollision(self):
        pass

    def isOutOfBound(self, time, agt2):
        if time >= len(self.pos[agt2]) or time < 0:
            println(f"Out of bounds for agent {agt2} at time {time+1}/{len(self.pos[agt2])-1}")
            return True
        return False

    def checkTailing(self, agt1, agt2, pos12, pos22, time):
        if type(time) == list:
            time1 = time[0] + 1
            time2 = time[1] + 1
        else:
            time1 = time + 1
            time2 = time + 1
        
        if self.isOutOfBound(time1, agt1) is True:
            return None
        agt1Pos = self.pos[agt1][time1]
        for pos11 in agt1Pos:
            if pos22 == pos11:
                self.collidedAgents = [agt1, agt2]
                println(
                    f"tail! between {pos11} & {pos12} with time {[time1-1,time2]} and agent {agt1} & {agt2}"
                )
                return agt1
        
        if self.isOutOfBound(time2, agt2) is True:
            return None

        agt2Pos = self.pos[agt2][time2]
        for pos21 in agt2Pos:
            if pos12 == pos21:
                self.collidedAgents = [agt1, agt2]
                println(
                    f"tail! between {pos21} & {pos22} with time {[time1,time2-1]} and agent {agt1} & {agt2}"
                )
                return agt2
        return None

    def checkSwapNew(self, agt1, agt2, pos12, pos22, time):
        if type(time) == list:
            time1 = time[0] + 1
            time2 = time[1] + 1
        else:
            time1 = time + 1
            time2 = time + 1

        swap = False
        #println(time)
        if self.isOutOfBound(time1, agt1) is True:
            return None
        agt1Pos = self.pos[agt1][time1]
        for pos11 in agt1Pos:
            if pos22 == pos11:
                swap = True
                break

        if self.isOutOfBound(time2, agt2) is True:
            return None
        agt2Pos = self.pos[agt2][time2]
        for pos21 in agt2Pos:
            if pos12 == pos21 and swap is True:
                self.collidedAgents = [agt1, agt2]
                println(
                    f"swap! between {pos21} & {pos22} with time {[time1,time2]} and agent {agt1} & {agt2}"
                )
                return True
        return None

    def isCollisionNew(self, agt1, agt2, pos1, pos2, time):
        
        if pos1 == pos2:
            self.collidedAgents = [agt1, agt2]
            println(
                f"collision! between {pos1} & {pos1} with time {time} and agent {agt1} & {agt2}"
            )
            return True
        return None

    def findCollidingAgt(self, agt1, time):

        agt1Pos = self.pos[agt1][time]
        for pos1 in agt1Pos:
            for agt2 in range(len(self.pos)):
                if agt1 == agt2:
                    continue
                if self.isOutOfBound(time, agt2) is True:
                    continue
                agt2Pos = self.pos[agt2][time]
                for pos2 in agt2Pos:
                    if self.isCollisionNew(agt1, agt2, pos1, pos2, time) is True:
                        self.collisionType = "col"
                        return agt2
                    if self.checkSwapNew(agt1, agt2, pos1, pos2, time) is not None:
                        self.collisionType = "swap"
                        return agt2
                    tailingAgt = self.checkTailing(agt1, agt2, pos1, pos2, time)
                    if tailingAgt is not None:
                        self.collisionType = "tail"
                        return tailingAgt

        return None

   
    # def placeHolderAStar():

    def tracebackCollision(self, collisionTime):
        # TODO take into account if there is multiple agents
        # TODO if out of bounds or no solution found return a new value
        println(self.collidedAgents)
        agt1 = self.collidedAgents[1]
        agt2 = self.collidedAgents[0]
        time2 = collisionTime + 1
        println("Traceback colission from now on:")
        for time1 in range(collisionTime, len(self.pos[agt1])):
            time2 -= 1
            obj1Pos = self.pos[agt1][time1]
            obj2Pos = self.pos[agt2][time2]
            obj3Pos = self.pos[agt2][time2 + 1]
            collision = False
            if self.isOutOfBound(time1, agt1) is True:
                println("Traceback not found")
                return None, None, None
            if self.isOutOfBound(time2, agt1) is True:
                println("Traceback not found")
                return None, None, None

            # println(f"{obj1Pos,obj2Pos,obj3Pos}, {time1,time2,time2+1}")
            for pos1 in obj1Pos:
                for pos2 in obj2Pos:
                    if self.isCollisionNew(agt1, agt2, pos1, pos2, [time1, time2]) is True:
                        continue
                        collision = True
                    if self.checkSwapNew(agt1, agt2, pos1, pos2, [time1, time2]):
                        collision = True
                        continue
                    if self.checkTailing(agt1, agt2, pos1, pos2, [time1, time2]):
                        collision = True
                        continue
                # for pos3 in obj3Pos:
                #     if pos1 == pos3:
                #         collision = True
                #         println(
                #             f"traceback swap at {pos1} & {pos2} at time {[time1, time2]} with agent {agt1} {agt2}"
                #         )
                #         continue
            if collision is False:
                break
            # TODO fix collision time, it should differ when using swap and collision
        println("Traceback found")
        return time1, time2, agt2  # the last one was not a a collision

    def fixLength(self):
        lengths = [len(self.pos[agt]) for agt in range(len(self.pos))]
        longest = max(lengths)
        shortest = min(lengths)
        println(longest)
        println(shortest)
        dif = False
        if longest > shortest:
            dif = True

        if dif is False:
            return None
            pass

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

    def fixCollision(self, collisionTime):
        forwardTime, bakcwardTime, agt = self.tracebackCollision(collisionTime)
        if bakcwardTime is None:
            self.traceback = 0
            return None
        for i in range(forwardTime - bakcwardTime):
            # Maybe remove this line, i don't think we need it
            self.pos[agt].insert(bakcwardTime+1, self.pos[agt][bakcwardTime+1])
        
        self.traceback = 0
        return True
        # println(self.pos)
        # println(self.paths)

    def findAndResolveCollision(self):
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
        println(self.pos)

        # self.generateHash()

        # TODO Also look at future collision
        # println(self.timeTable)

        # TODO TODO TODO if there is a collision the non priorities agent warps back in time,
        # and finds a new path. keeping in mind that it shouldn't occupy that spot at that time

        # sorted goals according to first agent
        goals = self.manager.sort_agents()  # for now assume len(goals) = len(agents)
        println(self.manager.tasks[goals[0]][0])

        # for goal in self.manager.agent_to_status.keys():
        #     if self.manager.agent_to_status[goal] == agt:
        #         pass
        #         # do things with goal

        deadlock = False
        # TODO remove tb from indicies or find another way to.
        # TODO hash with position as key, and the time this position is occupied
        # TODO if no positions are available at the traceback (out of bounds) explore nearby tiles
        while not deadlock:

            deadlock = True
            # for agt1 in range(len(self.paths) - 1, 0, -1):
            for agt1 in range(len(self.paths)):
                # timeTable = self.manager.generateHash(self.pos, [paths])
                for time in range(len(self.pos[agt1]) - 1):
                    self.traceback = 0
                    collisionType = self.findCollidingAgt(agt1, time)
                    #println(collisionType)
                    if collisionType is not None:
                        # #TODO break out to deadlock loop, fix actions and rehash
                        ####
                        if self.fixCollision(time) is not None:
                            # deadlock = False
                            break
                    self.collisionType = None
                    self.collidedAgents = None
                    self.collisionTime = None
                    
                else:
                    continue
            self.fixLength()
        return None


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
