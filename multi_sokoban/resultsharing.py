from copy import deepcopy
from typing import List

from .actions import StateInit
from .emergency_aStar import (BestFirstSearch, aStarSearch_func,
                              calcHuristicsFor)
from .memory import MAX_USAGE, get_usage
from .utils import ResourceLimit, println


class Resultsharing:

    def __init__(self, manager):
        """Initialize with the whole problem definition `top_problem`."""
        self.collisionType = None
        self.pos = []
        self.paths = []
        self.manager = manager
        self.timeTable = {}
    
    '''def fixCollision(self, timeTable, iPos, time, agtIdx):
        tb = 0 # traceback
        agtPos = iPos
        if self.collisionType == "col":
            agents1 = timeTable[iPos, time]
            pos1 = self.pos[agtIdx][time]
            
            # TODO Fix collision for agt 1

        elif self.collisionType == "fcol":
            agents2 = timeTable[iPos, time + 1]
            pos2 = self.pos[agtIdx][time + 1]
            
            # TODO Fix future collision for agt 1 by moving agt2

        elif self.collisionType == "swap":
            agents1 = timeTable[agtPos, time + tb]
            pos1 = self.pos[agtIdx][time + tb]
            agents2 = timeTable[agtPos, time + 1 + tb]
            pos2 = self.pos[agtIdx][time + 1 + tb]

            while checkValidity(self.pos, timeTable, agtPos, time, agtIdx) is not None:
                tb += 1
                agtPos = self.pos[agtIdx][time + tb]
                #println(f"{agtPos}")
            
                if type(agtPos) == list:
                    pass
                else:
                    if (agtPos, time + tb) in timeTable and (agtPos, time + tb + 1) in timeTable:
                        agents1 = timeTable[agtPos, time + tb]
                        pos1 = self.pos[agtIdx][time + tb]
                        agents2 = timeTable[agtPos, time + 1 + tb]
                        pos2 = self.pos[agtIdx][time + 1 + tb]
                    else:
                        pos1 = self.pos[agtIdx][time + tb]
                        pos2 = self.pos[agtIdx][time + 1 + tb]
                        break
                
            # println(f"{(pos1,pos2,time+tb)}")
                
            # TODO fix swap between 2 agents'''

    def addToHash(self, pos, time, identity):
        key = (pos, time)
        value = (identity)
        if key in self.timeTable:
            #timeTable[self.pos, identity].append(time)
            #timeTable[self.pos, time].append(identity)
            self.timeTable[key].append(value)
        else:
            # timeTable[self.pos, identity] = [time]
            #timeTable[self.pos, time] = [identity]
            self.timeTable[key] = [value]


    def generateHash(self):
        timeTable = {}

        #agtColor = self.manager.sort_agents()
        #println(agtColor)

        # Add initial positions for boxes
        for key in self.manager.top_problem.boxes:
            #println(self.manager.top_problem.boxes[key][0])
            boxPos, boxColor = self.manager.top_problem.boxes[key][0]
            self.addToHash(boxPos, 0, boxColor)

        agtColor = []
        for goal, val in self.manager.tasks.items():
            agtColor.append(list(val[0].agents.values())[0][0][1])
        println(agtColor)

        for agtIdx in range(len(self.paths)):
            for time in range(len(self.pos[agtIdx])):
                posAtTime = self.pos[agtIdx][time]
                #println(f"{posAtTime}")
                if len(posAtTime) > 1:
                    #println("the value above is the color")
                    # TODO find a solution to figure out how to identify the box
                    self.addToHash(posAtTime[1], time, agtColor[agtIdx])#
                self.addToHash(posAtTime[0], time, agtIdx)



    def checkPureCollision(self, objPosAtTime1, time, agtIdx):
        #println(f"{objPosAtTime1}, {time}")
        if (objPosAtTime1, time) in self.timeTable:
                
            agentsAtTime1 = self.timeTable[objPosAtTime1, time]
            #println(f"{agentsAtTime1}")
            if len(agentsAtTime1) > 1:
                println(f"collision! at {objPosAtTime1} with   time {time} and agent {agentsAtTime1}")
                return True #"col"  # collision
            # elif (objPos, time + 1) in self.timeTable:
            #     agentsAtTime2 = self.timeTable[objPos, time + 1]
            #     if len(agentsAtTime2) > 1:
            #         println(f"collision! at {objPos} with 1+time {time+1} and agent {agentsAtTime2}")
            #         return "fcol"  # future collision
            return False
        return None

    def checkSwap(self, obj1Pos, obj2Pos, time, agtIdx):
        # TODO swap between two positions
        agentsAtTime1Pos1 = self.timeTable[obj1Pos, time]
        agentsAtTime1Pos2 = self.timeTable[obj2Pos, time]
        agentsAtTime2Pos1 = None 
        agentsAtTime2Pos2 = None
        #println(f"swap1! between {obj1Pos} & {obj2Pos} with time {time} & {time} and agent {agentsAtTime1Pos1} & {agentsAtTime1Pos2}")        
        if (obj1Pos, time + 1) in self.timeTable:
            # println(f"No {obj1Pos, time+1} in timeTable")
            agentsAtTime2Pos1 = self.timeTable[obj1Pos, time + 1]
        if (obj2Pos, time + 1) in self.timeTable:
            # {obj2Pos, time+1} in timeTable")
            agentsAtTime2Pos2 = self.timeTable[obj2Pos, time + 1]
        
        if agentsAtTime2Pos2 == agentsAtTime1Pos1 and agentsAtTime2Pos1 == agentsAtTime1Pos2:
            println(f"swap! between {obj1Pos} & {obj2Pos} with time {time+1} & {time+1} and agent {agentsAtTime2Pos1} & {agentsAtTime2Pos2}")
            return True
        return False

    def isCollision(self, obj1Pos, time, agtIdx):

        collision = self.checkPureCollision(obj1Pos, time, agtIdx)
        if collision is not None:
            if collision is True:
                return "now"

            # check if the next position has a collision at the same time
            obj2Pos = self.pos[agtIdx][time + 1]
            for pos in obj2Pos:
                collision = self.checkPureCollision(pos, time, agtIdx)
                if collision is not None:
                    if collision is True:
                        return "next"
                    swap = self.checkSwap(obj1Pos, pos, time, agtIdx)
                    if swap is True:
                        return "swap"
                    

        # Maybe fuse isSwap and isCollision
        # if (objPosAtTime1, time) in self.timeTable:
        #     agentsAtTime1 = self.timeTable[objPosAtTime1, time]
        #     if len(agentsAtTime1) > 1:
        #         return False

        #     objPosAtTime2 = self.pos[agtIdx][time + 1]
        #     for pos in objPosAtTime2:
        #         if self.isPureCollision(objPosAtTime2, time, agtIdx) is not None:
        #             pass

                    
                            
            # elif (objPosAtTime1, time + 1) in self.timeTable:
            #     agentsAtTime2 = self.timeTable[objPosAtTime1, time + 1]
            #     if len(agentsAtTime2) > 1:
            #         return False
            #     elif agentsAtTime2 != agentsAtTime1:
            #         println(f"swap! between {1} & {2} with time {time} & {time+1} and agent {agentsAtTime1} & {agentsAtTime2}")        
        return False

    def checkValidity(self, time, agtIdx, to=0):
        # to = time offset
        objPos = self.pos[agtIdx][time]
        #println(objPos)
        for pos in objPos:
            collisionType = self.isCollision(pos, time, agtIdx)

                    
                # SWAP
                # elif agentsAtTime2 != agentsAtTime1:
                #     println(f"{agentsAtTime1}, {agentsAtTime2}")
                #     # agt1pos1 = positions[agentsAtTime1][time]
                #     # agt2pos1 = positions[agentsAtTime2][time]
                #     # agt1pos2 = positions[agentsAtTime1][time + 1]
                #     # agt2pos2 = positions[agentsAtTime2][time + 1]
                #     #println(f"{agt1pos1,agt2pos1,agt1pos2,agt2pos2}")
                #     # TODO Swap should only check if they swap positions!
                #     # right now it's a swap if robot 1 goes to position robot 2
                #     # and robot 2 goes a way!
                #     println(f"swap! between {pos1} & {pos2} with time {time} & {time+1} and agent {agentsAtTime1} & {agentsAtTime2}")
                #     return "swap"  # swap between agents

        return None

    # def placeHolderAStar():

    def findAndResolveCollision(self):
        # TODO TODO TODO, reimplement the way it's done, if a collision is found 
        # every agent moves away from the other agents path and gets + points for 
        # moving away from the object and for not standing in the path. Probably use astar for this!
        # +100 for being on the path and -1 for being outside the path
        sorted_agents = self.manager.sort_agents()
        self.paths = [self.manager.status[agent] for agent in sorted_agents if self.manager.status[agent]]

        initpos = [
            [[self.manager.top_problem.agents[self.manager.agent_to_status[agent]][0][0]]]
            for agent in sorted_agents
        ]
        self.pos = convert2pos(self.manager, initpos, self.paths)
        println(self.pos)

        self.generateHash()

        # TODO Also look at future collision 
        println(self.timeTable)
        
        # TODO TODO TODO if there is a collision the non priorities agent warps back in time, 
        # and finds a new path. keeping in mind that it shouldn't occupy that spot at that time

        # sorted goals according to first agent
        goals = self.manager.sort_agents() # for now assume len(goals) = len(agents)
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
            for agtIdx in range(len(self.paths)):
                #timeTable = self.manager.generateHash(self.pos, [paths])
                for time in range(len(self.pos[agtIdx]) - 1):
                    self.collisionType = self.checkValidity(time, agtIdx)

        return None


