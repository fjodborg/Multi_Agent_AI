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

    def addBox(self, key, value):
        # key is (letter, color)
        if key not in self.boxes:
            self.boxes[key] = [value]
        else:
            # if key already exists, make the value a list
            self.boxes[key].append(value)

    def GetPos(self, objtype, obj):
        if obj in objtype:
            return objtype[obj]
        else:
            return None

    def SetPos(self, objtype, obj, pos, i):
        objtype[obj][i] = pos

    def GaolAt(self, obj, pos):
        pass

    def BoxAt(self, obj, pos):
        pass

    def Free(self, pos):
        return self.map[pos]

    def Color(self, obj):
        pass

    def Neighbour(self, pos1, pos2):
        pass

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
        return tuple(map(operator.add, agtfrom[i], self.dir[agtdir]))

    def Move(self, agt, agtdir, i=0):
        agtfrom = self.GetPos(self.agents, agt)
        if agtfrom is None:
            print("agent", agt, "does not exist")
            return None
        if agtdir not in self.dir:
            print("Direction", agtdir, "does not exist")
            return None
        # TODO figure something out about having two ai's of the same type
        # right now we assume one 1 ai of each type [look at variable i]
        # if we can confirm that there only is one of each type, remove [i]
        # in Agent, the line below and in the AddAgent method
        # aka agtfrom[i] becomes agtfrom since agtfrom isn't a list anymore
        agtto = self.AddPos(agtfrom, agtdir, i)
        if self.Free(agtto) == chr(32):
            self.SetPos(self.agents, agt, agtto, i)
            return "Agent " + agt + " is now at " + str(agtto) + " (row,col)"
        else:
            return "Pos " + str(agtto) + " (row,col) is not free"

    def Push(self, agt, box, boxdir):
        self.Free(boxto)
        self.Neighbour(agtfrom, boxfrom)
        self.Neighbour(boxfrom, boxto)
        self.BoxAt(box, agtfrom)
        self.AgentAt(agt, agtfrom)

    def Pull(agt, agtfrom, agtto, box, boxfrom):
        self.Free(agtto)
        self.Neighbour(agtto, boxfrom)
        self.Neighbour(boxfrom, agtfrom)
        self.BoxAt(box, agtfrom)
        self.AgentAt(agt, agtfrom)

    def Noop(self, agt):
        pass


def test():
    # remember to make walls, otherwise it isn't bound to the matrix!
    state = Actions()
    state.addMap(
        [
            ["+", "+", "+", "+", "+"],
            ["+", chr(32), chr(32), chr(32), "+"],
            ["+", chr(32), chr(32), "+", "+"],
            ["+", "+", chr(32), chr(32), "+"],
            ["+", "+", "+", "+", "+"],
        ]
    )
    print(state.map)
    state.addAgent("b", (1, 1))  # key is color
    print(state.agents)
    print(state.Move("b", "S"))
    print(state.agents)
    print(state.Move("b", "E"))
    print(state.agents)
    print(state.Move("b", "S"))
    print(state.agents)
    state.addAgent("b", (1, 2))
    state.addAgent("b", (1, 2))
    state.addAgent("c", (1, 2))  # key is letter
    state.addGoal("c", (1, 1))
    state.addGoal("c", (1, 4))

    state.addBox(("c", "c"), (1, 1))  # key is (letter, color)
    state.addBox(("c", "c"), (1, 1))
    state.addBox(("c", "b"), (5, 4))

    """print(state.agents)
    print(state.goals)
    print(state.boxes)

    print(state.agents["b"])"""


# uncomment to see an example of the structure
# test()

# use
# from modules import actions
# to load the module from root
# then call actions.test() to run the test
