"""Define literals and actions schemas for the muli-PDDL framework."""
import copy
import operator
from typing import Dict

import numpy as np

from utils import println


class Literals:
    def __init__(self, parent: "Literals" = None):
        # initializes the literals
        if parent is None:
            # if no parent is present!
            self.dir = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}
            self.deltaPos = {
                (-1, 0): "N",
                (0, 1): "E",
                (1, 0): "S",
                (0, -1): "W",
            }
            self.goals = {}  # hashtable
            self.agentColor = {}  # hashtable
            self.agents = {}  # hashtable
            self.boxes = {}  # hashtable
            self.prevState = None
            self.actionPerformed = None
            self.g = 0
            self.t = 0
            self.h = None
            self.f = None
            self.explored = set()
        else:
            # if a parent is present!
            self.dir = parent.dir  # rigid
            self.deltaPos = parent.deltaPos  # rigid
            self.goals = parent.goals  # rigid
            self.agentColor = parent.agentColor  # rigid
            self.agents = copy.deepcopy(parent.agents)
            self.boxes = copy.deepcopy(parent.boxes)
            self.map = copy.deepcopy(parent.map)
            self.prevState = parent  # reference to previous state
            self.actionPerformed = None  # gets defined when action is chosen
            self.g = copy.deepcopy(parent.g) + 1
            self.h = None
            self.f = None
            self.t = parent.t + 1
            self.explored = parent.explored
        super().__init__()

    def addMap(self, map2):
        # initialized a map with only walls
        self.map = np.array(map2)

    def addAgent(self, key, pos, color="c"):
        # Adds an agent to the map and to a hashtable
        # key is the agent number and color is the color of the agent
        self.map[pos] = key
        self.agents[key] = [[pos, color]]

        # This is only used to get easy access to agents by color
        if color not in self.agentColor:
            self.agentColor[color] = [key]
        else:
            self.agentColor[color].append(key)

    def addGoal(self, key, pos, color=None):
        # Adds a goal to a hashtable
        # key is a letter
        key = key.lower()
        if key not in self.goals:
            self.goals[key] = [[pos, color]]
        else:
            self.goals[key].append([pos, color])

    def addBox(self, key, pos, color="c"):
        # Adds a box to the map and to a hashtable
        # key is a letter
        key = key.upper()
        self.map[pos] = key
        if key not in self.boxes:
            self.boxes[key] = [[pos, color]]
        else:
            self.boxes[key].append([pos, color])

    def forget_exploration(self):
        """Remove explored nodes."""
        self.explored = set()

    def deleteAgent(self, external_key):
        """Delete from `agents`, the `map` and `agent_color`."""
        pos = self.getPos(self.agents, external_key)
        del self.agents[external_key]
        self.map[pos] = " "
        for color in self.agentColor:
            if external_key in self.agentColor[color]:
                to_del = self.agentColor[color].index(external_key)
                del self.agentColor[color][to_del]

    def deleteBox(self, external_key):
        pos = self.getPos(self.boxes, external_key)
        del self.boxes[external_key]
        self.map[pos] = " "

    def deleteGoal(self, external_key):
        del self.goals[external_key]

    def keepJustAgent(self, external_key):
        ext_agents = list(self.agents.keys())
        for external_agent in ext_agents:
            if external_agent != external_key:
                self.deleteAgent(external_agent)

    def keepJustGoal(self, external_key):
        ext_goals = list(self.goals.keys())
        for external_goal in ext_goals:
            if external_goal != external_key:
                self.deleteGoal(external_goal)

    def keepJustBox(self, external_key):
        boxes = list(self.boxes.keys())
        for external_agent in boxes:
            if external_agent != external_key:
                self.deleteBox(external_agent)

    def getPos(self, objtype, obj, i=0):
        # gets the position of an object getPos(objecttype, the key, the index (if multiple))
        # returns None if not in hashtable
        if obj in objtype:
            return objtype[obj][i][0]
        else:
            return None

    def setPos(self, objtype, obj, pos, i=0):
        # sets the position of an object
        # setPos(objecttype, the key, position, the index (if multiple))
        # returns None if not in hashtable
        if type(objtype[obj][i][0]) == tuple:
            objtype[obj][i][0] = pos
        else:
            return None

    def Free(self, pos):
        # checks if position in map is free
        # returns true if it is free and false otherwise
        if self.map[pos] == chr(32) or self.map[pos].islower():
            return True
        else:
            return False

    def Color(self, obj):
        pass

    def Neighbour(self, pos1, pos2):
        # Returns true if the 2 positions are neighbours, otherwise false
        if abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1:
            return True
        else:
            return False

    def __str__(self):
        # Debugging purposes
        return "\n".join(["".join(line) for line in self.map]) + f" t={self.t}"


