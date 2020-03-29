import actions


def test(nr):
    # remember to make walls, otherwise it isn't bound to the matrix!
    state = actions.StateInit()
    # state2 = state.copy()
    state.addMap(
        [
            ["+", "+", "+", "+", "+"],
            ["+", "0", chr(32), chr(32), "+"],
            ["+", chr(32), "B", "+", "+"],
            ["+", "+", "+", chr(32), "+"],
            ["+", "+", "+", "+", "+"],
        ]
    )
    print(state.map)
    if nr == 0:
        state.addAgent("0", (1, 1))  # key is color
        state.addAgent("1", (1, 2))
        print(state.agents)
        state.Move("0", "W")
        print(state.agents)
        state.Move("1", "E")
        print(state.agents)
        state.Move("0", "S")
        print(state.agents)
        state.Move("0", "S")
        print(state.agents)
        state.addAgent("2", (1, 2))
        state.addAgent("3", (1, 2))  # key is letter
        state.addGoal("c", (1, 1))
        state.addGoal("c", (1, 4))

        state.addBox("C", "c", (1, 1))  # key is (letter, color)
        state.addBox("C", "c", (1, 1))
        state.addBox("C", "b", (5, 4))
    elif nr == 1:
        state.addAgent("0", (1, 1))  # key is color
        state.addBox("B", "b", (2, 2))
        state.Move("0", "E")
        # print(state.agents)
        state.Push("0", "B", "b", "W", 0)
        print(state.agents)
        print(state.boxes)
        state.Push("0", "B", "b", "N", 0)
        print(state.agents)
        print(state.boxes)
    elif nr == 2:
        state.addAgent("0", (1, 1))  # key is color
        state.addBox("B", "b", (2, 2))
        state.Move("0", "E")
        # print(state.agents)
        state.Pull("0", "B", "b", "W", 0)
        print(state.agents)
        print(state.boxes)
        state.Pull("0", "B", "b", "S", 0)
        print(state.agents)
        print(state.boxes)
        state.Pull("0", "B", "b", "S", 0)
        print(state.agents)
        print(state.boxes)
    elif nr == 3:
        state.addAgent("0", (1, 1))  # key is color
        state.addBox("B", "b", (2, 2))
        state.addGoal("b", (2, 2))
        print(state.agents)
        print(state.boxes)
        state2 = actions.StateInit(state)
        state.Move("0", "E")
        # print(state.agents)
        state.Pull("0", "B", "b", "W", 0)
        print(state.agents)
        print(state.boxes)
        state.Pull("0", "B", "b", "S", 0)
        print(state.agents)
        print(state.boxes)
        state.Pull("0", "B", "b", "S", 0)
        print(state.agents, state2.agents)
        print(state.boxes, state2.boxes)
        state.addGoal("b", (2, 2))
        print(state.goals, state2.goals)
    elif nr == 4:
        state.addAgent("0", (1, 1))  # key is color
        state.addBox("B", "b", (2, 2))
        state.Move("0", "E")
        print(state.map)
        state.Pull("0", "B", "b", "W", 0)
        print(state.map)
        state.Pull("0", "B", "b", "S", 0)
        print(state.map)
        state.Push("0", "B", "b", "E", 0)
        print(state.map)


test(4)
