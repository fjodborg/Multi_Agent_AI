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
        #self.collisionType = None
        self.collidedAgents = None
        self.unsolvableReason = None
        self.isBound = False

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

        # Add initial positions for boxes
        for key in self.manager.top_problem.boxes:
            # println(self.manager.top_problem.boxes[key][0])
            boxPos, boxColor = self.manager.top_problem.boxes[key][0]
            self.addToHash(boxPos, 0, boxColor)

        agtColor = []
        for goal, val in self.manager.tasks.items():
            agtColor.append(list(val[0].agents.values())[0][0][1])
        #println(agtColor)

        for agtIdx in range(len(self.paths)):
            for time in range(len(self.pos[agtIdx])):
                posAtTime = self.pos[agtIdx][time]
                # println(f"{posAtTime}")
                if len(posAtTime) > 1:
                    # println("the value above is the color")
                    # TODO find a solution to figure out how to identify the box
                    self.addToHash(posAtTime[1], time, agtColor[agtIdx])  #
                self.addToHash(posAtTime[0], time, agtIdx)

        return None

    def isOutOfBound(self, time, agt2):
        if time >= len(self.pos[agt2]) or time < 0:
            # TODO find out why self.collidedAgents is None
            self.unsolvableReason = [self.collidedAgents, "out of bounds/no traceback"]
            println(f"Out of bounds for agent {agt2} at time {time}/{len(self.pos[agt2])-1}")
            return True
        else: 
            self.unsolvableReason = None
        return False

    def checkTailingPart(self, agtA, agtB, posB, timeA):
        if self.isOutOfBound(timeA, agtA):
            self.isBound = True
            return None
        else:
            agtAPosA = self.pos[agtA][timeA]
            for posA in agtAPosA:
                if posB == posA:
                    self.collidedAgents = [agtA, agtB, timeA]
                    println(
                        f"agt {agtA} is tailing agt {agtB} at {posA} at time {[timeA]} "
                    )
                    return True
        return False

    def checkTailing(self, agt1, agt2, pos12, pos22, time):
        if type(time) == list:
            time1 = time[0] + 1
            time2 = time[1] + 1
        else:
            time1 = time + 1
            time2 = time + 1
        
        self.checkTailingPart(agt1, agt2, pos22, time1)

        if (self.isOutOfBound(time2, agt2) and self.isBound):
            return None
        else:
            self.checkTailingPart(agt2, agt1, pos12, time2)
            self.isBound = False
            return True
        return None

    def checkSwap(self, agt1, agt2, pos12, pos22, time):
        if type(time) == list:
            time1 = time[0] + 1
            time2 = time[1] + 1
        else:
            time1 = time + 1
            time2 = time + 1

        swap = False
        #println(time)
        if self.isOutOfBound(time1, agt1):
            self.isBound = True
            return None
        agt1Pos = self.pos[agt1][time1]
        for pos11 in agt1Pos:
            if pos22 == pos11:
                swap = True
                break

        if self.isOutOfBound(time2, agt2):
            self.isBound = True
            return None
        agt2Pos = self.pos[agt2][time2]
        for pos21 in agt2Pos:
            if pos12 == pos21 and swap:
                self.collidedAgents = [agt1, agt2, time1, time2]
                println(
                    f"swap! between {pos21} & {pos22} with time {[time1,time2]} and agent {agt1} & {agt2}"
                )
                return True
        return None

    def checkCollision(self, agt1, agt2, pos1, pos2, time):
        if pos1 == pos2:
            self.collidedAgents = [agt1, agt2, time, time]
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
                if self.isOutOfBound(time, agt2):
                    return None
                agt2Pos = self.pos[agt2][time]
                for pos2 in agt2Pos:
                    self.checkCollision(agt1, agt2, pos1, pos2, time)
                    self.checkSwap(agt1, agt2, pos1, pos2, time)
                    self.checkTailing(agt1, agt2, pos1, pos2, time)
                    if self.collidedAgents:
                        return True
                    if self.isBound: # is assigned inside swap and tail
                        return None
            else:
                continue
            break
        return False

   
    def fixLength(self):
        lengths = [len(self.pos[agt]) for agt in range(len(self.pos))]
        longest = max(lengths)
        shortest = min(lengths)
        #println(longest)
        #println(shortest)
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

    def tracebackCollision(self, collisionTime):
        # TODO take into account if there is multiple agents
        # TODO if out of bounds or no solution found return a new value
        #println(self.collidedAgents)
        agt1 = self.collidedAgents[1]
        agt2 = self.collidedAgents[0]
        time2 = collisionTime + 1
        self.traceback = 0
        println("Traceback collision from now on:")
        for time1 in range(collisionTime, len(self.pos[agt1])):
            time2 -= 1
            self.traceback += 1

            obj1Pos = self.pos[agt1][time1]
            obj2Pos = self.pos[agt2][time2]
            collision = False

            for pos1 in obj1Pos:
                for pos2 in obj2Pos:
                    if self.checkCollision(agt1, agt2, pos1, pos2, [time1, time2]):
                        collision = True
                        break
                    agentsSwaped = self.checkSwap(agt1, agt2, pos1, pos2, [time1, time2])
                    if agentsSwaped:
                        if not self.isBound:
                            collision = True
                            break
                        println("swap was bounded, trying to look for tailing to be sure")
                    tailingAgt = self.checkTailing(agt1, agt2, pos1, pos2, [time1, time2])
                    if tailingAgt:
                        if not self.isBound:
                            collision = True
                            break
                        else:
                            return None, None
                else: 
                    continue
                break  # if collision is True
            else:  
                break  # if collision is false
        
        self.traceback -= 1

        println("Traceback found")
        return time2, agt2  # the last one was not a a collision

    def fixCollision(self, collisionTime):
        backwardTime, agt = self.tracebackCollision(collisionTime)
        if backwardTime is None:
            self.traceback = 0
            return None
        elif backwardTime < 0:
            backwardTime = 0
        
        for i in range(self.traceback*2):
            # Maybe remove this line, i don't think we need it
            # println((i, agt, backwardTime, self.pos[agt][backwardTime], ))
            self.pos[agt].insert(backwardTime, self.pos[agt][backwardTime])
        
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
        self.unsolvableReason = None
        # TODO remove tb from indicies or find another way to.
        # TODO hash with position as key, and the time this position is occupied
        # TODO if no positions are available at the traceback (out of bounds) explore nearby tiles
        while not deadlock:
            
            deadlock = True
            for agt1 in range(len(self.paths)):
                # timeTable = self.manager.generateHash(self.pos, [paths])
                for time in range(len(self.pos[agt1]) - 1):
                    self.traceback = 0
                    self.collidedAgents = None
                    collisionType = self.findCollidingAgt(agt1, time)
                    
                    if self.collidedAgents is not None:
                        println((collisionType, self.collidedAgents))
                        if self.fixCollision(time) is not None:
                            if self.unsolvableReason is not None:
                                deadlock = False
                            break
                    elif self.unsolvableReason is not None:
                        break
            self.fixLength()

        if self.unsolvableReason is not None:
            println(f"unsolveable due to: {self.unsolvableReason}")
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