def isCollisionOld(pos, agt1Idx, i, agt2Idx, j):

    if type(pos[agt1Idx][i]) == list:
        pos1 = pos[agt1Idx][i]
    else:
        pos1 = [pos[agt1Idx][i], pos[agt1Idx][i]]
    if type(pos[agt2Idx][j]) == list:
        pos2 = pos[agt2Idx][j]
    else:
        pos2 = [pos[agt2Idx][j], pos[agt2Idx][j]]

    if (
        pos1[0] == pos2[0]
        or pos1[0] == pos2[1]
        or pos1[1] == pos2[0]
        or pos1[1] == pos2[1]
    ):
        # println([pos1, pos2, True])
        return True
    else:
        # println([pos1, pos2, False])
        return False


# This file is only to make manager.py easier to read.
def resolveCollision(pos, paths, indicies, agt1Idx, agt2Idx, i, j):
    # tracesback
    tb = 0

    while isCollisionOld(pos, agt1Idx, i - tb, agt2Idx, j + tb) or isCollisionOld(
        pos, agt1Idx, i - tb, agt2Idx, j + tb + 1
    ):
        if j + tb + 2 >= len(pos[agt2Idx]):
            break
        tb += 1
        # make chekc if out of bounce, and if it is explore the state!
        # print(i-tb,j+tb)
        # print(pos[agt1Idx][i-tb],pos[agt2Idx][j+tb])

    for k in range(tb + 1):
        pos[agt1Idx].insert(i - tb, pos[agt1Idx][i - tb - 1])