class StateInit(Literals):
    def __init__(self, parent: "Literals" = None):
        # initializes the state
        # it is (row, column) and not (x, y)
        super().__init__(parent)

    def getAgentsByKey(self, key):
        # same as getPos, just for all agents with the given key
        # if key not in self.agents:
        #    return None
        return self.agents[key]

    def getAgentsByColor(self, color):
        # same as getPos, just for all agents with the given key
        return self.agentColor[color]

    def getBoxesByKey(self, key):
        key = key.upper()
        # same as getPos, just for all Boxes with the given key
        # if key not in self.boxes:
        #    return None
        return self.boxes[key]

    def getGoalsByKey(self, key):
        key = key.lower()
        # same as getPos, just for all Goal with the given key
        # if key not in self.goals:
        #    return None
        return self.goals[key]

    def getGoalKeys(self):
        # returns all the keys
        return list(self.goals.keys())

    def getAgentKeys(self):
        # returns all the keys
        return list(self.agents.keys())

    """def updateParentCost(self, total_cost):
        state = self.prevState
        i = 0
        while state is not None:
            i += 1
            state.h = total_cost + i
            state.f = state.g + state.h
            state = state.prevState"""

    def __addPos(self, agtfrom, agtdir):
        # simply adds two positions together
        return tuple(map(operator.add, agtfrom, self.dir[agtdir]))

    def __getDir(self, agtfrom, agtto):
        # returns the direction the agent moved
        dir = (agtto[0] - agtfrom[0], agtto[1] - agtfrom[1])
        return self.deltaPos[dir]

    def __MovePrec(self, agt, agtdir):
        # returns the movement parameters if the preconditions are met
        # otherwise it returns 0
        agtfrom = self.getPos(self.agents, agt)
        if agtfrom is None:
            # # # print("agent", agt, "does not exist")
            return None
        if agtdir not in self.dir:
            # # # print("Direction", agtdir, "does not exist")
            return None
        agtto = self.__addPos(agtfrom, agtdir)
        if self.Free(agtto):
            return (agt, agtfrom, agtto)
        else:
            # # # print("Pos " + str(agtto) + " (row,col) is not free")
            return None

    def __MoveEffect(self, agt, agtfrom, agtto):
        # Moves the object with the given parameters
        # Does not check preconditions
        self.setPos(self.agents, agt, agtto)
        self.map[agtfrom] = chr(32)
        self.map[agtto] = agt
        # print("Agent " + agt + " is now at " + str(agtto) + " (row,col)")
        return True

    def Move(self, agt, agtdir):
        # moves the object in the given direction, it checks the precondition and does the movemnt
        actionParams = self.__MovePrec(agt, agtdir)
        if actionParams is not None:
            return self.__MoveEffect(*actionParams)
        else:
            return None

    def __PushPrec(self, agt, boxkey, boxdir, i=0):
        # returns the movement parameters if the preconditions are met
        # otherwise it returns 0
        agtfrom = self.getPos(self.agents, agt)
        boxfrom = self.getPos(self.boxes, boxkey, i)
        if agtfrom is None:
            # # # print("agent", agt, "does not exist")
            return None
        if boxfrom is None:
            # # # print("Box", boxkey, "does not exist")
            return None
        if boxdir not in self.dir:
            # # # print("Direction", boxdir, "does not exist")
            return None
        if self.Neighbour(agtfrom, boxfrom) != 1:
            # # # print("agent", agt, "and box", boxkey, "are not neighbors")
            return None

        boxto = self.__addPos(boxfrom, boxdir)
        if self.Free(boxto):
            return (agt, boxkey, agtfrom, boxfrom, boxto, i)
        else:
            # # # print("Pos " + str(boxto) + " (row,col) is not free")
            return None

    def __PushEffect(self, agt, boxkey, agtfrom, boxfrom, boxto, i):
        # Moves the objects with the given parameters
        # Does not check preconditions
        self.setPos(self.agents, agt, boxfrom, 0)  # agents are unique thus 0
        self.setPos(self.boxes, boxkey, boxto, i)
        self.map[agtfrom] = chr(32)
        self.map[boxfrom] = agt
        self.map[boxto] = boxkey
        # print("Agent " + agt + " is now at " + str(boxto) + " (row,col)")
        # print("Box " + str(box) + " is now at " + str(boxfrom) + " (row,col)")
        return True

    def Push(self, agt, boxkey, boxdir, i):
        # moves the objects in the given direction, it checks the precondition and does the movemnt
        actionParams = self.__PushPrec(agt, boxkey, boxdir, i)
        if actionParams is not None:
            return self.__PushEffect(*actionParams)
        else:
            return None

    def __PullPrec(self, agt, boxkey, agtdir, i=0):
        # Moves the object with the given parameters
        # Does not check preconditions
        agtfrom = self.getPos(self.agents, agt)
        boxfrom = self.getPos(self.boxes, boxkey, i)
        if agtfrom is None:
            # # # print("agent", agt, "does not exist")
            return None
        if boxfrom is None:
            # # # print("Box", boxkey, "does not exist")
            return None
        if agtdir not in self.dir:
            # # # print("Direction", agtdir, "does not exist")
            return None
        if self.Neighbour(agtfrom, boxfrom) != 1:
            # # # print("agent", agt, "and box", boxkey, "are not neighbors")
            return None

        agtto = self.__addPos(agtfrom, agtdir)
        if self.Free(agtto):
            return (agt, boxkey, agtfrom, agtto, boxfrom, i)
        else:
            # # # print("Pos " + str(agtto) + " (row,col) is not free")
            return None

    def __PullEffect(self, agt, boxkey, agtfrom, agtto, boxfrom, i):
        # Moves the objects with the given parameters
        # Does not check preconditions
        self.setPos(self.agents, agt, agtto, 0)  # agents are unique thus 0
        self.setPos(self.boxes, boxkey, agtfrom, i)
        self.map[boxfrom] = chr(32)
        self.map[agtfrom] = boxkey
        self.map[agtto] = agt
        # print("Agent " + agt + " is now at " + str(agtto) + " (row,col)")
        # print("Box " + str(box) + " is now at " + str(agtfrom) + " (row,col)")
        return True

    def Pull(self, agt, boxkey, boxdir, i):
        # moves the objects in the given direction, it checks the precondition and does the movemnt
        actionParams = self.__PullPrec(agt, boxkey, boxdir, i)
        if actionParams is not None:
            return self.__PullEffect(*actionParams)
        else:
            return None

    def minimalRep(self):
        # returns the minimal representation of the states
        return str([self.agents, self.boxes])

    def isExplored(self):
        # returns true if the state is explored
        return self.minimalRep() in self.explored

    def __addToExplored(self, children):
        # adds the state to the explored list
        if not self.isExplored():
            self.explored.add(self.minimalRep())
            children.append(self)

    def isGoalState(self):
        # checks if the state is a goal state
        keys = self.getGoalKeys()
        for key in keys:
            goals = self.getGoalsByKey(key)
            for pos, color in goals:
                if self.map[pos] != key.upper():
                    return False
        return True

    def bestPath(self, format=0, index=0):
        # function returns the list of actions used to reach the state
        path = []
        state = copy.deepcopy(self)
        if format == 1:
            # format used by actions
            while state.actionPerformed is not None:
                path.append(state.actionPerformed)
                state = state.prevState
        elif isinstance(format, str):
            # trace back an object
            looking_for = format
            obj_group = "agents" if format.isnumeric() else "boxes"

            while state.actionPerformed is not None:
                path.append(
                    [
                        state.t,
                        state.getPos(getattr(state, obj_group), looking_for, index),
                    ]
                )
                state = state.prevState
        else:
            # format used by server
            while state.actionPerformed is not None:
                # print(state.actionPerformed, state.actionPerformed[0])
                cmd = state.actionPerformed[0]
                if cmd == "Push":  # (agtfrom, boxfrom, boxto)
                    parm1 = self.__getDir(
                        state.actionPerformed[1][2], state.actionPerformed[1][3]
                    )
                    parm2 = self.__getDir(
                        state.actionPerformed[1][3], state.actionPerformed[1][4]
                    )
                    cmd = f"Push({parm1},{parm2})"
                elif cmd == "Pull":  # (agtfrom, agtto, boxfrom)
                    parm1 = self.__getDir(
                        state.actionPerformed[1][2], state.actionPerformed[1][3]
                    )
                    parm2 = self.__getDir(
                        state.actionPerformed[1][2], state.actionPerformed[1][4]
                    )
                    cmd = f"Pull({parm1},{parm2})"
                elif cmd == "Move":
                    parm1 = self.__getDir(
                        state.actionPerformed[1][1], state.actionPerformed[1][2]
                    )
                    cmd = f"Move({parm1})"
                elif cmd == "NoOp":
                    cmd = "NoOp"

                path.append(cmd)
                state = state.prevState
        # Reverse the order
        return path[::-1]

    def explore(self):
        # Explores unexplroed states and returns a list of children
        children = []

        # Loop iterales through every possible action
        for direction in self.dir:
            for agtkey in self.agents:

                # TODO reformat these nested loops and if statements!

                # This can be perhaps be optimized by only looking at boxes at the
                # neighboring tiles of the agent
                for boxkey in self.boxes:
                    for i in range(len(self.boxes[boxkey])):

                        boxcolor = self.boxes[boxkey][i][1]

                        # [agent letter][agent number (0 since it is unique)][color]
                        if self.agents[agtkey][0][1] == boxcolor:
                            # Checks a pull action if it is possible it is appended to the the children
                            actionParams = self.__PullPrec(agtkey, boxkey, direction, i)
                            if actionParams is not None:
                                child = StateInit(self)
                                child.actionPerformed = ["Pull", actionParams]
                                child.__PullEffect(*actionParams)
                                child.__addToExplored(children)
                            actionParams = self.__PushPrec(agtkey, boxkey, direction, i)
                            if actionParams is not None:
                                child = StateInit(self)
                                child.actionPerformed = ["Push", actionParams]
                                child.__PushEffect(*actionParams)
                                child.__addToExplored(children)
                            # Checks a Push action if it is possible it is appended to the the children
                # Checks a Move action if it is possible it is appended to the the children
                actionParams = self.__MovePrec(agtkey, direction)
                if actionParams is not None:
                    child = StateInit(self)
                    child.actionPerformed = ["Move", actionParams]

                    child.__MoveEffect(*actionParams)
                    child.__addToExplored(children)

        for agtkey in self.agents:
            # TODO make a noop function
            child = StateInit(self)
            child.actionPerformed = ["NoOp", None]
            child.__addToExplored(children)

        return children


