# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
import copy

from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#global variable for store currently carried food number of every agent
carriedFood = dict()
for i in range(0,4):
  carriedFood[i] = 0

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AttackAgent', second = 'AttackAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    middleLine = self.getMiddleLine(gameState)
    mapMatrix = self.getMapMatrix(gameState)
    print(mapMatrix)
    # print(middleLine)

  def getMiddleLine(self, gameState):
    middleLine = []
    mapWidth = gameState.data.layout.width
    mapHeight = gameState.data.layout.height
    if self.red:
      x = int((mapWidth - 2) / 2)
    else:
      x = int((mapWidth - 2) / 2 + 1)
    wallList = gameState.getWalls().asList()
    for y in range(1, mapHeight):
      if (x, y) not in wallList:
        middleLine.append((x,y))
    return middleLine

  def getMapMatrix(self, gameState):
    """
    Start counting from the top-left corner

    0 1 2 ➡
    1
    2
    ⬇

    0: Walls
    1: Available movements
    2: RedFood
    3: RedCapsule
    4: BlueFood
    5: BlueCapsule
    """
    mapMatrix = gameState.deepCopy().data.layout.layoutText
    mapHeight = len(mapMatrix)
    for i in range(mapHeight):
      mapMatrix[i] = mapMatrix[i].replace('%', '0')
      mapMatrix[i] = mapMatrix[i].replace(' ', '1')
      mapMatrix[i] = mapMatrix[i].replace('.', '1')
      mapMatrix[i] = mapMatrix[i].replace('o', '1')
      mapMatrix[i] = mapMatrix[i].replace('1', '1')
      mapMatrix[i] = mapMatrix[i].replace('2', '1')
      mapMatrix[i] = mapMatrix[i].replace('3', '1')
      mapMatrix[i] = mapMatrix[i].replace('4', '1')
      mapMatrix[i] = list(mapMatrix[i])
      mapMatrix[i] = list(map(float, mapMatrix[i]))
    for redFood in gameState.getRedFood().asList():
      x = redFood[0]
      y = mapHeight - 1 - redFood[1]
      mapMatrix[y][x] = 2.0
    for redCapsule in gameState.getRedCapsules():
      if not redCapsule:
        continue
      x = redCapsule[0]
      y = mapHeight - 1 - redCapsule[1]
      mapMatrix[y][x] = 3.0
    for blueFood in gameState.getBlueFood().asList():
      x = blueFood[0]
      y = mapHeight - 1 - blueFood[1]
      mapMatrix[y][x] = 4.0
    for blueCapsule in gameState.getBlueCapsules():
      if not blueCapsule:
        continue
      x = blueCapsule[0]
      y = mapHeight - 1 - blueCapsule[1]
      mapMatrix[y][x] = 5.0
    return mapMatrix

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
    return random.choice(actions)