def fixLength(poss):
    longest = 0
    for pos in poss:
        if len(pos) > longest:
            longest = len(pos)

    for pos in poss:
        for i in range(longest - len(pos)):
            pos.append(pos[-1])
            pass


def findAndResolveCollisionOld(manager):
    sorted_agents = manager.sort_agents()
    paths = [manager.status[agent] for agent in sorted_agents if manager.status[agent]]
    initpos = [
        [[manager.top_problem.agents[manager.agent_to_status[agent]][0][0]]]
        for agent in sorted_agents
    ]

    pos = convert2pos(manager, initpos, paths)
    indicies = [0] * len(paths)
    indexChanged = True
    # TODO remove tb from indicies or find another way to.
    # TODO hash with position as key, and the time this position is occupied
    # TODO if no positions are available at the traceback (out of bounds) explore nearby tiles
    while indexChanged:
        indexChanged = False
        for agt1Idx in range(len(paths)):
            i = indicies[agt1Idx] + 1
            # print("agent",agt1Idx, "iteration", i, "position:", pos[agt1Idx][i])
            path = paths[agt1Idx]
            if i >= len(path):
                continue
            else:
                indexChanged = True
                for agt2Idx in range(agt1Idx, len(paths)):
                    if agt2Idx == agt1Idx:
                        continue
                    j = indicies[agt2Idx]
                    cond1 = [pos, agt1Idx, i, agt2Idx, j]
                    cond2 = [pos, agt1Idx, i, agt2Idx, j + 1]
                    if isCollisionOld(*cond1) or isCollisionOld(
                        *cond2
                    ):  # occupiedList[agt2Idx]:
                        # TODO take boxes into account, this is probably why you get tuple integer problems
                        # println(f"Collision between agents! at: {pos[agt1Idx][i]}{pos[agt2Idx][j]}")
                        resolveCollision(pos, paths, indicies, agt1Idx, agt2Idx, i, j)

                indicies[agt1Idx] += 1

    fixLength(pos)
    for agt in range(len(pos)):
        for i in range(len(pos[agt]) - 1):
            if pos[agt][i] == pos[agt][i + 1]:
                if len(paths[agt]) > 0:
                    paths[agt].insert(i, "NoOp")
                else:
                    paths[agt].append("NoOp")
        # while len(paths[agt]) < len(pos[agt])-1:
        # paths[agt].append("NoOp")

        # println(paths)
    # return None if no solution was found

    return pos


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
