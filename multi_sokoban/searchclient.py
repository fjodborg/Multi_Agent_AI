"""Client that receives messages from the server."""
import argparse
import re
import string
import sys
from typing import List

import numpy as np

from _io import TextIOWrapper
from multi_sokoban.actions import StateInit
from multi_sokoban.emergency_aStar import BestFirstSearch, aStarSearch
from multi_sokoban.memory import MAX_USAGE, get_usage
from multi_sokoban.utils import println


class ParseError(Exception):
    """Define parsing error exception."""

    pass


class ResourceLimit(Exception):
    """Define limit of resources exception."""

    pass


class SearchClient:
    """Contain the AI, strategy and parsing."""

    def __init__(self, server_messages: TextIOWrapper, strategy: str):
        """Init object."""
        self.colors_re = re.compile(r"^([a-z]+):\s*([0-9])\s*")
        self.invalid_re = re.compile(r"[^A-Za-z0-9+]")
        self.colors = {}
        self.initial_state = self.parse_map(server_messages)
        self._strategy = None
        self.add_strategy(strategy)

    @property
    def strategy(self) -> BestFirstSearch:
        """Get strategy, the setter handles different types of inputs."""
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: str):
        if isinstance(strategy, BestFirstSearch):
            self._strategy = strategy(self.initial_state)
        else:
            if strategy == "astar":
                self._strategy = aStarSearch(self.initial_state)
            elif strategy == "wastar":
                raise NotImplementedError
            elif strategy == "greedy":
                raise NotImplementedError

    def add_strategy(self, strategy: str):
        """Initialize strategy, just for the __init__ method."""
        self.strategy = strategy

    def parse_map(self, server_messages: TextIOWrapper) -> StateInit:
        """Parse the initial server message into a map."""
        # a level has a header with color specifications followed by the map
        # the map starts after the line "#initial"
        line = server_messages.readline().rstrip()
        initial = False  # mark start of level map
        goal = False  # mark start of level map
        map = []
        goal_state = []
        col_count = 0
        while line:
            if goal:
                if line.find("#end") != -1:
                    return self.build_map(map, goal_state)
                goal_state.append(list(line))
            elif initial:
                if line.find("#goal") != -1:
                    goal = True
                else:
                    map.append(list(line))
            else:
                if line.find("#initial") != -1:
                    initial = True
                else:
                    color_matched = self.colors_re.search(line)
                    if color_matched:
                        col_count += 1
                        color = color_matched[1]
                        self.colors[color_matched[2]] = color
                        for obj in line[len(color) + 5 :].split(", "):
                            self.colors[obj] = color
            line = server_messages.readline()[:-1]  # chop last

    def build_map(self, map: List, goal_state: List) -> StateInit:
        """Build the StateInit from the parsed map.

        addMap just parses rigid positions (not agent and boxes), so
        get the positions of the agents and boxes and remove them from map
        """
        state = StateInit()
        all_objects = []
        agent_n_boxes = string.digits + string.ascii_uppercase
        all_objects = self._locate_objects(np.array(map), agent_n_boxes)
        # it is required to add the map first and then the rest level objects
        state.addMap(map)
        for obj, pos, color in all_objects:
            row, col = pos
            if obj in string.digits:
                state.addAgent(obj, (row, col), color)
            elif obj in string.ascii_uppercase:
                state.addBox(obj, (row, col), color)
        goals = string.ascii_uppercase
        all_objects = self._locate_objects(np.array(goal_state), goals)
        for obj, pos, color in all_objects:
            row, col = pos
            state.addGoal(obj, (row, col), color)
        return state

    def _locate_objects(self, map: np.array, possible_objects: str) -> List:
        all_objects = []
        # print(map, file=sys.stderr, flush=True)
        for obj in possible_objects:
            agent_pos = np.where(map == obj)
            if len(agent_pos) > 0:
                for x, y in zip(agent_pos[0], agent_pos[1]):
                    color = self.colors[obj] if obj in self.colors else None
                    all_objects.append([obj, (x, y), color])
                map[agent_pos] = " "
        return all_objects

    def search(self) -> List:
        """Apply search algorithm."""
        println(f"Starting search with strategy {self.strategy}.")

        iterations = 0
        while not self.strategy.leaf.isGoalState():
            # println(self.strategy.leaf.h)
            if iterations == 1000:
                println(f"{self.strategy.count} nodes explored")
                iterations = 0

            if get_usage() > MAX_USAGE:
                raise ResourceLimit("Maximum memory usage exceeded.")
                return None

            self.strategy.get_and_remove_leaf()

            if self.strategy.frontier_empty():
                println("Frontier empty!")
                return None

            if self.strategy.leaf.isGoalState():
                return self.strategy.walk_best_path()

            iterations += 1


def parse_arguments() -> argparse.ArgumentParser:
    """Parse CLI arguments, such as strategy and  nbn limit."""
    parser = argparse.ArgumentParser(
        description="Simple client based on state-space graph search."
    )
    parser.add_argument(
        "--max-memory",
        metavar="<MB>",
        type=float,
        default=2048.0,
        help="The maximum memory usage allowed in MB (soft limit).",
    )
    strategy_group = parser.add_mutually_exclusive_group()
    strategy_group.add_argument(
        "-astar",
        action="store_const",
        dest="strategy",
        const="astar",
        help="Use the A* strategy.",
    )
    strategy_group.add_argument(
        "-wastar",
        action="store_const",
        dest="strategy",
        const="wastar",
        help="Use the WA* strategy.",
    )
    strategy_group.add_argument(
        "-greedy",
        action="store_const",
        dest="strategy",
        const="greedy",
        help="Use the Greedy strategy.",
    )
    args = parser.parse_args()

    return args


def run_loop(strategy: str, memory: float):
    """Iterate over main loop Server->Client->Server."""
    global MAX_USAGE
    MAX_USAGE = memory
    server_messages = sys.stdin
    client = SearchClient(server_messages, strategy)
    solution = client.search()
    if solution is None:
        println("Unable to solve level.")
        sys.exit(1)
    else:
        println("\nSummary for {}.".format(strategy))
        println("Found solution of length {}.".format(len(solution)))
        for state in solution:
            print(state, flush=True)
            response = server_messages.readline().rstrip()
            if "false" in response:
                println(
                    f"Server responsed with '{response}' to the action"
                    f" '{state}' applied in:\n{solution}\n"
                )
                break


if __name__ == "__main__":
    args = parse_arguments()
    print("MAI client\n", flush=True)
    run_loop(args.strategy, args.max_memory)