class AttackAgent(CaptureAgent):

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState) # must be put ahead to set value of self.red
    global carriedFood
    carriedFood[self.index] = 0
    self.walls = gameState.getWalls()
    self.middleX = self.getMiddleX(gameState)
    self.enemyMiddleX = self.getEnemyMiddleX(gameState)
    self.middleLine = self.getMiddleLine(gameState)
    self.enemyMiddleLine = self.getEnemyMiddleLine(gameState)
    self.reachMiddleListProblem = ReachMiddleListProblem(gameState, self.index, self.middleX, self.enemyMiddleX, self.middleLine, self.enemyMiddleLine)
    self.attackProblem = AttackProblem(gameState, self.index, self.middleX, self.enemyMiddleX, self.middleLine, self.enemyMiddleLine)

  def getMiddleX(self, gameState):
    mapWidth = gameState.data.layout.width
    if self.red:
      x = int((mapWidth - 2) / 2)
    else:
      x = int((mapWidth - 2) / 2 + 1)
    return x

  def getEnemyMiddleX(self, gameState): # x of middle line on enemy's side
    mapWidth = gameState.data.layout.width
    if self.red:
      enemyX = int((mapWidth - 2) / 2 + 1)
    else:
      enemyX = int((mapWidth - 2) / 2)
    return enemyX

  def getMiddleLine(self, gameState):
    middleLine = []
    mapHeight = gameState.data.layout.height
    x = self.middleX
    wallList = gameState.getWalls().asList()
    for y in range(1, mapHeight):
      if (x, y) not in wallList:
        middleLine.append((x,y))
    return middleLine

  def getEnemyMiddleLine(self, gameState):
    enemyMiddleLine = []
    mapHeight = gameState.data.layout.height
    x = self.enemyMiddleX
    wallList = gameState.getWalls().asList()
    for y in range(1, mapHeight):
      if (x, y) not in wallList:
        enemyMiddleLine.append((x, y))
    return enemyMiddleLine

  def chooseAction(self, gameState):
    # TODO:
    #  go to middle Line,
    #  eat up to 10 [if ghost in sight then run back,
    #  or go back to middle line when pac man is with food],
    #  go back to middle line.
    curPos = gameState.getAgentPosition(self.index)
    """judge if the pac man died in last turn to reset carriedFood value"""
    prevGameState = self.getPreviousObservation()
    if prevGameState != None:
      if (prevGameState.getAgentPosition(self.index)[0] - self.getMiddleX(gameState)) * (curPos[0] - self.getMiddleX(gameState)) < 0:
        print("pacman ",self.index," died!")
        carriedFood[self.index] = 0

    #TODO: use getAgentPosition(enemy.index) to judge if ghost is within agent's sight:
    # if not, the func will return a noneType value;
    if self.red:
      # TODO: if ghost in sight of 5 real distance, go back to middleLine[consider midline and ghost]
      #   if distance to middle list smaller than distance to the closest ghost
      if carriedFood[self.index] == self.attackProblem.targetFoodNum:
        if curPos[0] <= self.getMiddleX(gameState):
          carriedFood[self.index] = 0
        else:
          # TODO: go back to midline
          pass
      else: # need to eat more food
        #go to the middle line
        if curPos[0] <= self.getMiddleX(gameState):
          return self.aStarSearch(self.reachMiddleListProblem, gameState, self.reachMiddleListHeuristic)[0]
        else: # search for more food
          if curPos in self.getFood(gameState).asList():
            carriedFood[self.index] += 1 # manually update carried food number
          a=self.aStarSearch(self.attackProblem, gameState, self.attackHeuristic)[0]
          print(a)

          return a
    else: # pac man is of blue side
      # TODO: if ghost in sight of 5 real distance, go back to middleLine[consider midline and ghost]
      #   if distance to middle list smaller than distance to the closest ghost
      if carriedFood[self.index] == self.attackProblem.targetFoodNum:
        if curPos[0] >= self.getMiddleX(gameState):
          carriedFood[self.index] = 0
        else:
          # TODO: go back to midline
          pass
      else: # need to eat more food
        #go to the middle line
        if curPos[0] >= self.getMiddleX(gameState):
          return self.aStarSearch(self.reachMiddleListProblem, gameState, self.reachMiddleListHeuristic)[0]
        else: # search for more food
          if curPos in self.getFood(gameState).asList():
            carriedFood[self.index] += 1 # manually update carried food number
          return self.aStarSearch(self.attackProblem, gameState, self.attackHeuristic)[0]

  def aStarSearch(self, problem, gameState, heuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    # print("doing astar")
    # import time
    # print("starttime:",time.clock())
    # init
    visited = set()
    best_g = dict()
    """state: [position, foodGrid, food]"""
    """state, action list, cost value g"""
    start_node = (problem.getStartState(gameState, self.getFood(gameState)), [], 0)
    frontier = util.PriorityQueue()
    priority = heuristic(gameState, problem.getStartState(gameState, self.getFood(gameState)))  # f = h + g(start is 0)
    frontier.push(start_node, priority)

    while not frontier.isEmpty():
      current_node = frontier.pop()
      if current_node[0] in best_g.keys():  # reopen
        if best_g[current_node[0]] > current_node[2]:
          best_g[current_node[0]] = current_node[2]
          for successor in problem.getSuccessors(current_node[0]):
            cost_g = current_node[2] + successor[2]
            priority = cost_g + heuristic(gameState, successor[0])
            path = current_node[1] + [successor[1]]
            frontier.push((successor[0], path, cost_g), priority)
      elif current_node[0] not in visited:
        best_g[current_node[0]] = current_node[2]
        visited.add(current_node[0])
        if problem.isGoalState(current_node[0]):
          # print("endtime1:",time.clock())
          print("current_node:",current_node)
          return current_node[1]
        else:
          for successor in problem.getSuccessors(current_node[0]):
            cost_g = current_node[2] + successor[2]
            priority = cost_g + heuristic(gameState, successor[0])
            path = current_node[1] + [successor[1]]
            frontier.push((successor[0], path, cost_g), priority)

    # print("endtime2:",time.clock())

  def attackHeuristic(self, gameState, state): # target on eating

    """
    used for attack agent
    dist(P,Food): to the nearest x food positions[x = foodToEat]
      + x1 * dist(P,middleLine)(mean for distances to middle line positions)
      - x2 * dist(P,P2)
    @:param index: index of agent the heuristic is used on
            state: [(x, y), foodGrid, foodToEat]
    """
    curPos, foodGrid, foodToEat = state
    foodList = copy.deepcopy(foodGrid.asList())
    sumFoodDist = 0
    closed = [curPos] # food in path calculated
    while foodToEat > 0:
      minDistToFood = 999999
      for food in foodList:
        for pos in closed:
          newDist = self.getMazeDistance(pos, food)
          if newDist < minDistToFood:
            minDistToFood = newDist
            nearestFoodPos = food
      foodList.remove(nearestFoodPos)
      closed.append(nearestFoodPos)
      foodToEat -= 1
      sumFoodDist += minDistToFood

    # midAccesses = self.getMiddleLine(gameState)
    # minDistToMid = 999999
    # for midPos in midAccesses:
    #   for closedPos in closed:
    #     newDist = self.getMazeDistance(closedPos, midPos)
    #     if newDist < minDistToMid:
    #       minDistToMid = newDist
    #
    # teamIds = self.getTeam(gameState)  # teammate index
    # for idx in teamIds:
    #   if idx != self.index:
    #     tmPos = gameState.getAgentPosition(idx)
    #     # find pos of the other pac man and calculate distance
    #     distToTm = self.getMazeDistance(curPos, tmPos)
    #     break

    x = 0.4
    # return sumFoodDist + minDistToMid - x * distToTm
    return sumFoodDist

  def reachMiddleListHeuristic(self, gameState, state): # reach the side of our own on the middle list
    curPos = state[0]
    middleList = self.getEnemyMiddleLine(gameState)
    minDistToMid = 999999
    for midPoint in middleList:
      newDist = self.getMazeDistance(curPos, midPoint)
      if newDist < minDistToMid:
        minDistToMid = newDist

    return minDistToMid


class AttackProblem:
  def __init__(self, gameState, index, midX, enemyMidX, midLine, enemyMidLine):
    # number of food to be eat that is used in policy selection
    # change to be applied in a new heuristic
    global carriedFood
    self.targetFoodNum = 1
    self.index = index
    self.walls = gameState.getWalls()
    self.middleX = midX
    self.enemyMiddleX = enemyMidX
    self.middleLine = midLine
    self.enemyMiddleLine = enemyMidLine
    self.carriedFood = 0
    #TODO： temporarily used hard coded carriedFood
    # self.carriedFood = carriedFood[self.index]

  def getStartState(self, gameState, foodGrid):
    return (gameState.getAgentPosition(self.index), foodGrid, self.targetFoodNum - self.carriedFood)
    #TODO： temporarily used hard coded carriedFood
    #return (gameState.getAgentPosition(self.index), foodGrid, self.targetFoodNum - carriedFood[self.index])

  def isGoalState(self, state):
    print("self.carriedFood:",self.carriedFood)
    return self.carriedFood == self.targetFoodNum
    # return state[0] in self.middleLine and carriedFood[self.index] == self.targetFoodNum

  def getSuccessors(self, state):
    successors = []
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]: #if STOP needed?
      x, y = state[0]
      dx, dy = game.Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if not self.walls[nextx][nexty]:
        nextFood = state[1].copy()
        if (nextx,nexty) in state[1].asList(): # successor in enemy's place
          nextFood[nextx][nexty] = False
          self.carriedFood += 1
          # TODO： temporarily used hard coded carriedFood
          # successors.append((((nextx, nexty), nextFood, state[2]-1), direction, 1))
        else:
          pass
          # TODO： temporarily used hard coded carriedFood
          # successors.append((((nextx, nexty), nextFood, state[2]), direction, 1))
        successors.append((((nextx, nexty), nextFood, self.targetFoodNum - self.carriedFood), direction, 1))
    return successors

class ReachMiddleListProblem:
  def __init__(self, gameState, index, midX, enemyMidX, midLine, enemyMidLine):
    self.index = index
    self.walls = gameState.getWalls()
    self.middleX = midX
    self.enemyMiddleX = enemyMidX
    self.middleLine = midLine
    self.enemyMiddleLine = enemyMidLine

  def getStartState(self, gameState, foodGrid):
    return (gameState.getAgentPosition(self.index), )

  def isGoalState(self, state):
    return state[0][0] == self.enemyMiddleX

  def getSuccessors(self, state):
    successors = []
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = state[0]
      dx, dy = game.Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if not self.walls[nextx][nexty]:
        successors.append((((nextx, nexty),), direction, 1))
    return successors
