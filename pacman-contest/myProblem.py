import copy

from myTeam import *
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
    self.walls = gameState.getWalls() # add deadEnd points to walls
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

class DefendingProblem:
  #TODO: [reach the change element in two situations]: enemy in sight/foodGrid change
  pass

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
    self.enemyIndices = AttackAgent.getOpponents()
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

def defendingHeuristic(self, state):
  # TODO:
  pass

def escapeHeuristic(agent, state):
  curPos = state[0]
  middleList = agent.middleLine
  minDistToMid = 999999
  for midPoint in middleList:
    newDist = agent.getMazeDistance(curPos, midPoint)
    if newDist < minDistToMid:
      minDistToMid = newDist
  return minDistToMid


def getActualWalls(agent):
  walls = agent.getWalls()
  return walls

def getWallsWithDeadEnd(agent):
  walls = agent.walls
  deadEnds = agent.deadEnds
  for pos in deadEnds:
    walls[pos[0]][pos[1]] = True
  return walls

#find shortest path, to any pos in posList
def minDistance(pos, posList, walls, agent):
  minDist = 9999
  action = Directions.NORTH
  for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:  # if STOP needed?
    x, y = pos
    dx, dy = Actions.directionToVector(direction)
    nextx, nexty = int(x + dx), int(y + dy)
    if not walls[nextx][nexty]:
      for target in posList:
        dist = agent.getMazeDistance((nextx, nexty), target)
        if dist < minDist:
          minDist = dist
          action = direction
  return action

def getFoodExceptDeadEnds(agent, gameState):
  food = agent.getFood(gameState)
  for pos in agent.deadEnds:
    food[pos[0]][pos[1]] = False
  foodList = food.asList()
  return foodList

def eatOneFood(agent, gameState, index):
  food = agent.getFood(gameState)
  foodList = food.asList()
  pos = gameState.getAgentPosition(index)
  walls = gameState.getWalls()
  #walls = getActualWalls(agent)
  action = minDistance(pos, foodList, walls, agent)
  return action

def eatFoodOutsideDeadEnd(agent, gameState, index):
  foodList = getFoodExceptDeadEnds(agent, gameState)
  pos = gameState.getAgentPosition(index)
  walls = getWallsWithDeadEnd(agent)
  action = minDistance(pos, foodList, walls, agent)
  return action

def eatCapsule(agent, gameState, index):
  capsuleList = agent.getCapsules()
  pos = gameState.getAgentPosition(index)
  walls = getActualWalls(agent)
  action = minDistance(pos, capsuleList, walls, agent)
  return action

def reachOwnMidList(agent, gameState, index):
  middleList = agent.middleLine
  pos = gameState.getAgentPosition(index)
  walls = getActualWalls(agent)
  action = minDistance(pos, middleList, walls, agent)
  return action

def reachEnemyMidList(agent, gameState, index):
  enemyMiddleList = agent.enemyMiddleLine
  pos = gameState.getAgentPosition(index)
  walls = getActualWalls(agent)
  action = minDistance(pos, enemyMiddleList, walls, agent)
  return action

def eatFoodClosestToMidList(agent, gameState, index):
  midList = agent.middleLine
  foodList = getFoodExceptDeadEnds(agent, gameState)
  pos = gameState.getAgentPosition(index)
  walls = getWallsWithDeadEnd(agent)
  minDist = 9999
  for midPos in midList:
    x, y = midPos
    if not walls[x][y]:
      for target in foodList:
        dist = agent.getMazeDistance((x, y), target)
        if dist < minDist:
          minDist = dist
          minDistFoodPos = target
  action = minDistance(pos, [minDistFoodPos], walls, agent)
  return action

def eatClosestGhost(agent, gameState, index):
  ghostIndices = agent.getOpponents(gameState)
  ghostList = []
  for idx in ghostIndices:
    enemyPos = gameState.getAgentPosition(idx)
    if enemyPos != None:
      ghostList.append(enemyPos)
  pos = gameState.getAgentPosition(index)
  walls = getWallsWithDeadEnd(agent)
  action = minDistance(pos, ghostList, walls, agent)
  return action

