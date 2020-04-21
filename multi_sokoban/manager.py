"""Task sharing MA communication."""
from copy import deepcopy
from typing import List

from .actions import StateInit
from .emergency_aStar import BestFirstSearch, aStarSearch_func, calcHuristicsFor
from .memory import MAX_USAGE, get_usage
from .utils import ResourceLimit, println


class Manager:
    """Top manager that performs problem subdivision and task broadcasting."""

    def __init__(self, top_problem: StateInit, strategy: BestFirstSearch):
        """Initialize with the whole problem definition `top_problem`."""
        self.top_problem = top_problem
        self.strategy = strategy
        self.tasks = {}
        # TODO: move status to BFS class
        self.status = {}
        self.freed_agents = {}
        self.agent_to_status = {}

    def run(self) -> List:
        """Perform the task sharing."""
        self.divide_problem()
        self.solve_world()
        return self.join_tasks()

    def divide_problem(self):
        """Subdivide the problem in terms of box colors."""
        for goal in self.top_problem.goals:
            # create subproblem and remove other goals
            task = deepcopy(self.top_problem)
            ext_goals = list(task.goals.keys())
            for external_goal in ext_goals:
                if external_goal != goal:
                    del task.goals[external_goal]
            # select best agent and remove other agents
            agent = self.broadcast_task(task)
            ext_agents = list(task.agents.keys())
            for external_agent in ext_agents:
                if external_agent != agent:
                    del task.agents[external_agent]

            self.tasks[goal] = (task, agent)
            self.status[goal] = None
            self.agent_to_status[goal] = agent

    def bidding(self, task: StateInit, agents):
        """Request a heuristic from the agents to solve a particular task."""
        raise NotImplementedError

    def broadcast_task(self, task: StateInit) -> str:
        """Request task for agents."""
        # a task is guaranteed to have exactly one goal
        # color_of = list(task.goals)[0][1]
        color_of = list(task.goals.values())[0][0][1]
        ok_agents = [k for k, v in task.agents.items() if color_of == v[0][1]]
        if len(ok_agents) > 1:
            selected_agent = self.bidding(task, ok_agents)
        else:
            selected_agent = ok_agents[0]
        return selected_agent

    def solve_task(self, task) -> List:
        """Search for task.

        Returns
        -------
        Path to the solutions (in actions) or none.

        """
        searcher = self.strategy(task)
        println(f"goals -> {task.goals}\n"
                f"agents -> {task.agents}\nboxes -> {task.boxes}\n")
        path, strategy = search(searcher)
        return path, strategy.leaf

    def choose_priority_path(self, paths):
        initPos = ([[initPos[0][0]] for initPos in list(self.top_problem.agents.values())])
        pos = initPos
        ##  Ask how to access the latest state
        i = 0 
        println(f"pos: {pos}")
        for agt in paths:
            for action in agt:
                prefix = action[0]
                #println(f"pos: {pos}")
                if type(pos[i][-1]) == list:
                    [row, col] = pos[i][-1][0]
                else:
                    [row, col] = pos[i][-1]
                #println(f"row:{row},col:{col}")
                if prefix == "N":
                    pos[i].append((row, col))
                elif prefix == "M":
                    [drow, dcol] = self.top_problem.dir[action[-2:-1]]
                    pos[i].append((row + drow, col + dcol))
                elif prefix == "P":
                    if action[0:4] == "Push":
                        [drow1, dcol1] = self.top_problem.dir[action[-4:-3]]
                        [drow2, dcol2] = self.top_problem.dir[action[-2:-1]]
                        #println(f"{row},{drow1}")

                        [row1, col1] = (row + drow1, col + dcol1)
                        [row2, col2] = (row1 + drow2, col1 + dcol2)
                        pos[i].append([(row1, col1), (row2, col2)])
                    else:
                        [drow1, dcol1] = self.top_problem.dir[action[-4:-3]]
                        [drow2, dcol2] = self.top_problem.dir[action[-2:-1]]
                        #println(f"{row},{drow1}")

                        [row1, col1] = (row + drow1, col + dcol1)
                        [row2, col2] = (row, col)
                        pos[i].append([(row1, col1), (row2, col2)])
                
            i += 1

        indicies = [0] * len(paths)
        println(pos)
             
        changeHappend = True
        while changeHappend:
            changeHappend = False
            for agtIdx in range(len(paths)):
                i = indicies[agtIdx] + 1
                path = paths[agtIdx]
                # println(f"{i},{len(path)}")
                if i >= len(path):
                    continue
                else: 

                    newPathLength = len(path)
                    for occupiedIdx in range(len(paths)):
                        if occupiedIdx == agtIdx:
                            continue
                        j = indicies[occupiedIdx]
                        #println(indicies) 
                        #println(f"agtIdx{pos[agtIdx][i]}, occIdx{pos[occupiedIdx][j]}") 
                            
                        #println(f"agtIdx{pos[agtIdx][i]}, occIdx{pos[occupiedIdx][j]}") 
                        if pos[agtIdx][i] == pos[occupiedIdx][j]:  #occupiedList[occupiedIdx]:
                            # TODO take boxes into account, this is probably why you get tuple integer problems
                            
                            #println(indicies)
                            println("Collission between agents!")
                            #println(f"agtIdx{pos[agtIdx][i]}, occIdx{pos[occupiedIdx][j]}") 
                            #  ts = traceback steps
                            ts = 0
                            
                            while pos[agtIdx][i + ts] == pos[occupiedIdx][j - ts]:
                                #println(f"agtIdx{pos[agtIdx][i -ts]}, {pos[occupiedIdx][j + ts]}")
                                if j - ts < 0  or i + ts >= len(path):
                                    #This is TODO and occurs when a agent is initialized on the path of another agent
                                    pass
                                
                                ts += 1
                            println(f"{i-ts},{ts}")
                            println(indicies)
                            for k in range(ts):
                                pos[occupiedIdx].insert(j - ts - 1, pos[occupiedIdx][j - ts - 2])
                                #println(paths[agtIdx][j-ts:j-ts+3])
                                #paths[agtIdx].insert(i - ts, "NoOp")
                            # indicies[agtIdx] -= ts
                            #pos[agtIdx].insert(i, pos[agtIdx][i - 1])
                            #println(pos)
                    
                    # newPathLength = 0
                    # for occupiedIdx in range(len(paths)):
                    #     if (paths[occupiedIdx]
                        
                    indicies[agtIdx] += 1
                    changeHappend = True
            
                
        #println([action[-4:-3]])
        println(pos)
        println(paths)
        #for k in range(13):
            #pos[agtIdx].insert(i - ts, pos[agtIdx][i - ts - 1])
            #println(paths[agtIdx][j-ts:j-ts+3])
            #paths[0].insert(0, "NoOp")
            #paths[1].append("NoOp")
        # Doesn't exist?
        
        #  1
        println(self.tasks['a'][0].map)
        #  1
        
        pathLength = 0
        for agt in pos:
            if len(agt) > pathLength:
                pathLength = len(agt)
        pathLength -= 1

        for agt in range(len(pos)):
            for i in range(len(pos[agt]) - 1):
                if pos[agt][i] == pos[agt][i + 1]:
                    paths[agt].insert(i, "NoOp")
            while len(paths[agt]) <= len(pos[agt]):
                paths[agt].append("NoOp")

        println(paths)

        return paths

    def solve_world(self):
        """Solve the top problem."""
        to_del = []
        for goal, val in self.tasks.items():
            task, agent = val
            if agent in self.freed_agents:
                # substitute this task with previous task using the agent
                prev_task = self.freed_agents[agent]
                pos, color = list(task.goals.values())[0][0]
                prev_task.addGoal(goal, pos, color)
                task = prev_task
                task.explored = set()
                to_del.append(goal)
            path, last_state = self.solve_task(task)
            if path is not None:
                self.freed_agents[agent] = last_state
                if goal not in to_del:
                    self.tasks[goal] = (last_state, self.tasks[goal][1])
                prev_goal = list(last_state.goals.keys())[0]
                self.status[prev_goal] = path
                # make sure that we are not removing the correct one
                if prev_goal in to_del:
                    to_del.remove(prev_goal)

        for goal in to_del:
            del self.status[goal]
            del self.tasks[goal]

    def join_tasks(self) -> List:
        """Join all the task in one big path.

        Returns
        -------
        list of actions to the best solution

        """
        # WARNING: ths fails if there are more than 10 agents
        sorted_agents = sorted(
            list(self.status.keys()), key=lambda a: self.agent_to_status[a]
        )
        paths = [self.status[agent] for agent in sorted_agents]
        println(paths)
        new_paths = self.choose_priority_path(paths)
        println(new_paths)
        return [";".join(actions) for actions in zip(*paths)]


def search(strategy: BestFirstSearch) -> List:
    """Search function.

    Returns
    -------
    Path to the solutions (in actions) or none.

    """

    #  Legacy function, but it takes a strategy rather than a leaf as argument
    # return aStarSearch_func(strategy)


    # This version gives an errors in some scenareos
    iterations = 0
    while not strategy.leaf.isGoalState():
        if iterations == 1000:
            println(f"{strategy.count} nodes explored")
            iterations = 0

        if get_usage() > MAX_USAGE:
            raise ResourceLimit("Maximum memory usage exceeded.")
            return None, strategy

        strategy.get_and_remove_leaf()
        '''
        if strategy.frontier_empty():
            println("Frontier empty!")
            return None, strategy
        '''

        if strategy.leaf.isGoalState():
            println(f"Solution found with {len(strategy.leaf.explored)} nodes explored")
            return strategy.walk_best_path(), strategy

        iterations += 1