class StateConcurrent(StateInit):
    """Extend StateInit with concurrent literals."""

    def __init__(self, parent: StateInit = None, concurrent: Dict = None):
        """Initialize by adding a time table to the usual `StateInit`.

        Parameters
        ----------
        parent: StateInit
        concurrent: Dict
            Shared table that contains times where an object (box) in the
            environment has been changed by another agent:
                {t: {box: [(row, col), index], ...}, ...}

        """
        super().__init__(parent)
        self.concurrent = concurrent if concurrent else parent.concurrent
        self.hunt_ghost()

    def __NoOpPrec(self):
        """Evaluate precondition for NoOp.

        Agent can stay at his position without doing anything.
        """
        return self.__WaitPrec_t(self.t) and self.__WaitPrec_t(self.t+1)

    def __WaitPrec_t(self, t):
        if t in self.concurrent:
            joint_concurrent = self.concurrent[t]
            # a state that it is being solved is guaranteed to have only one agent
            agent_pos = self.getPos(self.agents, list(self.agents.keys())[0])
            for pos, _ in joint_concurrent.values():
                if pos is None:
                    continue
                if agent_pos[0] == pos[0] and agent_pos[1] == pos[1]:
                    return False
        return True

    def __ConcurrentPrec(self):
        """Evaluate precondition for concurrent changes of the world.

        Something has changed given a concurrent action by another agent.
        """
        return self.t in self.concurrent

    def __ConcurrentEffect(self, t):
        """Modify environment according to concurrent actions at time `t`."""
        joint_concurrent = self.concurrent[t]
        for obj_key in joint_concurrent:
            pos, index = list(joint_concurrent[obj_key])
            obj_group = "agents" if obj_key.isnumeric() else "boxes"
            if obj_group == "boxes":
                prev_pos = self.getPos(getattr(self, obj_group), obj_key, index)
                self.setPos(getattr(self, obj_group), obj_key, pos, index)
                # introduce a ghost box which will be removed on child nodes
                self.map[prev_pos[0], prev_pos[1]] = "Ñ"
                if pos is not None:
                    self.map[pos[0], pos[1]] = obj_key
            else:
                # agents don't leave ghosts behind and are not in the StateInit
                self.map[self.map == obj_key] = "Ñ"
                self.map[pos[0], pos[1]] = obj_key
        return True

    def hunt_ghost(self):
        """Remove ghosted positions put by a Councurent Effect."""
        self.map[self.map == "Ñ"] = " "

    def explore(self):
        """Explore with 'NoOp's.

        The Preconditions to a NoOp is that the environment was changed
        by another agent; i.e., there is an entry in `self.concurrent`
        for the next time `self.t`. This ensures that agents just wait if the
        next state is new and applies the concurrent changes to all children.
        """
        children = []

        # Loop iterales through every possible action
        child_def = StateConcurrent(self)

        if child_def.__ConcurrentPrec():
            # apply concurrent effects to all children but also append
            # a NoOp children which just waits for the env to change
            # println("Applying NoOp")
            child_def.__ConcurrentEffect(child_def.t)
            if child_def.__NoOpPrec():
                child = copy.deepcopy(child_def)
                child.actionPerformed = ["NoOp", None]
                child._StateInit__addToExplored(children)

        for direction in self.dir:
            for agtkey in self.agents:

                # TODO reformat these nested loops and if statements!

                # This can be perhaps be optimized by only looking at boxes at
                # the neighboring tiles of the agent

                for boxkey in child_def.boxes:
                    for i in range(len(child_def.boxes[boxkey])):

                        boxcolor = child_def.boxes[boxkey][i][1]

                        # [agent letter][agent number (0 since it is unique)][color]
                        if child_def.agents[agtkey][0][1] == boxcolor:
                            # Checks a pull action if it is possible it is appended to the the children
                            actionParams = child_def._StateInit__PullPrec(
                                agtkey, boxkey, direction, i
                            )
                            if actionParams is not None:
                                child = copy.deepcopy(child_def)
                                child.actionPerformed = ["Pull", actionParams]
                                child._StateInit__PullEffect(*actionParams)
                                child._StateInit__addToExplored(children)
                            # Checks a Push action if it is possible it is appended to the the children
                            actionParams = child_def._StateInit__PushPrec(
                                agtkey, boxkey, direction, i
                            )
                            if actionParams is not None:
                                child = copy.deepcopy(child_def)
                                child.actionPerformed = ["Push", actionParams]
                                child._StateInit__PushEffect(*actionParams)
                                child._StateInit__addToExplored(children)
                # Checks a Move action if it is possible it is appended to the the children
                actionParams = child_def._StateInit__MovePrec(agtkey, direction)
                if actionParams is not None:
                    child = copy.deepcopy(child_def)
                    child.actionPerformed = ["Move", actionParams]

                    child._StateInit__MoveEffect(*actionParams)
                    child._StateInit__addToExplored(children)

        return children

    def AdvancePrec(self):
        """Is there some concurrent change in the future.

        It will be called by by strategy.
        """
        future = [t for t in self.concurrent if t > self.t]
        if future:
            return min(future)
        return False

    def advance(self) -> StateInit:
        """Advance in time until the environment is changed by other agent."""
        next_time = self.AdvancePrec()
        if not next_time:
            return self
        future_self = self
        while next_time > future_self.t:
            println(future_self)
            future_self = StateConcurrent(future_self)
            future_self.actionPerformed = ["NoOp", None]
        return future_self
