import copy

import myTeam
from myTeam import *
from game import *
from collections import defaultdict

timeExceed = False

class EatOneProblem:
  def __init__(self, gameState, agent):
    # number of food to be eat that is used in policy selection
    # change to be applied in a new heuristic
    self.targetFoodNum = 1 #TODO: change
    self.agent = agent
    self.index = agent.index
    self.walls = gameState.getWalls()
    self.middleX = agent.midX
    self.enemyMiddleX = agent.enemyMidX
    self.middleLine = agent.midLine
    self.enemyMiddleLine = agent.enemyMidLine
    self.carriedFood = gameState.data.agentStates[self.index].numCarrying

  def getStartState(self, gameState, foodGrid):
    return (gameState.getAgentPosition(self.index), foodGrid, self.targetFoodNum - self.carriedFood)

  def isGoalState(self, gameState, state):
    return self.carriedFood == self.targetFoodNum
    # return state[0] in self.midLine and carriedFood[self.index] == self.targetFoodNum

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

  def eatOneHeuristic(self, state):  # target on eating
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
    closed = [curPos]  # food in path calculated
    while foodToEat > 0:
      minDistToFood = 999999
      for food in foodList:
        for pos in closed:
          newDist = self.agent.distancer.getDistance(pos, food)
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
    #     newDist = self.distancer.getDistance(closedPos, midPos)
    #     if newDist < minDistToMid:
    #       minDistToMid = newDist
    #
    # teamIds = self.getTeam(gameState)  # teammate index
    # for idx in teamIds:
    #   if idx != self.index:
    #     tmPos = gameState.getAgentPosition(idx)
    #     # find pos of the other pac man and calculate distance
    #     distToTm = self.distancer.getDistance(curPos, tmPos)
    #     break

    # x = 0.4
    # return sumFoodDist + minDistToMid -  distToTm
    return sumFoodDist

class EatWithDeadEndProblem: # default: eat one
  def __init__(self, gameState, agent):
    self.targetFoodNum = 1
    self.agent = agent
    self.index = agent.index
    self.walls = gameState.getWalls()
    self.deadEnds = agent.deadEnd
    self.middleX = agent.midX
    self.enemyMiddleX = agent.enemyMidX
    self.middleLine = agent.midLine
    self.enemyMiddleLine = agent.enemyMidLine
    self.carriedFood = gameState.data.agentStates[self.index].numCarrying

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

  def eatWithDeadEndHeuristic(self, state):
    curPos, foodGrid, foodToEat = state
    foodList = copy.deepcopy(foodGrid.asList())
    sumFoodDist = 0
    closed = [curPos]  # food in path calculated
    while foodToEat > 0:
      minDistToFood = 999999
      for food in foodList:
        for pos in closed:
          newDist = self.agent.distancer.getDistance(pos, food)
          if newDist < minDistToFood:
            minDistToFood = newDist
            nearestFoodPos = food
      foodList.remove(nearestFoodPos)
      closed.append(nearestFoodPos)
      foodToEat -= 1
      sumFoodDist += minDistToFood
    return sumFoodDist

class EatCapsuleProblem:
  def __init__(self, gameState, agent):
    self.agent = agent
    self.index = agent.index
    self.walls = gameState.getWalls()
    self.middleX = agent.midX
    self.enemyMiddleX = agent.enemyMidX
    self.middleLine = agent.midLine
    self.enemyMiddleLine = agent.enemyMidLine
    self.capsules = agent.getCapsules()

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

  def eatCapsuleHeuristic(self, state):
    curPos, capsuleList = state
    minDistToCapsule = 999999
    for capsule in capsuleList:
      newDist = self.agent.distancer.getDistance(curPos, capsule)
      if newDist < minDistToCapsule:
        minDistToCapsule = newDist
    return minDistToCapsule

