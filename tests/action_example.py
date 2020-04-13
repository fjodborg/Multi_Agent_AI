from multi_sokoban import actions


def test(nr):
    # remember to make walls, otherwise it isn't bound to the matrix!
    state = actions.StateInit()
    # state2 = state.copy()
    state.addMap(
        [
            ["+", "+", "+", "+", "+"],
            ["+", "+", chr(32), chr(32), "+"],
            ["+", chr(32), "B", "+", "+"],
            ["+", "+", "+", chr(32), "+"],
            ["+", "+", "+", "+", "+"],
        ]
    )
    print(state.map)
    if nr == 0:
        state.addAgent("0", (1, 1))
        state.addBox("b", (2, 2), "b")
        state.addBox("C", (1, 2), "c")
        state.addBox("C", (2, 1), "b")
        leaf = state
        frontier = []
        frontier.append(leaf)

        newState = leaf.explore()

        print("\n\nFirst iteration\n")
        [print(child.map, child.prevAction, " cost:", child.g) for child in newState]
        leaf = newState[-1]
        newChildren = leaf.explore()
        print(newChildren)
        newState.extend(newChildren)

        # newState.remove(leaf)
        # del leaf

        print("\n\nSecond iteration using the last leaf\n")
        [print(child.map, child.prevAction, " cost:", child.g) for child in newState]

        leaf = newState[-1]
        children = leaf.explore()
        newState.extend(children)

        # newState.remove(leaf)
        # del leaf

        print("\n\nthird iteration using the last leaf\n")
        [
            print(child.map, child.prevAction, child.minimalRep(), " cost:", child.g,)
            for child in newState
        ]

        leaf = newState[-1]
        print(leaf.bestPath())
    if nr == 1:
        state.addAgent("0", (1, 1), "c")
        state.addBox("B", (2, 2), "c")
        state.addBox("C", (1, 2), "c")
        state.addBox("C", (2, 1), "b")
        state.addGoal("c", (3, 3))
        state.addGoal("b", (2, 3))
        leaf = state
        frontier = []
        frontier.append(leaf)

        newState = leaf.explore()

        print("\n\nFirst iteration\n")
        [
            print(child.map, child.actionPerformed, " cost:", child.g)
            for child in newState
        ]
        leaf = newState[-1]
        print(leaf.actionPerformed)
        newChildren = leaf.explore()
        print(newChildren)
        newState.extend(newChildren)

        newState.remove(leaf)
        # del leaf

        print("\n\nSecond iteration using the last leaf\n")
        [
            print(child.map, child.actionPerformed, " cost:", child.g)
            for child in newState
        ]

        leaf = newState[-1]
        print(leaf.actionPerformed)
        children = leaf.explore()
        newState.extend(children)

        newState.remove(leaf)
        # del leaf

        print("\n\nthird iteration using the last leaf\n")
        [
            print(
                child.map, child.actionPerformed, child.minimalRep(), " cost:", child.g,
            )
            for child in newState
        ]

        leaf = newState[-1]
        print(leaf.actionPerformed)
        print(leaf.bestPath())
        print(
            leaf.getPos(leaf.boxes, "C", 0),
            leaf.getPos(leaf.boxes, "C", 1),
            leaf.getPos(leaf.goals, "c"),
        )
        print(
            "Agent par:",
            leaf.getAgentByKey("0"),
            "Boxes par:",
            leaf.getBoxesByKey("C"),
            "Goal par:",
            leaf.getGoalsByKey("c"),
            "all goals:",
            leaf.getGoals(),
        )
        leaf.h = 5
        print("cost for", leaf, "to goal is", leaf.h)

test(1)
