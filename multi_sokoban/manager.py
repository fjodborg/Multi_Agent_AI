"""Task sharing MA communication."""
from copy import deepcopy
from typing import Callable, List

from .actions import StateInit
from .bdi import Agent, Message
from .heuristics import dGraph
from .resultsharing import Resultsharing
from .strategy import BestFirstSearch
from .utils import HEADER, STATUS, println


class Manager:
    """Top manager that performs problem subdivision and task broadcasting.

    Attributes
    ----------
    top_problem: StateInit
        whole problem definition
    strategy: BestFirstSearch
        child strategy of BestFirstSearch
    agents: dict
        agent names as keys and Agent objects as values. Agents are generated
        on demand; i.e., there can be idle agents in the map that won't have an
        associated Agent object (see multi_sokoban/bdi.py)
    heuristic: Callable
        function to calculate the heuristic. This is usually an object of a
        child class of Heuristics that implement __call__() but can be any
        function that accepts a list of states. Default: EasyRule
    solutions: List[List]
        the solutions of the different agents to their particular subproblems.
        `None` until there is a solution
    nodes_explored: int
        sum of the number of explored nodes by the agents
    inbox: List[Message]
        List of OK `Message`s (see multi_sokoban/bdi.py) that the agents
        generate when they solve a request of another agent.

    """

    def __init__(
        self,
        top_problem: StateInit,
        strategy: BestFirstSearch,
        heuristic: Callable = None,
    ):
        """Initialize with the whole problem definition `top_problem`."""
        self.top_problem = top_problem
        self.strategy = strategy
        self.agents = {}
        self.heuristic = heuristic if heuristic else dGraph(top_problem)
        self.solutions = None
        self.nodes_explored = 0
        self.paths = {}
        self.inbox = []


    def run(self) -> List:
        """Perform the task sharing."""
        self.divide_problem()

        colliding = True
        new_time = 0
        while colliding is not None:
            println("===================TASK SHARING!===================")
            self.solve_world()
            println(f"Solution: {self.join_tasks()}")

            println("==================RESULT SHARING!==================")
            colliding = self.solveCollision(new_time)
            println(colliding)
            if colliding is not None:
                # we have all the information to do direct contracting
                self.pack_collision(colliding)
                time = self.inbox[0].time
                curr_pos = time[0][1]
                for event in time:
                    pos = event[1]
                    if curr_pos[0] != pos[0] or curr_pos[1] != pos[1]:
                        new_time = event[0]
                        break

        return self.join_tasks()

    def divide_problem(self):
        """Subdivide the problem in terms of box colors."""
        for goal in self.top_problem.goals:
            # create subproblem and remove other goals
            task = deepcopy(self.top_problem)
            task.keepJustGoal(goal)
            # select best agent and remove other agents
            agent = self.broadcast_task(task)
            if agent is None:
                continue
            task.keepJustAgent(agent)
            if agent in self.agents:
                self.agents[agent].add_task(task)
            else:
                println("hello", self.heuristic)
                self.agents[agent] = Agent(task, self.strategy, self.heuristic)

    def bidding(self, task: StateInit, agents: List[str]) -> str:
        """Request heuristic from the `agents` to solve a particular `task`."""
        min_marginal_cost = float("inf")
        for agent in agents:
            if agent in self.agents:
                # agent got already tasks assigned so you have to use the joint
                marginal_cost = self.agents[agent].marginal_task_cost(task)
            else:
                # here marginal cost is the total heuristic estimate
                tmp_task = deepcopy(task)
                tmp_task.keepJustAgent(agent)
                self.heuristic(tmp_task)
                marginal_cost = tmp_task.f
            # greater or equal to guarantee a selected agent
            if min_marginal_cost >= marginal_cost:
                min_marginal_cost = marginal_cost
                selected_agent = agent
        return selected_agent

    def broadcast_task(self, task: StateInit) -> str:
        """Request task for agents."""
        # a task is guaranteed to have exactly one goal
        color_of = list(task.goals.values())[0][0][1]
        ok_agents = [k for k, v in task.agents.items() if color_of == v[0][1]]
        if len(ok_agents) > 1:
            selected_agent = self.bidding(task, ok_agents)
        elif ok_agents:
            # direct contract, the usual case
            selected_agent = ok_agents[0]
        else:
            selected_agent = None
        return selected_agent

    def broadcast_message(self, message: Message) -> str:
        """Request help in the form of a message."""
        if message.receiver:
            return message.receiver
        color_of = message.color
        ok_agents = [k for k, v in self.agents.items() if color_of == v.color][0]
        return ok_agents

    def sort_agents(self):
        """Return sorted agents by name of agent (0-10)."""
        # WARNING: ths fails if there are more than 10 agents
        return sorted(self.agents)

    def solveCollision(self, new_time):
        """Call the Result Sharing module: avoid deadlocks and collisions.

        -> multi_sokoban/resultsharing.py
        """
        # TODO check for empty frontiers
        # check for traceback possibilities
        rs = Resultsharing(self, [])
        return rs.findAndResolveCollision(new_time)

    def pack_collision(self, colliding: List):
        """Write a message to inbox from self.solveCollision results."""
        receiver = str(colliding[0])
        requester = str(colliding[1])
        span = colliding[2]
        println(span)
        moving_task = self.agents[requester].task
        # let's try with just one goal and one box
        box = list(moving_task.goals)[0].upper()
        index = 0
        # clean up messages
        for agent in self.agents.values():
            agent.stored_message = False
        self.inbox = []
        time = moving_task.bestPath(
            format=box, index=index,
        )
        time_agent = moving_task.bestPath(
            format=requester, index=index,
        )
        # result sharing has introduced NoOps
        for i in range(len(time)):
            time[i][0] += span
            time_agent[i][0] += span
        # to get the right times, we need to trim artificial NoOps
        while self.paths[receiver][-1] == "NoOp":
            self.paths[receiver].pop()
        self.inbox.append(
            Message(
                object_problem=box,
                color=self.agents[receiver].color,
                index=index,
                receiver=receiver,  # will move away
                requester=requester,  # is doing its stuff
                header=HEADER.replan,
                time=time,
                agent=time_agent
            )
        )

    def solve_world(self):
        """Solve the top problem."""
        solved = set()
        while len(solved) != len(self.agents):
            for name, agent in self.agents.items():
                path, message = agent.solve(self.inbox)
                self.nodes_explored += len(agent.task.explored)
                if message:
                    ok_agent = self.broadcast_message(message)
                    message.receiver = ok_agent
                    println(f"Agent({name}) broadcasted {message.header} task!")
                    self.inbox.append(message)
                if agent.status == STATUS.ok:
                    solved.add(name)
                    if name in self.paths:
                        self.paths[name] += path
                    else:
                        self.paths[name] = path

        self.solutions = [self.paths[agent_name] for agent_name in self.sort_agents()]

    def join_tasks(self) -> List:
        """Join all the task in one big path.

        Returns
        -------
        list of actions to the best solution

        """
        paths = deepcopy(self.solutions)
        # make sure that all paths has the same length
        sol_len = max([len(path) for path in paths])
        for i in range(len(paths)):
            while sol_len > len(paths[i]):
                paths[i].append("NoOp")
        
        if len(paths) < len(self.top_problem.agents):
            missing = set(self.top_problem.agents.keys()) ^ {
                agent for agent in self.agents
            }
            paths.insert(int(list(missing)[0]), ["NoOp"] * len(paths[0]))

        println(paths)
        return [";".join(actions) for actions in zip(*paths)]