class ReachMiddleListProblem:
  def __init__(self, gameState, agent):
    self.agent = agent
    self.index = agent.index
    self.walls = gameState.getWalls()
    self.middleX = agent.midX
    self.enemyMiddleX = agent.enemyMidX
    self.middleLine = agent.midLine
    self.enemyMiddleLine = agent.enemyMidLine

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

  def reachMiddleListHeuristic(self, state):  # reach the side of our own on the middle list
    curPos = state[0]
    enemyMiddleList = self.enemyMiddleLine
    minDistToMid = 999999
    for midPoint in enemyMiddleList:
      newDist = self.agent.distancer.getDistance(curPos, midPoint)
      if newDist < minDistToMid:
        minDistToMid = newDist
    return minDistToMid

class BackToMiddleListProblem:
  def __init__(self, gameState, agent):
    self.agent = agent
    self.index = agent.index
    self.walls = gameState.getWalls()
    self.middleX = agent.midX
    self.enemyMiddleX = agent.enemyMidX
    self.middleLine = agent.midLine
    self.enemyMiddleLine = agent.enemyMidLine

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

  def backToMiddleListHeuristic(self, state):  # reach the side of our own on the middle list
    curPos = state[0]
    middleList = self.middleLine
    minDistToMid = 999999
    for midPoint in middleList:
      newDist = self.agent.distancer.getDistance(curPos, midPoint)
      if newDist < minDistToMid:
        minDistToMid = newDist
    return minDistToMid

class DefendingProblem:
  #TODO: [reach the change element in two situations]: enemy in sight/foodGrid change
  pass

  def defendingHeuristic(agent, state):
    # TODO:
    pass

class EscapeProblem:
  #fixme: strictly forbid path for pacman, useless in most situation
  def __init__(self, gameState, agent):
    self.index = agent.index
    self.pacmanPos = gameState.getAgentPosition(self.index)
    self.deadEnds = agent.deadEnd
    self.walls = gameState.getWalls() + self.deadEnds # add deadEnd points to walls
    self.walls = gameState.getWalls()
    self.middleX = agent.midX
    self.enemyMiddleX = agent.enemyMidX
    self.middleLine = agent.midLine
    self.enemyMiddleLine = agent.enemyMidLine
    self.enemyIndices = agent.getOpponents()
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

  def escapeHeuristic(self, state):
    curPos = state[0]
    middleList = self.middleLine
    minDistToMid = 999999
    for midPoint in middleList:
      newDist = self.agent.distancer.getDistance(curPos, midPoint)
      if newDist < minDistToMid:
        minDistToMid = newDist
    return minDistToMid


