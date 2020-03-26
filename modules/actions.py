import sys
import numpy as np
from abc import ABC, ABCMeta, abstractmethod


class Literals(ABC):
    def __init__(self):
        self.agents = {}  # hashtable
        self.goals = {}  # hashtable
        self.boxes = {}  # hashtable
        
        super().__init__()

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

    def AgentAt(obj, pos):
        pass

    def GaolAt(obj, pos):
        pass

    def BoxAt(obj, pos):
        pass

    def Free(pos):
        pass

    def Color(obj):
        pass

    def Neighbour(pos1, pos2):
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


class StateInit(Literals):
    def __init__(self):
        super().__init__()

    def Move(self, agt, agtfrom, agtto):
        Literals.Free(agtto)
        Literals.Neighbour(agtfrom, agtto)
        Literals.AgentAt(agt, agtfrom)

    def Push(self, agt, agtfrom, box, boxfrom, boxto):
        Literals.Free(boxto)
        Literals.Neighbour(agtfrom, boxfrom)
        Literals.Neighbour(boxfrom, boxto)
        Literals.BoxAt(box, agtfrom)
        Literals.AgentAt(agt, agtfrom)

    def Pull(agt, agtfrom, agtto, box, boxfrom):
        Literals.Free(agtto)
        Literals.Neighbour(agtto, boxfrom)
        Literals.Neighbour(boxfrom, agtfrom)
        Literals.BoxAt(box, agtfrom)
        Literals.AgentAt(agt, agtfrom)

    def Noop(self, agt):
        pass


def test():
    state = StateInit()
    state.Move(1, 2, 3)
    state.addAgent("b", (1, 1))  # key is color
    state.addAgent("b", (1, 2))
    state.addAgent("b", (1, 2))
    state.addAgent("c", (1, 2))  # key is letter
    state.addGoal("c", (1, 1))
    state.addGoal("c", (1, 4))

    state.addBox(("c", "c"), (1, 1))  # key is (letter, color)
    state.addBox(("c", "c"), (1, 1))
    state.addBox(("c", "b"), (5, 4))

    print(state.agents)
    print(state.goals)
    print(state.boxes)

    print(state.agents['b'])


# uncomment to see an example of the structure
# test()

# use 
# from modules import actions
# to load the module from root
# then call actions.test() to run the test