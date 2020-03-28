"""Define literals and actions schemas for the muli-PDDL framework."""
import numpy as np
from abc import ABC, abstractmethod
import operator


class Literals(ABC):
    def __init__(self):
        self.agents = {}  # hashtable
        self.goals = {}  # hashtable
        self.boxes = {}  # hashtable
        super().__init__()

    def addMap(self, map2):
        self.map = np.array(map2)

    def addAgent(self, key, value):
        # key is color
        if key not in self.agents:
            self.agents[key] = [value]
        else:
            # if key already exists, make the value a list
            self.agents[key].append(value)

    def addGoal(self, key, value):
        # key is letter
        if key not in self.goals:
            self.goals[key] = [value]
        else:
            # if key already exists, make the value a list
            self.goals[key].append(value)

    def addBox(self, key1, key2, value):
        # key is (letter, color)
        key = (key1, key2)
        if key not in self.boxes:
            self.boxes[key] = [value]
        else:
            # if key already exists, make the value a list
            self.boxes[key].append(value)

    def GetPos(self, objtype, obj, i=0):
        if obj in objtype:
            return objtype[obj][i]
        else:
            return None

    def SetPos(self, objtype, obj, pos, i=0):
        if type(objtype[obj][i]) == tuple:
            objtype[obj][i] = pos
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

    @abstractmethod
    def Move(self):
        pass

    def Push(self):
        pass

    def Pull(self):
        pass

    def Noop(self):
        pass


class Actions(Literals):
    def __init__(self):
        # it is (row, column) and not (x, y)
        self.dir = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}
        super().__init__()

    def AddPos(self, agtfrom, agtdir, i=0):
        return tuple(map(operator.add, agtfrom, self.dir[agtdir]))

    def Move(self, agt, agtdir):
        agtfrom = self.GetPos(self.agents, agt)
        if agtfrom is None:
            print("agent", agt, "does not exist")
            return None
        if agtdir not in self.dir:
            print("Direction", agtdir, "does not exist")
            return None
        agtto = self.AddPos(agtfrom, agtdir)
        if self.Free(agtto):
            self.SetPos(self.agents, agt, agtto)
            # maybe add it to the map and remove the old one?
            print("Agent " + agt + " is now at " + str(agtto) + " (row,col)")
            return True
        else:
            print("Pos " + str(agtto) + " (row,col) is not free")
            return None

    def Push(self, agt, boxid, boxcolor, boxdir, i=0):
        box = (boxid, boxcolor)
        agtfrom = self.GetPos(self.agents, agt)
        boxfrom = self.GetPos(self.boxes, box, i)
        if agtfrom is None:
            print("agent", agt, "does not exist")
            return None
        if boxfrom is None:
            print("Box", box, "does not exist")
            return None
        if boxdir not in self.dir:
            print("Direction", boxdir, "does not exist")
            return None
        if self.Neighbour(agtfrom, boxfrom) != 1:
            print("agent", agt, "and box", box, "are not neighbors")
            return None

        boxto = self.AddPos(boxfrom, boxdir, i)
        if self.Free(boxto):
            self.SetPos(self.agents, agt, boxfrom, i)
            self.SetPos(self.boxes, box, boxto, i)
            # maybe add it to the map and remove the old one?
            print("Agent " + agt + " is now at " + str(boxto) + " (row,col)")
            print("Box " + str(box) + " is now at " + str(boxfrom) + " (row,col)")
            return True
        else:
            print("Pos " + str(boxto) + " (row,col) is not free")
            return None

    def Pull(self, agt, boxid, boxcolor, agtdir, i=0):
        box = (boxid, boxcolor)
        agtfrom = self.GetPos(self.agents, agt)
        boxfrom = self.GetPos(self.boxes, box, i)
        if agtfrom is None:
            print("agent", agt, "does not exist")
            return None
        if boxfrom is None:
            print("Box", box, "does not exist")
            return None
        if agtdir not in self.dir:
            print("Direction", agtdir, "does not exist")
            return None
        if self.Neighbour(agtfrom, boxfrom) != 1:
            print("agent", agt, "and box", box, "are not neighbors")
            return None

        agtto = self.AddPos(agtfrom, agtdir, i)
        if self.Free(agtto):
            self.SetPos(self.agents, agt, agtto, i)
            self.SetPos(self.boxes, box, agtfrom, i)
            # maybe add it to the map and remove the old one?
            print("Agent " + agt + " is now at " + str(agtto) + " (row,col)")
            print("Box " + str(box) + " is now at " + str(agtfrom) + " (row,col)")
            return True
        else:
            print("Pos " + str(agtto) + " (row,col) is not free")
            return None

    def Noop(self, agt):
        pass