class EatOneSafeFoodProblem:
  def __init__(self, gameState, agent):
    global timeExceed
    timeExceed = False
    self.index = agent.index
    self.agent = agent
    self.pacmanPos = gameState.getAgentPosition(self.index)
    self.deadEnds = agent.deadEnd
    self.walls = gameState.getWalls()
    #for i in self.deadEnds:
    #  self.walls[i[1]][i[0]] = True
    # add deadEnd points to walls
    self.middleX = agent.midX
    self.enemyMiddleX = agent.enemyMidX
    self.middleLine = agent.midLine
    self.enemyMiddleLine = agent.enemyMidLine
    self.enemyIndices = agent.getOpponents(gameState)
    self.foods = agent.getFood(gameState)
    self.foodList = self.foods.asList()
    self.enemyPositions = set()
    for idx in self.enemyIndices:
      enemyPos = gameState.getAgentPosition(idx)
      if enemyPos != None:
        self.enemyPositions.add(enemyPos)
    self.enemyPositions = tuple(self.enemyPositions)

  def getStartState(self, gameState, foodGrid):
    # 3: num of steps; 4: DeadEnd depth
    return (gameState.getAgentPosition(self.index), self.enemyPositions, self.foods,1,0)

  def isGoalState(self, gameState, state):
    global timeExceed
    if state[3]>100:
      timeExceed = True
    return (len(state[2].asList()) < len(self.foods.asList())) or (state[3]>100)

  def getSuccessors(self, state):
    successors = []
    expandedForbidden = self.getExpandedForbidden(state[1]) # set
    separateExpandedForbidden = self.getSeparateExpandedForbidden(state[1]) # dict
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = state[0]
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if not self.walls[nextx][nexty]:
        newEnemyPositions = self.getNewEnemyPostion((nextx, nexty), separateExpandedForbidden)
        if (nextx, nexty) not in expandedForbidden:#self.testValid((nextx,nexty),state[1],state[3]):
        # if self.expandedForbidden[state[2]+1] == None:
        #   self.storeExpandedForbidden(state[2]+1)
          numDE = state[4]
          closeDist = 999
          for enemy in newEnemyPositions:
            if not enemy is None:
              dis = self.agent.distancer.getDistance((nextx,nexty),enemy)
              closeDist = min(closeDist,dis)
          # print("test for deadEnd",(nextx,nexty),self.deadEnds)
          if ((nextx,nexty) in self.deadEnds):
              numDE += 1
          # closeDist 是更新后的enemyPosition, 更新位置需额外加1
          # if closeDist-1 > numDE+1:
          if closeDist-1 > numDE:
            nextFood = state[2].copy()
            nextFood[nextx][nexty] = False
            successors.append((((nextx, nexty), newEnemyPositions, nextFood, state[3]+1,numDE), direction,1))
    return successors

  def eatOneSafeHeuristic(self,state):
    curPos, enemy, foods,step,dead = state
    minDist = 9999
    foodList = copy.deepcopy(foods.asList())
    for food in foodList:
        dis = self.agent.distancer.getDistance(curPos,food)
        minDist = min(minDist,dis)
    return minDist

  def getExpandedForbidden(self,enemySet):
    expandedForbidden = set()
    for enemy in enemySet:
      expandedForbidden.add(enemy)
      (x,y) = enemy
      for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
        dx, dy = Actions.directionToVector(direction)
        expandedForbidden.add((int(x+dx),int(y+dy)))
    return expandedForbidden

  def getSeparateExpandedForbidden(self,enemySet): # set to dict
    expandedForbidden = defaultdict(set)
    for idx, enemyPos in enumerate(enemySet):
      subPos = set() # positions from one possible ghost
      subPos.add(enemyPos)
      (x,y) = enemyPos
      for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
        dx, dy = Actions.directionToVector(direction)
        subPos.add((int(x+dx),int(y+dy)))
      expandedForbidden[idx] = subPos
    return expandedForbidden

  def getNewEnemyPostion(self,pos,enemyDict): # dict to tuple
    newEnemySet = set()
    enemyExpansion = set()
    for enemySet in enemyDict.values():
      minDist = 9999
      for enemy in enemySet:
        # print("enemy",enemy)
        if not self.walls[enemy[0]][enemy[1]]:
          dis = self.agent.distancer.getDistance(pos,enemy)
          if dis == minDist:
            enemyExpansion.add(enemy)
          if dis < minDist:
            minDist = dis
            enemyExpansion = set()
            enemyExpansion.add(enemy)
      newEnemySet.update(enemyExpansion)
    return tuple(newEnemySet)

  def testValid(self,pos,enemyList,step):
    for enemy in enemyList:
      if self.agent.distancer.getDistance(pos,enemy) <= step:
        return False
    return True

  # forceReturn
  def getInSightEnemyDistances(self, curPos):  # distance to enemy from current position
    distList = []
    for enemyPos in self.enemyPositions:
      if enemyPos != None:
        distList.append(self.agent.distancer.getDistance(enemyPos, curPos))
    return distList

