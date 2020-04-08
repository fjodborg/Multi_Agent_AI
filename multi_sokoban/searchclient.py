"""Client that receives messages from the server."""
import argparse
import re
import string
import sys
from typing import List

import numpy as np

from _io import TextIOWrapper
from heuristic import AStar, Greedy, WAStar

from .actions import StateInit
from .aStar import PriorityQueue
from .memory import MAX_USAGE, get_usage


class ParseError(Exception):
    """Define parsing error exception."""

    pass


class ResourceLimit(Exception):
    """Define limit of resources exception."""

    pass


class SearchClient:
    """Contain the AI, strategy and parsing."""

    def __init__(
        self, server_messages: TextIOWrapper, strategy: PriorityQueue = None
    ):
        """Init object."""
        self.colors_re = re.compile(r"^[a-z]+:\s*([0-9])\s*,\s*([0-9A-Z]+)")
        self.invalid_re = re.compile(r"[^A-Za-z0-9+ ]")
        self._strategy = self.add_strategy(strategy)
        self.colors = {}
        self.initial_state = self.parse_map(server_messages)

    @property
    def strategy(self) -> PriorityQueue:
        """Get strategy, the setter handles different types of inputs."""
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: str):
        self.strategy = PriorityQueue()
        # this is, of course, wrong
        # we need to have a way to build progammatically the PriorityQueue
        # given a search algorithm
        if isinstance(strategy, Strategy):
            self._strategy = strategy
        elif strategy == "astar":
            self._strategy = StrategyBestFirst(AStar(self.initial_state))
        elif strategy == "wastar":
            self._strategy = StrategyBestFirst(WAStar(self.initial_state, 5))
        elif strategy == "greedy":
            self._strategy = StrategyBestFirst(Greedy(self.initial_state))

    def add_strategy(self, strategy: str):
        """Initialize strategy, just for the __init__ method."""
        self.strategy = strategy

    def parse_map(self, server_messages: TextIOWrapper) -> StateInit:
        """Parse the initial server message into a map."""
        # a level has a header with color specifications followed by the map
        # the map starts after the line "#initial"
        line = server_messages.readline().rstrip()
        initial = False  # mark start of level map
        map = []
        while line:
            if initial:
                map.append(line)
                for char in line:
                    if self.invalid_re.match(char):
                        raise ParseError(f"Invalid character in level: {char}")
            else:
                if line.find("#initial") != -1:
                    initial = True
                    continue
                color = self.colors_re.search(line)
                if color:
                    col_count = np.unique(list(self.colors.values()))
                    for col in color.groups:
                        self.colors[col] = str(col_count)
            line = server_messages.readline().rstrip()
        return self.build_map(np.array(map))

    def build_map(self, map: np.array) -> StateInit:
        """Build the StateInit from the parsed map.

        addMap just parses rigid positions (not agent and boxes), so
        get the positions of the agents and boxes and remove them from map
        """
        state = StateInit()
        all_objects = []
        possible_objects = string.digits + string.ascii_letters
        for obj in possible_objects:
            agent_pos = np.where(map == obj)
            for x, y in zip(agent_pos[0], agent_pos[1]):
                color = self.colors[obj] if obj in self.colors else None
                all_objects.append([obj, (x, y), color])
            map[agent_pos] = " "
        # it is required to add the map first and then the rest level objects
        state.addMap(map)
        for obj, pos, color in all_objects:
            x, y = pos
            if obj in string.digits:
                state.addAgent(obj, (x, y), color)
            elif obj in string.string.ascii_letters:
                state.addBox(obj, (x, y), color)
            else:
                state.addGoal(obj, (x, y))
        return state

    def search(self) -> List[np.array, ...]:
        """Apply search algorithm."""
        print(
            f"Starting search with strategy {self.strategy}.",
            file=sys.stderr,
            flush=True,
        )
        self.strategy.add_to_frontier(self.initial_state)
        iterations = 0

        while True:
            if iterations == 1000:
                print(
                    self.strategy.search_status(), file=sys.stderr, flush=True
                )
                iterations = 0

            if get_usage() > MAX_USAGE:
                raise ResourceLimit("Maximum  nbn usage exceeded.")
                return None

            if self.strategy.frontier_empty():
                return None

            leaf = self.strategy.get_and_remove_leaf()

            if leaf.is_goal_state():
                return leaf.extract_plan()

            self.strategy.add_to_explored(leaf)
            for child_state in leaf.get_children():
                if not self.strategy.is_explored(
                    child_state
                ) and not self.strategy.in_frontier(child_state):
                    self.strategy.add_to_frontier(child_state)

        iterations += 1


def parse_arguments() -> argparse.ArgumentParser:
    """Parse CLI arguments, such as strategy and  nbn limit."""
    parser = argparse.ArgumentParser(
        description="Simple client based on state-space graph search."
    )
    parser.add_argument(
        "--max- nbn",
        metavar="<MB>",
        type=float,
        default=2048.0,
        help="The maximum memory usage allowed in MB (soft limit, default 2048).",
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
        print(strategy.search_status(), file=sys.stderr, flush=True)
        print("Unable to solve level.", file=sys.stderr, flush=True)
        sys.exit(0)
    else:
        print("\nSummary for {}.".format(strategy), file=sys.stderr, flush=True)
        print(
            "Found solution of length {}.".format(len(solution)),
            file=sys.stderr,
            flush=True,
        )
        print(
            "{}.".format(strategy.search_status()), file=sys.stderr, flush=True
        )

        for state in solution:
            print(state.action, flush=True)
            response = server_messages.readline().rstrip()
            if "false" in response:
                print(
                    'Server responsed with "{}" to the action "{}" applied in:\n{}\n'.format(
                        response, state.action, state
                    ),
                    file=sys.stderr,
                    flush=True,
                )
                break


if __name__ == "__main__":
    args = parse_arguments()
    run_loop(args.strategy, args.memory)
