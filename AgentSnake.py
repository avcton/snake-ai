import State as ST
from heapdict import heapdict
from State import Vector
import heapq


class Agent(object):
    def SearchSolution(self, state):
        return []

    def _GetMoveCoordinates(self, source: tuple, move: int):
        # X = Cols | Y = Rows
        col, row = source

        if move == 0:
            return (col, row - 1)
        if move == 6:
            return (col, row + 1)
        if move == 3:
            return (col + 1, row)
        if move == 9:
            return (col - 1, row)

    def GenerateMoves(self, state, source: tuple, visited: set, previousMove):
        # List of Potential Moves
        moves = [0, 6, 3, 9]

        # Remove those moves which are invalid
        if previousMove == 0:
            moves.remove(6)
        if previousMove == 6:
            moves.remove(0)
        if previousMove == 3:
            moves.remove(9)
        if previousMove == 9:
            moves.remove(3)

        return {move: self._GetMoveCoordinates(source, move) for move in moves if self.IsValidMove(self._GetMoveCoordinates(source, move), state, visited)}

    def IsValidMove(self, moveCoordinate, state: ST.SnakeState, visited: set):
        # Checking if the move was already visited before
        if moveCoordinate in visited:
            return False

        col, row = moveCoordinate
        # Checking if the move is within the maze
        if col < 0 or col >= state.maze.WIDTH:
            return False

        if row < 0 or row >= state.maze.HEIGHT:
            return False

        # Checking if the move does not lead to a wall
        if state.maze.MAP[row][col] == -1:
            return False

        return True

    def GetPreviousMove(self, state):
        if state.snake.HeadDirection.X == 0 and state.snake.HeadDirection.Y == -1:
            return 0
        if state.snake.HeadDirection.X == 0 and state.snake.HeadDirection.Y == 1:
            return 6
        if state.snake.HeadDirection.X == 1 and state.snake.HeadDirection.Y == 0:
            return 3
        if state.snake.HeadDirection.X == -1 and state.snake.HeadDirection.Y == 0:
            return 9


class AgentSnake(Agent):
    def SearchSolution(self, state):
        FoodX = state.FoodPosition.X
        FoodY = state.FoodPosition.Y

        HeadX = state.snake.HeadPosition.X  # L
        HeadY = state.snake.HeadPosition.Y  # T

        DR = FoodY - HeadY
        DC = FoodX - HeadX

        plan = []

        # Moves
        # 0 = Top
        # 6 = Bottom
        # 9 = Left
        # 3 = Right

        F = -1
        if (DR == 0 and state.snake.HeadDirection.X*DC < 0):
            plan.append(0)
            F = 6

        if (state.snake.HeadDirection.Y*DR < 0):
            plan.append(3)
            if (DC == 0):
                F = 9
            else:
                DC = DC - 1
        Di = 6
        if (DR < 0):
            Di = 0
            DR = -DR
        for i in range(0, int(DR)):
            plan.append(Di)
        Di = 3
        if (DC < 0):
            Di = 9
            DC = -DC
        for i in range(0, int(DC)):
            plan.append(Di)
        if (F > 0):
            plan.append(F)
            F = -1

        return plan

    def showAgent():
        print("A Snake Solver By MB")

# You code of agent goes here
# You must create three agents one using A*, second using greedy best first search and third using an uninformed algo of your choice to make a plan


class AStarSearch(Agent):
    def SearchSolution(self, state: ST.SnakeState):
        source = (state.snake.HeadPosition.X, state.snake.HeadPosition.Y)
        goal = (state.FoodPosition.X, state.FoodPosition.Y)

        # Fetching last move: to stop the snake from turning 360°
        previousMove = self.GetPreviousMove(state)

        plan = []
        body = [(BodyFragment.X, BodyFragment.Y) for BodyFragment in state.snake.Body]
        visited = set()
        heap = heapdict()
        heap[source] = (0, 0, body, plan)  # TotalCost + SourceCost + Body + Moves

        while heap:
            node, data = heap.popitem()
            _, sourceCost, body, currentPlan = data
            visited.add(node)

            if node == goal:
                plan = currentPlan
                if len(plan) == 0:
                    print('Food at Same Location: No need to move')
                break

            # We have taken a single path here thus updating body
            for i, _ in enumerate(body):
                if i == len(body) - 1:
                    # This fragment is right behind the snake
                    body[i] = node
                else:
                    # Updating the rest of the body
                    body[i] = body[i + 1]

            if node != source:
                # Updating previous move to avoid foul move
                previousMove = currentPlan[-1]

            Moves = self.GenerateMoves(
                state, node, visited, previousMove)

            for move, moveCoordinate in Moves.items():
                moveSourceCost = sourceCost + 1
                moveHeuristic = abs(moveCoordinate[0] - goal[0]) + \
                    abs(moveCoordinate[1] - goal[1])
                
                # Dealing heuristics if we hit the snake body
                if moveCoordinate in body:
                    depthFactor = state.maze.HEIGHT * state.maze.WIDTH
                    moveHeuristic += depthFactor
                    # moveHeuristic = 10^20

                currentMoveCost = moveSourceCost + moveHeuristic
                previousMoveCost = heap.get(
                    moveCoordinate, (float('inf'), None))[0]

                if currentMoveCost < previousMoveCost:
                    heap[moveCoordinate] = (
                        currentMoveCost, moveSourceCost, [*body], [*currentPlan, move])

        print(plan)
        return plan


class GreedyBestFirstSearch(Agent):
    def SearchSolution(self, state: ST.SnakeState):
        source = state.snake.HeadPosition.getTuple()
        goal = state.FoodPosition.getTuple()

        plan = []
        visited = set()
        queue = [(abs(source[0] - goal[0]) + abs(source[1] - goal[1]), source, plan)]  # Heuristic + Node + Plan
        previousMove = self.GetPreviousMove(state)

        while queue:
            _, node, currentPlan = heapq.heappop(queue)
            visited.add(node)

            if node[0] == goal[0] and node[1] == goal[1]:
                plan = currentPlan
                break

            Moves = self.GenerateMoves(
                state, node, visited, previousMove if node == source else -1)

            for move, moveCoordinate in Moves.items():
                moveHeuristic = abs(moveCoordinate[0] - goal[0]) + abs(moveCoordinate[1] - goal[1])
                heapq.heappush(queue,(moveHeuristic, moveCoordinate, [*currentPlan, move]))

        return plan

class UniformCostSearch(Agent):
    def SearchSolution(self, state: ST.SnakeState):
        source = state.snake.HeadPosition.getTuple()
        goal = state.FoodPosition.getTuple()

        plan = []
        visited = set()
        cost = {source: 0}
        queue = [(0, source, plan)]  # Cost + Node + Plan
        previousMove = self.GetPreviousMove(state)

        while queue:
            currentCost, node, currentPlan = heapq.heappop(queue)
            visited.add(node)

            if node[0] == goal[0] and node[1] == goal[1]:
                plan = currentPlan
                break

            if currentCost > cost[node]:
                continue  # Skip if we have already found a cheaper path to this node

            Moves = self.GenerateMoves(
                state, node, visited, previousMove if node == source else -1)

            for move, moveCoordinate in Moves.items():
                moveCost = 1  # Uniform cost for each move
                totalCost = cost[node] + moveCost

                if moveCoordinate not in cost or totalCost < cost[moveCoordinate]:
                    cost[moveCoordinate] = totalCost
                    heapq.heappush(queue, (totalCost, moveCoordinate, [*currentPlan, move]))

        return plan