class EscapeProblem1:
  def __init__(self, gameState,agent):
    self.index = agent.index
    self.agent = agent
    self.pacmanPos = gameState.getAgentPosition(self.index)
    self.deadEnds = agent.deadEnd
    self.walls = gameState.getWalls()
    self.middleX = agent.midX
    self.enemyMiddleX = agent.enemyMidX
    self.middleLine = agent.midLine
    self.enemyMiddleLine = agent.enemyMidLine
    self.enemyIndices = agent.getOpponents(gameState)
    self.foods = agent.getFood(gameState)
    self.foodList = self.foods.asList()
    self.enemyPositions = set()
    for idx in self.enemyIndices:
      enemyPos = gameState.getAgentPosition(idx)
      if enemyPos != None:
        self.enemyPositions.add(enemyPos)
    self.enemyPositions = tuple(self.enemyPositions)

  def getStartState(self, gameState, foodGrid):
    return (gameState.getAgentPosition(self.index), self.enemyPositions)

  def isGoalState(self, gameState, state):
    return state[0][0] == self.middleX

  def getSuccessors(self, state):
    successors = []
    expandedForbidden = self.getExpandedForbidden(state[1]) # set
    separateExpandedForbidden = self.getSeparateExpandedForbidden(state[1]) # dict
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = state[0]
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if not self.walls[nextx][nexty]:
        newEnemyPositions = self.getNewEnemyPostion((nextx,nexty), separateExpandedForbidden)
        if (nextx,nexty) not in expandedForbidden:#self.testValid((nextx,nexty),state[1],state[3]):
          successors.append((((nextx, nexty), newEnemyPositions), direction, 1))
    return successors

  def EscapeHeuristic(self,state):
    middleLine = self.middleLine
    # print(state)
    curPos, enemy = state
    minDist = 9999
    for mid in middleLine:
      minDist = min(minDist,self.agent.distancer.getDistance(curPos,mid))
    return minDist

  def getExpandedForbidden(self,enemySet):
    expandedForbidden = set()
    for enemy in enemySet:
      expandedForbidden.add(enemy)
      (x,y) = enemy
      for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
        dx, dy = Actions.directionToVector(direction)
        expandedForbidden.add((int(x+dx),int(y+dy)))
    return expandedForbidden

  def getSeparateExpandedForbidden(self,enemySet): # set to dict
    expandedForbidden = defaultdict(set)
    for idx, enemyPos in enumerate(enemySet):
      subPos = set() # positions from one possible ghost
      subPos.add(enemyPos)
      (x,y) = enemyPos
      for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
        dx, dy = Actions.directionToVector(direction)
        subPos.add((int(x+dx),int(y+dy)))
      expandedForbidden[idx] = subPos
    return expandedForbidden

  def getNewEnemyPostion(self,pos,enemyDict): # dict to tuple
    newEnemySet = set()
    enemyExpansion = set()
    for enemySet in enemyDict.values():
      minDist = 9999
      for enemy in enemySet:
        # print("enemy",enemy)
        if not self.walls[enemy[0]][enemy[1]]:
          dis = self.agent.distancer.getDistance(pos,enemy)
          if dis == minDist:
            enemyExpansion.add(enemy)
          if dis < minDist:
            minDist = dis
            enemyExpansion = set()
            enemyExpansion.add(enemy)
      newEnemySet.update(enemyExpansion)
    return tuple(newEnemySet)

  def testValid(self,pos,enemyList,step):
    for enemy in enemyList:
      if self.agent.distancer.getDistance(pos,enemy) <= step:
        return False
    return True

  # forceReturn
  def getInSightEnemyDistances(self, curPos):  # distance to enemy from current position
    distList = []
    for enemyPos in self.enemyPositions:
      if enemyPos != None:
       distList.append(self.agent.distancer.getDistance(enemyPos, curPos))
    return distList

