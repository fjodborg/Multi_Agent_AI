import actions


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

        newState = state.explore()

        print("\n\nFirst iteration\n")
        [print(child.map, child.prevAction, " cost:", child.g) for child in newState]
        leaf = newState[0]
        newChildren = leaf.explore()
        print(newChildren)
        newState.extend(newChildren)

        # newState.remove(leaf)
        # del leaf

        print("\n\nSecond iteration using the last leaf\n")
        [print(child.map, child.prevAction, " cost:", child.g) for child in newState]

        leaf = newState[0]
        children = leaf.explore()
        newState.extend(children)

        # newState.remove(leaf)
        # del leaf

        print("\n\nthird iteration using the last leaf\n")
        [
            print(child.map, child.prevAction, child.minimalRep(), " cost:", child.g)
            for child in newState
        ]


test(2)
