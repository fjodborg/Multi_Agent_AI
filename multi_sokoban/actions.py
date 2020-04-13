"""Define literals and actions schemas for the muli-PDDL framework."""
import copy
import operator

import numpy as np


class Literals:
    def __init__(self, parent: "Literals" = None):
        # initializes the literals
        if parent is None:
            # if no parent is present!
            self.dir = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}
            self.agents = {}  # hashtable
            self.goals = {}  # hashtable
            self.boxes = {}  # hashtable
            self.prevState = None
            self.actionPerformed = None
            self.g = 0
            self.h = None
            self.explored = set()
        else:
            # if a parent is present!
            self.dir = parent.dir  # rigid
            self.goals = parent.goals  # rigid
            self.agents = copy.deepcopy(parent.agents)
            self.boxes = copy.deepcopy(parent.boxes)
            self.map = copy.deepcopy(parent.map)
            self.prevState = parent  # reference to previous state
            self.actionPerformed = None  # gets defined when action is chosen
            self.g = copy.deepcopy(parent.g) + 1
            self.h = None
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

    def addGoal(self, key, pos):
        # Adds a goal to a hashtable
        # key is a letter
        key = key.lower()
        if key not in self.goals:
            self.goals[key] = [pos]
        else:
            self.goals[key].append(pos)

    def addBox(self, key, pos, color="c"):
        # Adds a box to the map and to a hashtable
        # key is a letter
        key = key.upper()
        self.map[pos] = key
        if key not in self.boxes:
            self.boxes[key] = [[pos, color]]
        else:
            self.boxes[key].append([pos, color])

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


class StateInit(Literals):
    def __init__(self, parent: "Literals" = None):
        # initializes the state
        # it is (row, column) and not (x, y)
        super().__init__(parent)

    def getAgentByKey(self, key):
        # same as getPos, just for all agents with the given key
        if key in self.agents:
            return self.agents[key]
        else:
            return None

    def getBoxesByKey(self, key):
        # same as getPos, just for all Boxes with the given key
        if key in self.boxes:
            return self.boxes[key]
        else:
            return None

    def getGoalsByKey(self, key):
        # same as getPos, just for all Goal with the given key
        if key in self.goals:
            return self.goals[key]
        else:
            return None

    def getGoals(self):
        # returns all the keys
        return list(self.goals.keys())

    def __AddPos(self, agtfrom, agtdir):
        # simply adds two positions together
        return tuple(map(operator.add, agtfrom, self.dir[agtdir]))

    def __MovePrec(self, agt, agtdir):
        # returns the movement parameters if the preconditions are met
        # otherwise it returns 0
        agtfrom = self.getPos(self.agents, agt)
        if agtfrom is None:
            print("agent", agt, "does not exist")
            return None
        if agtdir not in self.dir:
            print("Direction", agtdir, "does not exist")
            return None
        agtto = self.__AddPos(agtfrom, agtdir)
        if self.Free(agtto):
            return (agt, agtfrom, agtto)
        else:
            print("Pos " + str(agtto) + " (row,col) is not free")
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
            print("agent", agt, "does not exist")
            return None
        if boxfrom is None:
            print("Box", boxkey, "does not exist")
            return None
        if boxdir not in self.dir:
            print("Direction", boxdir, "does not exist")
            return None
        if self.Neighbour(agtfrom, boxfrom) != 1:
            print("agent", agt, "and box", boxkey, "are not neighbors")
            return None

        boxto = self.__AddPos(boxfrom, boxdir)
        if self.Free(boxto):
            return (agt, boxkey, agtfrom, boxfrom, boxto, i)
        else:
            print("Pos " + str(boxto) + " (row,col) is not free")
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
            print("agent", agt, "does not exist")
            return None
        if boxfrom is None:
            print("Box", boxkey, "does not exist")
            return None
        if agtdir not in self.dir:
            print("Direction", agtdir, "does not exist")
            return None
        if self.Neighbour(agtfrom, boxfrom) != 1:
            print("agent", agt, "and box", boxkey, "are not neighbors")
            return None

        agtto = self.__AddPos(agtfrom, agtdir)
        if self.Free(agtto):
            return (agt, boxkey, agtfrom, agtto, boxfrom, i)
        else:
            print("Pos " + str(agtto) + " (row,col) is not free")
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
        else:
            del self

    def isGoalState(self):
        # checks if the state is a goal state
        keys = self.getGoals()
        for key in keys:
            goals = self.getGoalsByKey(key)
            for pos in goals:
                if self.map[pos] != key.upper():
                    return False
        return True

    def bestPath(self):
        # function returns the list of actions used to reach the state
        path = []
        state = self
        while state.actionPerformed is not None:
            path.append(state.actionPerformed)
            state = state.prevState
        # Reverse the order
        return path[::-1]

    def explore(self):
        # Explores unexplroed states and returns a list of children
        children = []

        # Loop iterales through every possible action
        for direction in self.dir:
            for agtkey in self.agents:

                # Checks a Move action if it is possible it is appended to the the children
                actionParams = self.__MovePrec(agtkey, direction)
                if actionParams is not None:
                    child = StateInit(self)
                    child.actionPerformed = ["Move", actionParams]
                    child.__MoveEffect(*actionParams)
                    child.__addToExplored(children)

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
                            # Checks a Push action if it is possible it is appended to the the children
                            actionParams = self.__PushPrec(agtkey, boxkey, direction, i)
                            if actionParams is not None:
                                child = StateInit(self)
                                child.actionPerformed = ["Push", actionParams]
                                child.__PushEffect(*actionParams)
                                child.__addToExplored(children)

        for agtkey in self.agents:
            # TODO make a noop function
            child = StateInit(self)
            child.actionPerformed = ["Noop", None]
            child.__addToExplored(children)

        return children