class EatOneEscapeProblem:
  def __init__(self, gameState, agent):
    self.index = agent.index
    self.agent = agent
    self.pacmanPos = gameState.getAgentPosition(self.index)
    self.deadEnds = agent.deadEnd
    self.walls = gameState.getWalls()
    #for i in self.deadEnds:
    #  self.walls[i[1]][i[0]] = True
    # add deadEnd points to walls
    self.middleX = agent.midX
    self.enemyMiddleX = agent.enemyMidX
    self.middleLine = agent.midLine
    self.enemyMiddleLine = agent.enemyMidLine
    self.enemyIndices = agent.getOpponents(gameState)
    self.foods = agent.getFood(gameState)
    self.foodList = self.foods.asList()
    self.enemyPositions = []
    for idx in self.enemyIndices:
      enemyPos = gameState.getAgentPosition(idx)
      if enemyPos != None:
        self.enemyPositions.append(enemyPos)
    self.enemyPositions = tuple(self.enemyPositions)

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
    middleLine = self.middleLine
    if debug:
      print(state)
    curPos, enemy, foods,step = state
    minDist = 9999
    foodList = copy.deepcopy(foods.asList())
    if len(self.foodList) > len(foodList):
      minDist = 9999
      for mid in middleLine:
        minDist = min(minDist,self.agent.distancer.getDistance(curPos,mid))
      return minDist
    for food in foodList:
      for mid in middleLine:
        dis = self.agent.distancer.getDistance(curPos,food) + self.agent.distancer.getDistance(food,mid)
        minDist = min(minDist,dis)
    return minDist

  def getNewEnemyPostion(self,pos,enemyList):
    newEnemyList = []
    minDist = 9999
    for enemy in enemyList:
      if debug:
        print("enemy",enemy)
      if not self.walls[enemy[0]][enemy[1]]:
        dis = self.agent.distancer.getDistance(pos,enemy)
        if dis == minDist:
          newEnemyList.append((enemy[0],enemy[1]))
        if dis < minDist:
          minDist = dis
          newEnemyList = []
          newEnemyList.append(enemy)
    return tuple(newEnemyList)


  def testValid(self,pos,enemyList,step):
    for enemy in enemyList:
      if self.agent.distancer.getDistance(pos,enemy) <= step:
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

  # forceReturn
  def getInSightEnemyDistances(self, curPos):  # distance to enemy from current position
    distList = []
    for enemyPos in self.enemyPositions:
      if enemyPos != None:
       distList.append(self.agent.distancer.getDistance(enemyPos, curPos))
    return distList

def getActualWalls(gameState):
  walls = gameState.getWalls()
  return walls

def getWallsWithDeadEnd(agent):
  walls = agent.walls
  deadEnds = agent.deadEnd
  for pos in deadEnds: # x y of deadEnd is reversed
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
        dist = agent.distancer.getDistance((nextx, nexty), target)
        if dist < minDist:
          minDist = dist
          action = direction
  return action

#find shortest path, to any pos in posList
def minDistanceToFarthestFood(pos, posList, walls, agent):
  maxDist = 0
  x, y = pos
  foodPos = posList[0]
  for target in posList:
    dist = agent.distancer.getDistance((x, y), target)
    if dist > maxDist:
      maxDist = dist
      foodPos = target

  minDist = 9999
  action = Directions.NORTH
  for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:  # if STOP needed?
    x, y = pos
    dx, dy = Actions.directionToVector(direction)
    nextx, nexty = int(x + dx), int(y + dy)
    if not walls[nextx][nexty]:
      dist = agent.distancer.getDistance((nextx, nexty), foodPos)
      if dist < minDist:
        minDist = dist
        action = direction
  return action

def getFoodExceptDeadEnds(agent, gameState):
  food = agent.getFood(gameState)
  for pos in agent.deadEnd:
    food[pos[0]][pos[1]] = False
  foodList = food.asList()
  return foodList

def eatCloseFood(agent, gameState, index):
  food = agent.getFood(gameState)
  foodList = food.asList()
  pos = gameState.getAgentPosition(index)
  walls = gameState.getWalls()
  #walls = getActualWalls(gameState)
  action = minDistance(pos, foodList, walls, agent)
  return action

