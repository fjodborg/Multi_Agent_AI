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


def findAndResolveCollision2(pos, paths):
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


def addToHash(timeTable, pos, time, agt):
    if (pos, time) in timeTable:
        timeTable[pos, time].append(agt)
    else:
        timeTable[pos, time] = [agt]


def checkCollision(pos, timeTable, iPos, time, agtIdx):
    agt1 = timeTable[iPos, time]
    pos1 = pos[agtIdx][time]
    #println(f"{timeTableAgts},{len(timeTableAgts)}")
    if len(timeTable[iPos, time]) > 1:
        println(f"collision! at {pos1} with   time {time} and agent {agt1}")
    elif (iPos, time + 1) in timeTable:
        pos2 = pos[agtIdx][time + 1]
        agt2 = timeTable[iPos, time + 1]
        if len(agt2) > 1:
            # TODO handle if next position (time+1) has a collision
            println(f"collision! at {pos2} with   time {time+1} and agent {agt2}")
        elif agt2 != agt1:
            println(f"swap! between {pos1} & {pos2} with time {time} & {time+1} and agent {agt1} & {agt2}")
    

def findAndResolveCollision(pos, paths):
    timeTable = {}
    for agtIdx in range(len(paths)):
        for time in range(len(pos[agtIdx])):
            posAtTime = pos[agtIdx][time]
            if type(posAtTime) == list:
                addToHash(timeTable, posAtTime[0], time, agtIdx)
                addToHash(timeTable, posAtTime[1], time, agtIdx)
            else:
                addToHash(timeTable, posAtTime, time, agtIdx)
    println(pos)      
    println(timeTable)
    
    indexChanged = True
    # TODO remove tb from indicies or find another way to.
    # TODO hash with position as key, and the time this position is occupied
    # TODO if no positions are available at the traceback (out of bounds) explore nearby tiles
    while indexChanged:
        indexChanged = False
        for agtIdx in range(len(paths)):
            for time in range(len(pos[agtIdx]) - 1):
                agtPos = pos[agtIdx][time]
                if type(agtPos) == list:
                    for iPos in agtPos:
                        checkCollision(pos, timeTable, iPos, time, agtIdx)
                        #println(f"agt {timeTable[iPos, time]} occupies {iPos} at   time {time}")
                        pass 
                else:
                    iPos = agtPos
                    # println(f"agt {timeTable[iPos, time]} occupies {iPos} at   time {time}")
                    checkCollision(pos, timeTable, iPos, time, agtIdx)

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
