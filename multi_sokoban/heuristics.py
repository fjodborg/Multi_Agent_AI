"""Heuristics for Best First Search."""
from abc import ABC, abstractmethod
from typing import List


def manha_dist(a, b):
    """Measure Manhattan distance."""
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


class Heuristics(ABC):
    """Class for definin heuristcs."""

    @abstractmethod
    def __call__(self, states: List):
        """Call method, compute `heuristics` of List `states`."""
        return


class EasyRule(Heuristics):
    """Simple heuristics.

    Computes Manhattan distance for:
    * Boxes to goals.
    * Agents to boxes.
    """

    def __call__(self, states: List):
        """Calculate heuristic for states in place."""
        if type(states) is not list:
            states = [states]
        if len(states) == 0:
            return None

        for state in states:
            box_goal_cost = 0
            agt_box_cost = 0
            agt_box_costs = []
            for key in state.getGoalKeys():
                goal_params = state.getGoalsByKey(key)
                box_params = state.getBoxesByKey(key)
                # maybe add some temporary costs here for each key

                # find every position of goals and boxes with the given key
                for goal_pos, goal_color in goal_params:
                    box_goal_costs = []
                    # agtBoxCosts = []
                    for box_pos, _ in box_params:
                        # only take agents with the same color as goalColor
                        agent_keys = state.getAgentsByColor(goal_color)

                        if manha_dist(goal_pos, box_pos) == 0:
                            continue

                        for agent_key in agent_keys:
                            agentPos = state.getAgentsByKey(agent_key)[0][0]
                            agt_box_costs.append(manha_dist(agentPos, box_pos))

                        box_goal_costs.append(manha_dist(box_pos, goal_pos))

                    if len(box_goal_costs) > 0:
                        box_goal_cost += min(box_goal_costs)
                if len(agt_box_costs) > 0:
                    agt_box_cost += sum(agt_box_costs)

            state.h = box_goal_cost + agt_box_cost
            state.f = state.h * 5 + state.g
