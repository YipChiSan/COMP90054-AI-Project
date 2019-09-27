import copy

from myTeam import AttackAgent
from game import *
from collections import defaultdict


class EatOneProblem:
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
    self.carriedFood = carriedFood[self.index]

  def getStartState(self, gameState, foodGrid):
    return (gameState.getAgentPosition(self.index), foodGrid, self.targetFoodNum - self.carriedFood)

  def isGoalState(self, gameState, state):
    return self.carriedFood == self.targetFoodNum
    # return state[0] in self.middleLine and carriedFood[self.index] == self.targetFoodNum

  def getSuccessors(self, state):
    successors = []
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]: #if STOP needed?
      x, y = state[0]
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if not self.walls[nextx][nexty]:
        nextFood = state[1].copy()
        if (nextx,nexty) in state[1].asList(): # successor in enemy's place
          nextFood[nextx][nexty] = False
          self.carriedFood += 1
        successors.append((((nextx, nexty), nextFood, self.targetFoodNum - self.carriedFood), direction, 1))
    return successors

class EatWithDeadEndProblem: # default: eat one
  def __init__(self, gameState, index, midX, enemyMidX, midLine, enemyMidLine):
    global carriedFood
    self.targetFoodNum = 1
    self.index = index
    self.deadEnds = AttackAgent.deadEnds
    self.walls = gameState.getWalls() + self.deadEnds # add deadEnd points to walls
    self.middleX = midX
    self.enemyMiddleX = enemyMidX
    self.middleLine = midLine
    self.enemyMiddleLine = enemyMidLine
    self.carriedFood = carriedFood[self.index]

  def getStartState(self, gameState, foodGrid):
    for pos in self.deadEnds: # deadEnd foods are considered nothing
      foodGrid[pos[0]][pos[1]] = False
    return (gameState.getAgentPosition(self.index), foodGrid, self.targetFoodNum - self.carriedFood)

  def isGoalState(self, gameState, state):
    return self.carriedFood == self.targetFoodNum
    # return state[0] in self.middleLine and carriedFood[self.index] == self.targetFoodNum

  def getSuccessors(self, state):
    successors = []
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:  # if STOP needed?
      x, y = state[0]
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if not self.walls[nextx][nexty]:
        nextFood = state[1].copy()
        if (nextx, nexty) in state[1].asList():  # successor in enemy's place
          nextFood[nextx][nexty] = False
          self.carriedFood += 1
        successors.append((((nextx, nexty), nextFood, self.targetFoodNum - self.carriedFood), direction, 1))
    return successors

class EatCapsuleProblem:
  def __init__(self, gameState, index, midX, enemyMidX, midLine, enemyMidLine):
    self.index = index
    self.walls = gameState.getWalls()
    self.middleX = midX
    self.enemyMiddleX = enemyMidX
    self.middleLine = midLine
    self.enemyMiddleLine = enemyMidLine
    self.capsules = AttackAgent.getCapsules()

  def getStartState(self, gameState, foodGrid):
    return (gameState.getAgentPosition(self.index), self.capsules)

  def isGoalState(self, gameState, state):
    for capPos in state[1]:
      if capPos == (-1,-1):
        return True
    return False

  def getSuccessors(self, state):
    successors = []
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]: #if STOP needed?
      x, y = state[0]
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if not self.walls[nextx][nexty]:
        for idx,(x,y) in enumerate(self.capsules):
          if x == nextx and y == nexty:
            self.capsules[idx] = (-1,-1)
        successors.append((((nextx, nexty), self.capsules), direction, 1))
    return successors

