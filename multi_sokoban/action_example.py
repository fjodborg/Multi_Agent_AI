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
        # TODO  check if next State is explored!
        #print(state.map)
        state.addAgent("0", (1, 1))
        state.addBox("C", (2, 2), "c")
        state.addBox("C", (1, 2), "c")
        state.addBox("C", (2, 1), "b")
        newState = state.get_children()
        print("\n\nFirst iteration\n")
        [print(child.map, child.prevAction, " cost:", child.g) for child in newState]
        leaf = newState[0]
        children = leaf.get_children()
        newState.extend(children)
        
        newState.remove(leaf)
        del leaf
        
        print("\n\nSecond iteration using leaf 0\n")
        [print(child.map, child.prevAction, " cost:", child.g) for child in newState]
    
    elif nr == 1:
        state.addAgent("0", (1, 1))
        state.addBox("C", (2, 2), "c")
        state.addBox("C", (1, 2), "b")
        state.addBox("C", (2, 1), "b")

        frontier = []
        frontierSet = set()
        frontier.append(state)
        # using getState rather than the whole state saves memory

        newState = state.get_children()

        print("\n\nFirst iteration\n")
        [print(child.map, child.prevAction, " cost:", child.g) for child in newState]
        leaf = newState[-1]
        children = leaf.get_children()
        newState.extend(children)
        
        #newState.remove(leaf)
        #del leaf

        print("\n\nSecond iteration using the last leaf\n")
        [print(child.map, child.prevAction, " cost:", child.g) for child in newState]
    
        leaf = newState[-1]
        children = leaf.get_children()
        newState.extend(children)
        
        #newState.remove(leaf)
        #del leaf

        print("\n\nthird iteration using the last leaf\n")
        [print(child.map, child.prevAction, " cost:", child.g) for child in newState]


test(1)
