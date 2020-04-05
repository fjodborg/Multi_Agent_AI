"""Define literals and actions schemas for the muli-PDDL framework."""
import numpy as np
import operator
import copy


class Literals:
    def __init__(self, parent: "Literals" = None):
        if parent is None:
            self.dir = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}
            self.agents = {}  # hashtable
            self.goals = {}  # hashtable
            self.boxes = {}  # hashtable
            self.prevState = None
            self.actionPerformed = None
            self.g = 0
            self.explored = set()
        else:
            self.dir = parent.dir  # rigid
            self.goals = parent.goals  # rigid
            self.agents = copy.deepcopy(parent.agents)
            self.boxes = copy.deepcopy(parent.boxes)
            self.map = copy.deepcopy(parent.map)
            self.prevState = parent  # reference to previous state
            self.actionPerformed = None
            self.g = copy.deepcopy(parent.g) + 1
            self.explored = parent.explored
        super().__init__()

    def addMap(self, map2):
        self.map = np.array(map2)

    def addAgent(self, key, value, color="c"):
        # key is number
        self.map[value] = key
        self.agents[key] = [[value, color]]

    def addGoal(self, key, value):
        # key is letter
        key = key.lower()
        if key not in self.goals:
            self.goals[key] = [[value]]
        else:
            self.goals[key].append([value])

    def addBox(self, key, value, color="c"):
        # key is (letter, color)
        key = key.upper()
        self.map[value] = key
        if key not in self.boxes:
            self.boxes[key] = [[value, color]]
        else:
            self.boxes[key].append([value, color])

    def getPos(self, objtype, obj, i=0):
        if obj in objtype:
            return objtype[obj][i][0]
        else:
            return None

    def setPos(self, objtype, obj, pos, i=0):
        if type(objtype[obj][i][0]) == tuple:
            objtype[obj][i][0] = pos
        else:
            return None

    def Free(self, pos):
        if self.map[pos] == chr(32) or self.map[pos].islower():
            return True
        else:
            return False

    def Color(self, obj):
        pass

    def Neighbour(self, pos1, pos2):
        if abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1:
            return True
        else:
            return False


class StateInit(Literals):
    def __init__(self, parent: "Literals" = None):
        # it is (row, column) and not (x, y)
        super().__init__(parent)

    def __AddPos(self, agtfrom, agtdir):
        return tuple(map(operator.add, agtfrom, self.dir[agtdir]))

    def __MovePrec(self, agt, agtdir):
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
        self.setPos(self.agents, agt, agtto)
        self.map[agtfrom] = chr(32)
        self.map[agtto] = agt
        # print("Agent " + agt + " is now at " + str(agtto) + " (row,col)")
        return True

    def Move(self, agt, agtdir):
        actionParams = self.__MovePrec(agt, agtdir)
        if actionParams is not None:
            return self.__MoveEffect(*actionParams)
        else:
            return None

    def __PushPrec(self, agt, boxkey, boxdir, i=0):
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
        self.setPos(self.agents, agt, boxfrom, 0)  # agents are unique thus 0
        self.setPos(self.boxes, boxkey, boxto, i)
        self.map[agtfrom] = chr(32)
        self.map[boxfrom] = agt
        self.map[boxto] = boxkey
        # print("Agent " + agt + " is now at " + str(boxto) + " (row,col)")
        # print("Box " + str(box) + " is now at " + str(boxfrom) + " (row,col)")
        return True

    def Push(self, agt, boxkey, boxdir, i):
        actionParams = self.__PushPrec(agt, boxkey, boxdir, i)
        if actionParams is not None:
            return self.__PushEffect(*actionParams)
        else:
            return None

    def __PullPrec(self, agt, boxkey, agtdir, i=0):
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
        self.setPos(self.agents, agt, agtto, 0)  # agents are unique thus 0
        self.setPos(self.boxes, boxkey, agtfrom, i)
        self.map[boxfrom] = chr(32)
        self.map[agtfrom] = boxkey
        self.map[agtto] = agt
        # print("Agent " + agt + " is now at " + str(agtto) + " (row,col)")
        # print("Box " + str(box) + " is now at " + str(agtfrom) + " (row,col)")
        return True

    def Pull(self, agt, boxkey, boxdir, i):
        actionParams = self.__PullPrec(agt, boxkey, boxdir, i)
        if actionParams is not None:
            return self.__PullEffect(*actionParams)
        else:
            return None

    def minimalRep(self):
        return str([self.agents, self.boxes])

    def isExplored(self):
        return self.minimalRep() in self.explored

    def __addTo(self, children):
        if not self.isExplored():
            self.explored.add(self.minimalRep())
            children.append(self)
        else:
            del self

    def bestPath(self):
        # function returns the list of actions used to reach the state
        path = []
        state = self
        while state.actionPerformed is not None:
            path.append(state.actionPerformed)
            state = state.prevState

        return path[::-1]

    def explore(self):
        # only explores unexplored states and returns a list of children
        children = []

        for direction in self.dir:
            for agtkey in self.agents:

                actionParams = self.__MovePrec(agtkey, direction)
                if actionParams is not None:
                    child = StateInit(self)
                    child.actionPerformed = ["Move", actionParams]
                    child.__MoveEffect(*actionParams)
                    child.__addTo(children)

                # TODO reformat these nested loops and if statements!

                # This can be perhaps be optimized by only looking at boxes at the
                # neighboring tiles of the agent
                for boxkey in self.boxes:
                    for i in range(len(self.boxes[boxkey])):

                        boxcolor = self.boxes[boxkey][i][1]

                        # [agent letter][agent number (0 since it is unique)][color]
                        if self.agents[agtkey][0][1] == boxcolor:
                            actionParams = self.__PullPrec(agtkey, boxkey, direction, i)
                            if actionParams is not None:
                                child = StateInit(self)
                                child.actionPerformed = ["Pull", actionParams]
                                child.__PullEffect(*actionParams)
                                child.__addTo(children)
                                if ["Pull", ("0", "B", (1, 2), (1, 1), (2, 2), 0)] == [
                                    "Pull",
                                    actionParams,
                                ]:
                                    print(
                                        "\n\n\n\n\n\nwtf\n\n\n\n\n",
                                        boxcolor,
                                        self.agents[agtkey][0][1],
                                    )

                            actionParams = self.__PushPrec(agtkey, boxkey, direction, i)
                            if actionParams is not None:
                                child = StateInit(self)
                                child.actionPerformed = ["Push", actionParams]
                                child.__PushEffect(*actionParams)
                                child.__addTo(children)

        for agtkey in self.agents:
            # TODO make a noop function
            child = StateInit(self)
            child.actionPerformed = ["Noop", None]
            child.__addTo(children)

        return children