class EscapeProblem:
  def __init__(self, gameState, index, enemyIndices, midX, enemyMidX, midLine, enemyMidLine):
    self.index = index
    self.pacmanPos = gameState.getAgentPosition(index)
    self.deadEnds = AttackAgent.deadEnds
    self.walls = gameState.getWalls() + self.deadEnds # add deadEnd points to walls
    self.middleX = midX
    self.enemyMiddleX = enemyMidX
    self.middleLine = midLine
    self.enemyMiddleLine = enemyMidLine
    self.enemyIndices = enemyIndices
    self.enemyPositions = set() # in sight enemies
    for idx in self.enemyIndices:
      enemyPos = gameState.getAgentPosition(idx)
      if enemyPos != None:
        self.enemyPositions.add(enemyPos)
    self.expandedForbidden = defaultdict(set()) # key is the expanded time

  def storeExpandedForbidden(self, step):
    # return a expanded wall list from original one
    if step == 1:
      for enemyPos in self.enemyPositions:
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
          x, y = enemyPos
          dx, dy = Actions.directionToVector(direction)
          nextx, nexty = int(x + dx), int(y + dy)
          if not self.walls[nextx][nexty]:
            self.expandedForbidden[step].add((nextx, nexty))
    else:
      for pos in self.expandedForbidden[step - 1]:
        if step > 2:
          if pos not in self.expandedForbidden[step-2]:
            for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
              x, y = pos
              dx, dy = Actions.directionToVector(direction)
              nextx, nexty = int(x + dx), int(y + dy)
              if (not self.walls[nextx][nexty]) and ((nextx, nexty) not in self.expandedForbidden[step-1]):
                self.expandedForbidden[step].add((nextx, nexty))
        else:
          for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = pos
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if (not self.walls[nextx][nexty]) and ((nextx, nexty) not in self.expandedForbidden[step-1]):
              self.expandedForbidden[step].add((nextx, nexty))
      self.expandedForbidden[step].update(self.expandedForbidden[step - 1])

  def getStartState(self, gameState, foodGrid):
    self.storeExpandedForbidden(1)
    return (gameState.getAgentPosition(self.index), self.expandedForbidden[1], 1)

  def isGoalState(self, gameState, state):
    return state[0][0] == self.middleX

  def getSuccessors(self, state):
    successors = []
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = state[0]
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if (not self.walls[nextx][nexty]) and ((nextx,nexty) not in self.expandedForbidden[state[2]]):
        if self.expandedForbidden[state[2]+1] == None:
          self.storeExpandedForbidden(state[2]+1)
        successors.append(((nextx, nexty), self.expandedForbidden[state[2]+1], state[2]+1), direction, 1)
    return successors

class DefendingProblem:
  #TODO: [reach the change element in two situations]: enemy in sight/foodGrid change
  pass

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

  def isGoalState(self, gameState, state):
    return state[0][0] == self.enemyMiddleX

  def getSuccessors(self, state):
    successors = []
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = state[0]
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if not self.walls[nextx][nexty]:
        successors.append((((nextx, nexty),), direction, 1))
    return successors

class BackToMiddleListProblem:
  def __init__(self, gameState, index, midX, enemyMidX, midLine, enemyMidLine):
    self.index = index
    self.walls = gameState.getWalls()
    self.middleX = midX
    self.enemyMiddleX = enemyMidX
    self.middleLine = midLine
    self.enemyMiddleLine = enemyMidLine

  def getStartState(self, gameState, foodGrid):
    return (gameState.getAgentPosition(self.index),)

  def isGoalState(self, gameState, state):
    return state[0][0] == self.middleX

  def getSuccessors(self, state):
    successors = []
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = state[0]
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if not self.walls[nextx][nexty]:
        successors.append((((nextx, nexty),), direction, 1))
    return successors


def eatOneHeuristic(agent, state): # target on eating
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
        newDist = agent.getMazeDistance(pos, food)
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

  # x = 0.4
  # return sumFoodDist + minDistToMid -  distToTm
  return sumFoodDist

def eatWithDeadEndHeuristic(agent, state):
  curPos, foodGrid, foodToEat = state
  foodList = copy.deepcopy(foodGrid.asList())
  sumFoodDist = 0
  closed = [curPos]  # food in path calculated
  while foodToEat > 0:
    minDistToFood = 999999
    for food in foodList:
      for pos in closed:
        newDist = agent.getMazeDistance(pos, food)
        if newDist < minDistToFood:
          minDistToFood = newDist
          nearestFoodPos = food
    foodList.remove(nearestFoodPos)
    closed.append(nearestFoodPos)
    foodToEat -= 1
    sumFoodDist += minDistToFood
  return sumFoodDist

def eatCapsuleHeuristic(agent, state):
  curPos, capsuleList = state
  minDistToCapsule = 999999
  for capsule in capsuleList:
      newDist = agent.getMazeDistance(curPos, capsule)
      if newDist < minDistToCapsule:
        minDistToCapsule = newDist
  return minDistToCapsule

def escapeHeuristic(agent, state):
  return backToMiddleListHeuristic(agent, state)

def denfendingHeuristic(self, state):
  # TODO:
  pass

def reachMiddleListHeuristic(agent, state): # reach the side of our own on the middle list
  curPos = state[0]
  enemyMiddleList = agent.enemyMiddleLine
  minDistToMid = 999999
  for midPoint in enemyMiddleList:
    newDist = agent.getMazeDistance(curPos, midPoint)
    if newDist < minDistToMid:
      minDistToMid = newDist

  return minDistToMid

def backToMiddleListHeuristic(agent, state): # reach the side of our own on the middle list
  curPos = state[0]
  middleList = agent.middleLine
  minDistToMid = 999999
  for midPoint in middleList:
    newDist = agent.getMazeDistance(curPos, midPoint)
    if newDist < minDistToMid:
      minDistToMid = newDist

  return minDistToMid