def eatFarthestFoodFromGhost(agent, gameState, index):
  pass
  # fixme: blocked
  # enemyIndices = agent.getOpponents()
  # enemyPosList = [gameState.getAgentPosition()]
  # pos = gameState.getAgentPosition(index)
  # walls = getWallsWithDeadEnd(agent)
  # action = minDistance(pos, foodList, walls, agent)
  # return action

def foolGhost(agent, gameState, index):
  ghostIndices = agent.getOpponents(gameState)
  ghostList = []
  for idx in ghostIndices:
    enemyPos = gameState.getAgentPosition(idx)
    if enemyPos != None:
      ghostList.append(enemyPos)
  pos = gameState.getAgentPosition(index)
  walls = getWallsWithDeadEnd(agent)
  action = minDistance(pos, ghostList, walls, agent)
  return action


class EatOneSafeFoodProblem:
  def __init__(self, gameState, index, enemyIndices, midX, enemyMidX, midLine, enemyMidLine,agent):
    self.index = index
    self.agent = agent
    self.pacmanPos = gameState.getAgentPosition(index)
    self.deadEnds = agent.deadEnd
    self.walls = gameState.getWalls()
    #for i in self.deadEnds:
    #  self.walls[i[1]][i[0]] = True
    # add deadEnd points to walls
    self.middleX = midX
    self.enemyMiddleX = enemyMidX
    self.middleLine = midLine
    self.enemyMiddleLine = enemyMidLine
    self.enemyIndices = agent.getOpponents(gameState)
    self.foods = agent.getFood(gameState)
    self.foodList = self.foods.asList()
    self.enemyPositions = []
    for idx in self.enemyIndices:
      enemyPos = gameState.getAgentPosition(idx)
      if enemyPos != None:
        self.enemyPositions.append(enemyPos)
    self.enemyPositions = tuple(self.enemyPositions)
    #self.expandedForbidden = defaultdict(set()) # key is the expanded time

  def getStartState(self, gameState, foodGrid):
    return (gameState.getAgentPosition(self.index), self.enemyPositions, self.foods,1,0)

  def isGoalState(self, gameState, state):
    return (len(state[2].asList()) < len(self.foods.asList())) or (state[3]>100)

  def getSuccessors(self, state):
    successors = []
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = state[0]
      expandedForbidden = self.getExpandedForbidden(state[1])
      newEnemyList = self.getNewEnemyPostion(state[0],expandedForbidden)
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if (not self.walls[nextx][nexty]) and ((nextx,nexty) not in expandedForbidden):#self.testValid((nextx,nexty),state[1],state[3]):
        # if self.expandedForbidden[state[2]+1] == None:
        #   self.storeExpandedForbidden(state[2]+1)
        numDE = state[4]
        closeDist = 999
        for enemy in newEnemyList:
          if not enemy is None:
            dis = self.agent.getMazeDistance((nextx,nexty),enemy)
            closeDist = min(closeDist,dis)
        print("test for deadEnd",(nextx,nexty),self.deadEnds)
        if ((nexty,nextx) in self.deadEnds):
            numDE += 1
        if closeDist-1 > numDE:
          nextFood = state[2].copy()
          nextFood[nextx][nexty] = False
          successors.append((((nextx, nexty), newEnemyList, nextFood, state[3]+1,numDE), direction,1))
    return successors

  def eatOneSafeHeuristic(self,state):
    curPos, enemy, foods,step,dead = state
    minDist = 9999
    foodList = copy.deepcopy(foods.asList())
    for food in foodList:
        dis = self.agent.getMazeDistance(curPos,food)
        minDist = min(minDist,dis)
    return minDist

  def getNewEnemyPostion(self,pos,enemyList):
    newEnemyList = []
    minDist = 9999
    for enemy in enemyList:
      print("enemy",enemy)
      if not self.walls[enemy[0]][enemy[1]]:
        dis = self.agent.getMazeDistance(pos,enemy)
        if dis == minDist:
          newEnemyList.append((enemy[0],enemy[1]))
        if dis < minDist:
          minDist = dis
          newEnemyList = []
          newEnemyList.append(enemy)
    return tuple(newEnemyList)


  def testValid(self,pos,enemyList,step):
    for enemy in enemyList:
      if self.agent.getMazeDistance(pos,enemy) <= step:
        return False
    return True

  def getExpandedForbidden(self,enemyList):
    expandedForbidden = []
    for enemy in enemyList:
      expandedForbidden.append(enemy)
      (x,y) = enemy
      for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
        dx, dy = Actions.directionToVector(direction)
        expandedForbidden.append((int(x+dx),int(y+dy)))
    return expandedForbidden