def eatRandomFood(agent, gameState, index):
  foodIndex = agent.randomFoodIndex
  foodPos = agent.getFood(gameState).asList()[foodIndex]
  pos = gameState.getAgentPosition(index)
  walls = getActualWalls(gameState)
  action = minDistance(pos, [foodPos], walls, agent)
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
  walls = getActualWalls(gameState)
  action = minDistance(pos, capsuleList, walls, agent)
  return action

# reach the top middleLine position
def reachSpecificEnemyMidPos(agent, gameState, index):
  middleList = agent.enemyMidLine
  topMidPos = [middleList[0]]
  pos = gameState.getAgentPosition(index)
  walls = getActualWalls(gameState)
  action = minDistance(pos, topMidPos, walls, agent)
  return action

def reachOwnMidList(agent, gameState, index):
  middleList = agent.midLine
  pos = gameState.getAgentPosition(index)
  walls = getActualWalls(gameState)
  action = minDistance(pos, middleList, walls, agent)
  return action

# used when escape & eatSafeFood return nothing
def reachOwnMidWithEnemyInsight(agent, gameState, index):
  ghostIndices = agent.getOpponents(gameState)
  ghostList = []
  for idx in ghostIndices:
    enemyPos = gameState.getAgentPosition(idx)
    if enemyPos != None:
      ghostList.append(enemyPos)
  middleList = agent.midLine
  pos = gameState.getAgentPosition(index)
  walls = getActualWalls(gameState)
  for ghost in ghostList: # x y of deadEnd is reversed
    if debug:
      print("ghost:",ghost)
    walls[ghost[0]][ghost[1]] = True
  action = minDistance(pos, middleList, walls, agent)
  if debug:
    print("legal actions:", gameState.getLegalActions(agent.index))
    print("actual action:", action)
  return action

def reachEnemyMidList(agent, gameState, index):
  enemyMiddleList = agent.enemyMidLine
  pos = gameState.getAgentPosition(index)
  walls = getActualWalls(gameState)
  action = minDistance(pos, enemyMiddleList, walls, agent)
  return action

def eatFoodClosestToMidList(agent, gameState, index):
  midList = agent.midLine
  foodList = getFoodExceptDeadEnds(agent, gameState)
  pos = gameState.getAgentPosition(index)
  walls = getWallsWithDeadEnd(agent)
  minDist = 9999
  for midPos in midList:
    x, y = midPos
    if not walls[x][y]:
      for target in foodList:
        dist = agent.distancer.getDistance((x, y), target)
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

def eatClosestEnemyPacman(agent, gameState, index):
  enemyIndices = agent.getOpponents(gameState)
  enemyList = []
  for idx in enemyIndices:
    enemyPos = gameState.getAgentPosition(idx)
    if enemyPos != None:
      if agent.red:
        if enemyPos[0] <= agent.midX:
          enemyList.append(enemyPos)
      else:
        if enemyPos[0] >= agent.enemyMidX:
          enemyList.append(enemyPos)
  pos = gameState.getAgentPosition(index)
  walls = getActualWalls(agent)
  action = minDistance(pos, enemyList, walls, agent)
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

# used when in stalemate
def breakStalemate(agent, gameState, index):
  x, y = gameState.getAgentPosition(index)
  if agent.red: # red team back to left
    for direction in [Directions.WEST, Directions.NORTH, Directions.SOUTH, Directions.EAST]:
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      walls = getActualWalls(gameState)
      if not walls[nextx][nexty]:
        return direction
  else: # blue team back to right
    for direction in [Directions.EAST, Directions.NORTH, Directions.SOUTH, Directions.WEST]:
      dx, dy = Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      walls = getActualWalls(gameState)
      if not walls[nextx][nexty]:
        return direction

