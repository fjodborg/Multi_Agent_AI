from multi_sokoban import actions
from multi_sokoban import emergency_aStar


def test(nr):
    if nr == 0:
        # remember to make walls, otherwise it isn't bound to the matrix!
        state = actions.StateInit()
        # state2 = state.copy()
        state.addMap(
            [
                ["+", "+", "+", "+", "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", "+", "+", "+", "+"],
            ]
        )

        state.addAgent("0", (1, 2), "b")
        # state.addBox("B", (2, 2), "c")
        state.addBox("B", (2, 2), "c")
        state.addBox("B", (3, 2), "b")
        # state.addGoal("b", (2, 2))
        state.addGoal("b", (3, 1))
        # state.addGoal("c", (1, 3))
        # state.addGoal("c", (2, 1))
        print(state.map)
        path, goalState = emergency_aStar.aStarSearch_func(state)
        print(path, "\n", goalState.map, goalState.goals, goalState.boxes)
    if nr == 1:
        # remember to make walls, otherwise it isn't bound to the matrix!
        state = actions.StateInit()
        # state2 = state.copy()
        state.addMap(
            [
                ["+", "+", "+", "+", "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", chr(32), chr(32), chr(32), "+"],
                ["+", "+", "+", "+", "+"],
            ]
        )

        state.addAgent("0", (1, 2), "b")
        # state.addBox("B", (2, 2), "c")
        # state.addBox("B", (11, 2), "c")
        state.addBox("C", (12, 2), "b")
        state.addBox("B", (11, 2), "b")
        # state.addGoal("b", (2, 2))
        state.addGoal("C", (1, 1))
        state.addGoal("b", (2, 1))
        # state.addGoal("c", (1, 3))
        # state.addGoal("c", (2, 1))
        print(state.map)
        path, goalState = emergency_aStar.aStarSearch_func(state)
        print(path, "\n", goalState.map, goalState.goals, goalState.boxes)
        print("notes explored:", len(goalState.explored))
    if nr == 2:
        # remember to make walls, otherwise it isn't bound to the matrix!
        state = actions.StateInit()
        # state2 = state.copy()
        state.addMap(
            [
                ['+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', ],
                ['+', '0', chr(32), 'A', chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), '+', ],
                ['+', '+', 'B', chr(32), '+', '+', '+', '+', '+', '+', '+', '+', chr(32), '+', '+', '+', '+', '+', '+', '+', chr(32), '+', ],
                ['+', '+', chr(32), chr(32), '+', chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), '+', chr(32), '+', chr(32), chr(32), chr(32), chr(32), chr(32), '+', chr(32), '+', ],
                ['+', '+', chr(32), chr(32), '+', chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), '+', chr(32), '+', chr(32), chr(32), chr(32), chr(32), chr(32), '+', chr(32), '+', ],
                ['+', '+', chr(32), chr(32), '+', chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), '+', chr(32), '+', chr(32), chr(32), chr(32), chr(32), chr(32), '+', chr(32), '+', ],
                ['+', '+', chr(32), chr(32), '+', chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), '+', chr(32), '+', chr(32), chr(32), chr(32), chr(32), chr(32), '+', chr(32), '+', ],
                ['+', '+', chr(32), chr(32), '+', chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), '+', chr(32), '+', chr(32), chr(32), chr(32), chr(32), chr(32), '+', chr(32), '+', ],
                ['+', '+', chr(32), chr(32), '+', '+', '+', '+', '+', '+', '+', '+', chr(32), '+', '+', '+', '+', '+', '+', '+', chr(32), '+', ],
                ['+', chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), chr(32), '+', ],
                ['+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+', ],
            ]
        )

        state.addAgent("0", (1, 1), "b")
        state.addBox("A", (1, 3), "b")
        state.addBox("B", (2, 2), "b")
        #state.addGoal("a", (10, 8))
        #state.addGoal("b", (10, 8))
        state.addGoal("a", (1, 4))
        state.addGoal("b", (3, 2))
        print(state.map)
        path, goalState = emergency_aStar.aStarSearch_func(state)
        print(path, "\n", goalState.map, goalState.goals, goalState.boxes)
        print("notes explored:", len(goalState.explored))
    if nr == 3:
        # remember to make walls, otherwise it isn't bound to the matrix!
        state = actions.StateInit()
        # state2 = state.copy()
        state.addMap(
            [
                ['+','+','+','+','+','+','+','+','+','+','+','+','+','+'],
                ['+','0',' ','A',' ',' ',' ',' ',' ',' ',' ',' ',' ','+'],
                ['+','+','B',' ','+','+','+','+','+','+','+','+',' ','+'],
                ['+','+',' ',' ','+',' ',' ',' ',' ',' ',' ','+',' ','+'],
                ['+','+',' ',' ','+','+','+','+','+','+','+','+',' ','+'],
                ['+',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','+'],
                ['+','+','+','+','+','+','+','+','+','+','+','+','+','+'],
            ]
        )

        state.addAgent("0", (1, 1), "b")
        state.addBox("A", (1, 3), "b")
        state.addBox("B", (2, 2), "b")
        #state.addGoal("a", (5, 5))
        #state.addGoal("b", (5, 4))
        state.addGoal("a", (1, 4))
        state.addGoal("b", (3, 2))
        print(state.map)
        path, goalState = emergency_aStar.aStarSearch_func(state)
        print(path, "\n", goalState.map, goalState.goals, goalState.boxes)
        print("nodes explored:", len(goalState.explored))
    if nr == 4:
        frontier = PriorityQueue()
        leaf = initState
        calcHuristicsFor(leaf)
        self.strategy.get_and_remove_leaf()
        while not self.strategy.leaf.isGoalState():
            if iterations == 1000:
                println(f"{self.strategy.count} nodes explored")
                iterations = 0

            if get_usage() > MAX_USAGE:
                raise ResourceLimit("Maximum  nbn usage exceeded.")
                return None

            if self.strategy.frontier_empty():
                return None

            self.strategy.get_and_remove_leaf()

            if self.strategy.leaf.isGoalState():
                return self.strategy.walk_best_path()

            iterations += 1

test(3)