def getMiddleLineHeuristic(agent,state):
  curPos,enemy,foods = state
  middleLine = agent.middleLine
  minDist = 9999
  for mid in middleLine:
    minDist = min(minDist,agent.getMazeDistance(curPos,mid))
  return minDist


    #
    # sumFoodDist = 0
    # closed = [curPos] # food in path calculated
class EscapeProblem1:
  def __init__(self, gameState, index, enemyIndices, midX, enemyMidX, midLine, enemyMidLine,agent):
    self.index = index
    self.agent = agent
    self.pacmanPos = gameState.getAgentPosition(index)
    self.deadEnds = agent.deadEnd
    self.walls = gameState.getWalls()
    self.middleX = midX
    self.enemyMiddleX = enemyMidX
    self.middleLine = midLine
    self.enemyMiddleLine = enemyMidLine
    self.enemyIndices = agent.getOpponents(gameState)
    self.foods = agent.getFood(gameState)
    self.foodList = self.foods.asList()
    self.enemyPositions = []
    for idx in self.enemyIndices:
      enemyPos = gameState.getAgentPosition(idx)
      if enemyPos != None:
        self.enemyPositions.append(enemyPos)
    self.enemyPositions = tuple(self.enemyPositions)
    #self.expandedForbidden = defaultdict(set()) # key is the expanded time

  def getStartState(self, gameState, foodGrid):
    return (gameState.getAgentPosition(self.index), self.enemyPositions)

  def isGoalState(self, gameState, state):
    return state[0][0] == self.middleX

  def getSuccessors(self, state):
    successors = []
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = state[0]
      expandedForbidden = self.getExpandedForbidden(state[1])
      newEnemyList = self.getNewEnemyPostion(state[0],expandedForbidden)
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if (not self.walls[nextx][nexty]) and ((nextx,nexty) not in expandedForbidden):#self.testValid((nextx,nexty),state[1],state[3]):
        # if self.expandedForbidden[state[2]+1] == None:
        #   self.storeExpandedForbidden(state[2]+1)
        nextFood = state[2].copy()
        nextFood[nextx][nexty] = False
        successors.append((((nextx, nexty), newEnemyList), direction, 1))
    return successors

  def EscapeHeuristic(self,state):
    middleLine = self.agent.middleLine
    print(state)
    curPos, enemy = state
    minDist = 9999
    for mid in middleLine:
      minDist = min(minDist,self.agent.getMazeDistance(curPos,mid))
    return minDist

  def getNewEnemyPostion(self,pos,enemyList):
    newEnemyList = []
    minDist = 9999
    for enemy in enemyList:
      print("enemy",enemy)
      if not self.walls[enemy[0]][enemy[1]]:
        dis = self.agent.getMazeDistance(pos,enemy)
        if dis == minDist:
          newEnemyList.append((enemy[0],enemy[1]))
        if dis < minDist:
          minDist = dis
          newEnemyList = []
          newEnemyList.append(enemy)
    return tuple(newEnemyList)


  def testValid(self,pos,enemyList,step):
    for enemy in enemyList:
      if self.agent.getMazeDistance(pos,enemy) <= step:
        return False
    return True

  def getExpandedForbidden(self,enemyList):
    expandedForbidden = []
    for enemy in enemyList:
      expandedForbidden.append(enemy)
      (x,y) = enemy
      for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
        dx, dy = Actions.directionToVector(direction)
        expandedForbidden.append((int(x+dx),int(y+dy)))
    return expandedForbidden


