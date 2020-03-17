import sys
import numpy as np

from abc import ABCMeta, abstractmethod


def manh(x, y):
    """Compute Manhattan distance."""
    return sum(abs(i - j) for i, j in zip(x, y))


class Heuristic(metaclass=ABCMeta):
    def __init__(self, initial_state: "State"):
        # Here's a chance to pre-process the static parts of the level.
        self.box_number = len(
            [j for row in initial_state.boxes for j in row if j is not None]
        )
        self.goal_coords = {
            k.upper(): v for k, v in initial_state.localize_goals().items()
        }
        if len(self.goal_coords) == 1:
            # use vector operations instead of dicts
            self.goal_coords = np.array(self.goal_coords[next(iter(self.goal_coords))])
            self.h = self.h_vector
        else:
            self.h = self.h_dict

    def h_dict(self, state: "State") -> "int":
        # TODO add Ai coords
        ai = [state.agent_row, state.agent_col]
        box_coords = state.localize_boxes(self.box_number)
        # TODO: use a sum instead of a min?
        fitness = [
            min(manh(box, coord) for box in box_coords[goal] for coord in coords)
            for goal, coords in self.goal_coords.items()
        ]
        fitness_ai2box = [
            min(manh(box, ai) for box in box_coords[goal])
            for goal, coords in self.goal_coords.items()
        ]

        return sum(fitness) + min(fitness_ai2box)

    def h_vector(self, state: "State"):
        # added ai coords
        ai_coords = [state.agent_row, state.agent_col]
        box_coords = state.localize_boxes_vec(self.box_number)
        goal_coords = self.goal_coords
        return sum(
            [
                (abs(ai_coords - goal) + abs(box_coords - goal)).sum(axis=1).min()
                for goal in goal_coords
            ]
        )

    def __call__(self, state):
        return self.h(state)

    @abstractmethod
    def f(self, state: "State") -> "int":
        pass

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError


class AStar(Heuristic):
    def __init__(self, initial_state: "State"):
        super().__init__(initial_state)

    def f(self, state: "State") -> "int":
        return state.g + self.h(state)

    def __repr__(self):
        return "A* evaluation"


class WAStar(Heuristic):
    def __init__(self, initial_state: "State", w: "int"):
        super().__init__(initial_state)
        self.w = w

    def f(self, state: "State") -> "int":
        return state.g + self.w * self.h(state)

    def __repr__(self):
        return "WA* ({}) evaluation".format(self.w)


class Greedy(Heuristic):
    def __init__(self, initial_state: "State"):
        super().__init__(initial_state)

    def f(self, state: "State") -> "int":
        return self.h(state)

    def __repr__(self):
        return "Greedy evaluation"
