from copy import deepcopy
from typing import List

from .actions import StateInit
from .emergency_aStar import (BestFirstSearch, aStarSearch_func,
                              calcHuristicsFor)
from .memory import MAX_USAGE, get_usage
from .utils import ResourceLimit, println


# This file is only to make manager.py easier to read.
def resolveCollision(pos, paths, indicies, agt1Idx, agt2Idx, i, j):
    # tracesback
    tb = 0

    while isCollision(pos, agt1Idx, i - tb, agt2Idx, j + tb) or isCollision(
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


def findAndResolveCollisionOld(pos, paths):
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
                    if isCollision(*cond1) or isCollision(
                        *cond2
                    ):  # occupiedList[agt2Idx]:
                        # TODO take boxes into account, this is probably why you get tuple integer problems
                        # println(f"Collision between agents! at: {pos[agt1Idx][i]}{pos[agt2Idx][j]}")
                        resolveCollision(pos, paths, indicies, agt1Idx, agt2Idx, i, j)

                indicies[agt1Idx] += 1

    fixLength(pos)

    return pos





def fixCollision(collisionType, pos, timeTable, iPos, time, agtIdx):
    tb = 0 # traceback
    agtPos = iPos
    if collisionType == "col":
        agents1 = timeTable[iPos, time]
        pos1 = pos[agtIdx][time]
        
        # TODO Fix collision for agt 1

    elif collisionType == "fcol":
        agents2 = timeTable[iPos, time + 1]
        pos2 = pos[agtIdx][time + 1]
        
        # TODO Fix future collision for agt 1 by moving agt2

    elif collisionType == "swap":
        agents1 = timeTable[agtPos, time + tb]
        pos1 = pos[agtIdx][time + tb]
        agents2 = timeTable[agtPos, time + 1 + tb]
        pos2 = pos[agtIdx][time + 1 + tb]

        while checkCollision(pos, timeTable, agtPos, time, agtIdx) is not None:
            tb += 1
            agtPos = pos[agtIdx][time + tb]
            #println(f"{agtPos}")
        
            if type(agtPos) == list:
                pass
            else:
                if (agtPos, time + tb) in timeTable and (agtPos, time + tb + 1) in timeTable:
                    agents1 = timeTable[agtPos, time + tb]
                    pos1 = pos[agtIdx][time + tb]
                    agents2 = timeTable[agtPos, time + 1 + tb]
                    pos2 = pos[agtIdx][time + 1 + tb]
                else:
                    pos1 = pos[agtIdx][time + tb]
                    pos2 = pos[agtIdx][time + 1 + tb]
                    break
            
        # println(f"{(pos1,pos2,time+tb)}")
            
        # TODO fix swap between 2 agents

def checkCollision(pos, timeTable, iPos, time, agtIdx):

    if (iPos, time) in timeTable:
        agents1 = timeTable[iPos, time]
        pos1 = pos[agtIdx][time]

        if len(agents1) > 1:
            println(f"collision! at {pos1} with   time {time} and agent {agents1}")
            return "col"  # collision
        elif (iPos, time + 1) in timeTable:
            agents2 = timeTable[iPos, time + 1]
            pos2 = pos[agtIdx][time + 1]
            if len(agents2) > 1:
                println(f"collision! at {pos2} with   time {time+1} and agent {agents2}")
                return "fcol"  # future collision
            elif agents2 != agents1:
                println(f"swap! between {pos1} & {pos2} with time {time} & {time+1} and agent {agents1} & {agents2}")
                return "swap"  # swap between agents

    return None


def findAndResolveCollision(pos, paths, timeTable):
    println(pos)
    println(timeTable)
    
    deadlock = False
    # TODO remove tb from indicies or find another way to.
    # TODO hash with position as key, and the time this position is occupied
    # TODO if no positions are available at the traceback (out of bounds) explore nearby tiles
    while not deadlock:
        deadlock = True
        for agtIdx in range(len(paths)):
            for time in range(len(pos[agtIdx]) - 1):
                agtPos = pos[agtIdx][time]
                if type(agtPos) == list:
                    for iPos in agtPos:
                        # TODO fix list collision (Moving boxes)
                        collisionType = checkCollision(pos, timeTable, iPos, time, agtIdx)
                        #println(f"agt {timeTable[iPos, time]} occupies {iPos} at   time {time}")
                        pass 
                else:
                    iPos = agtPos
                    # println(f"agt {timeTable[iPos, time]} occupies {iPos} at   time {time}")
                    collisionType = checkCollision(pos, timeTable, iPos, time, agtIdx)
                    # if collisionType is not None:
                    #     fixCollision(collisionType, pos, timeTable, iPos, time, agtIdx)
                    #     pass
               # if len(timeTable[agtPos,time]) > 1:
                #     println(f"collision! at {pos[agtIdx][time]} with time {time} and agent {agtIdx}")
                #     #println(f"collision! at {pos[agtIdx][time]}")
                # elif len(pos[agtIdx][time + 1]) > 1:
                #     println(f"collision! at {pos[agtIdx][time + 1]} time+1")
                
            # if True:
            #     indexChanged = True
            #     for agt2Idx in range(agt1Idx, len(paths)):
            #         if agt2Idx == agt1Idx:
            #             continue
            #         j = indicies[agt2Idx]
            #         cond1 = [pos, agt1Idx, i, agt2Idx, j]
            #         cond2 = [pos, agt1Idx, i, agt2Idx, j + 1]
            #         if isCollision(*cond1) or isCollision(
            #             *cond2
            #         ):  # occupiedList[agt2Idx]:
            #             # TODO take boxes into account, this is probably why you get tuple integer problems
            #             # println(f"Collision between agents! at: {pos[agt1Idx][i]}{pos[agt2Idx][j]}")
            #             resolveCollision(pos, paths, indicies, agt1Idx, agt2Idx, i, j)

            #     indicies[agt1Idx] += 1

    # fixLength(pos)

    return pos


def isCollision(pos, agt1Idx, i, agt2Idx, j):

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