class EatOneEscapeProblem:
  def __init__(self, gameState, index, enemyIndices, midX, enemyMidX, midLine, enemyMidLine,agent):
    self.index = index
    self.agent = agent
    self.pacmanPos = gameState.getAgentPosition(index)
    self.deadEnds = agent.deadEnd
    self.walls = gameState.getWalls()
    #for i in self.deadEnds:
    #  self.walls[i[1]][i[0]] = True
    # add deadEnd points to walls
    self.middleX = midX
    self.enemyMiddleX = enemyMidX
    self.middleLine = midLine
    self.enemyMiddleLine = enemyMidLine
    self.enemyIndices = agent.getOpponents(gameState)
    self.foods = agent.getFood(gameState)
    self.foodList = self.foods.asList()
    self.enemyPositions = []
    for idx in self.enemyIndices:
      enemyPos = gameState.getAgentPosition(idx)
      if enemyPos != None:
        self.enemyPositions.append(enemyPos)
    self.enemyPositions = tuple(self.enemyPositions)
    #self.expandedForbidden = defaultdict(set()) # key is the expanded time

  def getStartState(self, gameState, foodGrid):
    return (gameState.getAgentPosition(self.index), self.enemyPositions, self.foods,1)

  def isGoalState(self, gameState, state):
    return ((state[0][0] == self.middleX) and (len(state[2].asList()) < len(self.foods.asList()))) or (state[3]>10)

  def getSuccessors(self, state):
    successors = []
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = state[0]
      expandedForbidden = self.getExpandedForbidden(state[1])
      newEnemyList = self.getNewEnemyPostion(state[0],expandedForbidden)
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if (not self.walls[nextx][nexty]) and ((nextx,nexty) not in expandedForbidden):#self.testValid((nextx,nexty),state[1],state[3]):
        # if self.expandedForbidden[state[2]+1] == None:
        #   self.storeExpandedForbidden(state[2]+1)
        nextFood = state[2].copy()
        nextFood[nextx][nexty] = False
        successors.append((((nextx, nexty), newEnemyList, nextFood, state[3]+1), direction, 1))
    return successors

  def eatOneEscapeHeuristic(self,state):
    middleLine = self.agent.middleLine
    print(state)
    curPos, enemy, foods,step = state
    minDist = 9999
    foodList = copy.deepcopy(foods.asList())
    if len(self.foodList) > len(foodList):
      minDist = 9999
      for mid in middleLine:
        minDist = min(minDist,self.agent.getMazeDistance(curPos,mid))
      return minDist
    for food in foodList:
      for mid in middleLine:
        dis = self.agent.getMazeDistance(curPos,food) + self.agent.getMazeDistance(food,mid)
        minDist = min(minDist,dis)
    return minDist

  def getNewEnemyPostion(self,pos,enemyList):
    newEnemyList = []
    minDist = 9999
    for enemy in enemyList:
      print("enemy",enemy)
      if not self.walls[enemy[0]][enemy[1]]:
        dis = self.agent.getMazeDistance(pos,enemy)
        if dis == minDist:
          newEnemyList.append((enemy[0],enemy[1]))
        if dis < minDist:
          minDist = dis
          newEnemyList = []
          newEnemyList.append(enemy)
    return tuple(newEnemyList)


  def testValid(self,pos,enemyList,step):
    for enemy in enemyList:
      if self.agent.getMazeDistance(pos,enemy) <= step:
        return False
    return True

  def getExpandedForbidden(self,enemyList):
    expandedForbidden = []
    for enemy in enemyList:
      expandedForbidden.append(enemy)
      (x,y) = enemy
      for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
        dx, dy = Actions.directionToVector(direction)
        expandedForbidden.append((int(x+dx),int(y+dy)))
    return expandedForbidden

def getMiddleLineHeuristic(agent,state):
  curPos,enemy,foods = state
  middleLine = agent.middleLine
  minDist = 9999
  for mid in middleLine:
    minDist = min(minDist,agent.getMazeDistance(curPos,mid))
  return minDist


    #
    # sumFoodDist = 0
    # closed = [curPos] # food in path calculated

