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

import sys
sys.path.append('teams/kdbnb/pacman-contest/')

import copy
import InitialMap
from captureAgents import CaptureAgent
import random, time, util
from game import *
import game
from layout import Grid
import myProblem
from State_1 import *
import random
import getEnemyPosition

#################
# Team creation #
#################
debug = False
enemyPosition = getEnemyPosition.enemyPosition()

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

def getMapMatrix(gameState):
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

class AttackAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState) # must be put ahead to set value of self.red
    self.walls = gameState.getWalls()
    self.midX = self.getMiddleX(gameState)
    self.enemyMidX = self.getEnemyMiddleX(gameState)
    self.midLine = self.getMiddleLine(gameState)
    self.enemyMidLine = self.getEnemyMiddleLine(gameState)
    self.mapMatrix = getMapMatrix(gameState)
    self.capsules = self.getCapsules(gameState)
    self.deadEnd = InitialMap.searchDeadEnd(self.mapMatrix) # keys are deadEnds, values are corresponding depth
    self.sumOfFood = len(self.getFood(gameState).asList())
    # used for separate pacman
    self.randomFoodIndex = random.randint(0, self.sumOfFood-1)
    # print(self.randomFoodIndex)
    self.randomSelectFood = True
    self.allienIndex = (self.index + 2) % 4
    if self.red:
      self.enemyIndex = [1,3]
    else:
      self.enemyIndex = [0,2]
    enemyPosition.initial(gameState,self.red,self.mapMatrix)
    # for i in self.deadEnd:
    #   # x = i[1]
    #   # y = len(self.mapMatrix) - i[0] -1
    #   if i[0] <= self.midX:
    #     self.debugDraw(i,[self.deadEnd[i]/100+0.3,0,0])
    #   else:
    #     self.debugDraw(i,[0,self.deadEnd[i]/100+0.3,0])

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
    midLine = []
    mapHeight = gameState.data.layout.height
    x = self.midX
    wallList = gameState.getWalls().asList()
    for y in range(1, mapHeight):
      if (x, y) not in wallList:
        midLine.append((x,y))
    return midLine

  def getEnemyMiddleLine(self, gameState):
    enemyMidLine = []
    mapHeight = gameState.data.layout.height
    x = self.enemyMidX
    wallList = gameState.getWalls().asList()
    for y in range(1, mapHeight):
      if (x, y) not in wallList:
        enemyMidLine.append((x, y))
    return enemyMidLine

  def getIndex(self, index): # 0:self;2:teammate;1/3:enemy
    new_index = index + self.index
    if new_index > 3:
      new_index = new_index - 4
    return new_index

  def capsuleEatenLastMove(self, gameState):
    prevGameState = self.getPreviousObservation()
    if prevGameState != None:
      prevCapsules = self.getCapsules(prevGameState)
      curCapsules = self.getCapsules(gameState)
      for capsule in prevCapsules:
        if capsule not in curCapsules:
          return True
    return False

  def eatEnemy(self,gameState):
      eatEnemy = {}
      preGameState = self.getPreviousObservation()
      for index in self.enemyIndex:
        eatEnemy[index] = False
        if gameState.data.timeleft <1190:
          enemyCur = gameState.getAgentPosition(index)
          enemyPre = preGameState.getAgentPosition(index)
          posPre = preGameState.getAgentPosition(self.index)
          allienPre = preGameState.getAgentPosition(self.allienIndex)
          if enemyCur is None and (not enemyPre is None) and (gameState.getAgentPosition(self.index) != gameState.getInitialAgentPosition(self.index)):
            distance = self.distancer.getDistance(posPre,enemyPre)
            distance2 = self.distancer.getDistance(allienPre,enemyPre)
            if (distance < 2) or (distance2 < 2):
              eatEnemy[index] = True
            else:
              eatEnemy[index] = False
          else:
            if (not enemyPre is None) and (enemyCur is None):
              distance = self.distancer.getDistance(posPre,enemyPre)
              if distance > 2:
                eatEnemy[index] = True
              else:
                eatEnemy[index] = False
            else:
              eatEnemy[index] = False
      return eatEnemy

  def getEnemyTrueP(self,gameState):
    enemyPosition = {}
    if self.red:
      enemyPosition[1] = gameState.getAgentPosition(1)
      enemyPosition[3] = gameState.getAgentPosition(3)
    else:
      enemyPosition[0] = gameState.getAgentPosition(0)
      enemyPosition[2] = gameState.getAgentPosition(2)
    return enemyPosition

  def foodBeenEaten(self,gameState):
      if gameState.data.timeleft<1190:
        curFoods = self.getFoodYouAreDefending(gameState).asList()
        preFoods = self.getFoodYouAreDefending(self.getPreviousObservation()).asList()
      else:
        return set()
      return set(preFoods) - set(curFoods)

  def capsuleBeenEaten(self,gameState):
      if gameState.data.timeleft<1190:
        curCap = self.getCapsulesYouAreDefending(gameState)
        preCap = self.getCapsulesYouAreDefending(self.getPreviousObservation())
      else:
        return set()
      return set(preCap) - set(curCap)

  def getEnemyPosition(self,gameState):
    curPos = gameState.getAgentPosition(self.index)
    noiseDistance = gameState.agentDistances
    if gameState.data.timeleft <1200:
      eatEnemy = self.eatEnemy(gameState)
      for i in eatEnemy:
        if eatEnemy[i]:
          enemyPosition.updateWithDeath(i)
      enemyPosition.updateWithNoise(noiseDistance,self.index,curPos)
      enemyTruePosition = self.getEnemyTrueP(gameState)
      for i in enemyTruePosition:
        if not enemyTruePosition[i] is None:
          enemyPosition.updateWithVision(i,enemyTruePosition[i])
      if len(self.foodBeenEaten(gameState)) != 0:
        enemyPosition.updateWithEatenFood(list(self.foodBeenEaten(gameState))[0])
      if len(self.capsuleBeenEaten(gameState)) != 0:
        enemyPosition.updateWithEatenFood(list(self.capsuleBeenEaten(gameState))[0])
      a = enemyPosition.enemyPosition
      if debug:
          self.debugClear()
          for i in a[1]:
            self.debugDraw(i,[0,.3,.9])
          # for i in enemyPosition.validPosition:
          #   self.debugDraw(i,[0,0,1])
          for i in a[3]:
            self.debugDraw(i,[.1,.75,.7])

  def chooseAction(self, gameState):
    curPos = gameState.getAgentPosition(self.index)
    teammateIndex = self.getIndex(2)
    teammatePos = gameState.getAgentPosition(teammateIndex)
    enemyIndices = self.getOpponents(gameState)
    enemyPos = []
    for idx in enemyIndices:
      enemyPos.append(gameState.getAgentPosition(idx))
    enemyPosition = self.getEnemyPosition(gameState)
    # print(self.midLine)
    # print("=============")

    # initialize attack problem for new gameState
    # attackProblem = myProblem.EatOneProblem(gameState, self)
    # """judge if the pac man died in last turn to reset carriedFood value"""
    # prevGameState = self.getPreviousObservation()
    # if prevGameState != None:
    #   if (prevGameState.getAgentPosition(self.index)[0] - self.midX) * (curPos[0] - self.midX) < 0:
    #     print("pacman ",self.index," died!")
    #     carriedFood[self.index] = 0
    enemyScaredTimer = [gameState.data.agentStates[idx].scaredTimer for idx in enemyIndices]
    numOfFoodCarried = gameState.data.agentStates[self.index].numCarrying
    numOfFoodLeft = len(self.getFood(gameState).asList())
    # distance to the closest point in own middle line
    minDistToOwnMid = 999999
    for midPoint in self.midLine:
        newDist = self.distancer.getDistance(curPos, midPoint)
        if newDist < minDistToOwnMid:
          minDistToOwnMid = newDist
          # closestOwnMidPos = midPoint
    minDistToFood = 999999
    for foodPos in self.getFood(gameState).asList():
      newDist = self.distancer.getDistance(curPos, foodPos)
      if newDist < minDistToFood:
        minDistToFood = newDist

    if self.red:
      timer = None # None for not using capsule logic
      if (enemyScaredTimer[0] > 0 or enemyScaredTimer[1] > 0) and curPos[0] > self.midX: # enemy is scared
        # print("enemyScaredTimer:", enemyScaredTimer)
        # print("minDistToOwnMid:", minDistToOwnMid)
        #todo: 吃过capsule以后看到capsule绕路? capsule堵关键路口怎么办？
        if enemyScaredTimer[0] > 0 and enemyPos[0] != None:
          if enemyScaredTimer[1] > 0 and enemyPos[1] != None:
            timer = min(enemyScaredTimer[0],enemyScaredTimer[1])
          elif enemyPos[1] == None:
            timer = enemyScaredTimer[0]
          if timer != None and timer <= minDistToOwnMid+1:
            # print("capsule action: reachOwnMidList")
            action = myProblem.reachOwnMidList(self, gameState, self.index)
          elif timer != None and timer > minDistToOwnMid+1:
            # print("capsule action: eatCloseFood")
            action = myProblem.eatCloseFood(self, gameState, self.index)
        elif enemyPos[0] == None:
          if enemyScaredTimer[1] > 0 and enemyPos[1] != None:
            timer = enemyScaredTimer[1]
          if timer != None and timer <= minDistToOwnMid+1:
            # print("capsule action: reachOwnMidList")
            action = myProblem.reachOwnMidList(self, gameState, self.index)
          elif timer != None and timer > minDistToOwnMid+1:
            # print("capsule action: eatCloseFood")
            action = myProblem.eatCloseFood(self, gameState, self.index)
        if timer != None:
          return action

      close = False
      for enemy in enemyPos:
        if not(enemy is None):
          close = close or (self.distancer.getDistance(curPos,enemy) <= 5)
      # if enemyPos == [None, None] or (not close):
      if enemyPos == [None, None]:
        if (minDistToFood> minDistToOwnMid and numOfFoodCarried > 0) or numOfFoodLeft <= 2:
          # go back to midline
          action = myProblem.reachOwnMidList(self, gameState, self.index)
        else:
          # separate two pacman
          if self.index//2 == 0 and self.randomSelectFood:
            # teammate may eat one food when crossing midline and led to bug
            if curPos[0] >= self.enemyMidX or teammatePos[0] >= self.enemyMidX:
              self.randomSelectFood = False
            if self.randomSelectFood:
              # print("entering randomSelectFood")
              action = myProblem.eatRandomFood(self, gameState, self.index)
            else:
              # print("entering eatCloseFood")
              action = myProblem.eatCloseFood(self, gameState, self.index)
          else:
            # print("entering eatCloseFood")
            action = myProblem.eatCloseFood(self, gameState, self.index)
      else:
        # judge enemy is ghost or pacman
        for enemy in enemyPos:
          if not (enemy is None) and enemy[0] <= self.midX:  # any one of enemies is PACMAN
            # print("chase closest enemy pacman")
            action = myProblem.eatClosestEnemyPacman(self, gameState, self.index)
            return action
        if curPos[0] < self.midX:
          action = myProblem.reachOwnMidList(self, gameState, self.index)
        elif curPos in self.midLine:
          action = myProblem.breakStalemate(self, gameState, self.index)
        else: # close and pacman on enemy's field
          if numOfFoodLeft > 2:
            # print("eat safe food")
            problem = myProblem.EatOneSafeFoodProblem(gameState,self)
            actions = self.aStarSearch(problem, gameState, problem.eatOneSafeHeuristic)
            if actions == None or actions == "TIMEEXCEED":
              escapeProblem = myProblem.EscapeProblem1(gameState, self)
              actions = self.aStarSearch(escapeProblem, gameState, escapeProblem.EscapeHeuristic)
              if actions == None:
                # print("reachOwnMidWithEnemyInsight1")
                action = myProblem.reachOwnMidWithEnemyInsight(self, gameState, self.index)
              else:
                # print("EscapeProblem1:", actions)
                action = actions[0]
            else:
              # print("eatOneSafeFood")
              action = actions[0]
          else:
            escapeProblem = myProblem.EscapeProblem1(gameState, self)
            actions = self.aStarSearch(escapeProblem, gameState, escapeProblem.EscapeHeuristic)
            if actions == None:
              # print("reachOwnMidWithEnemyInsight2")
              action = myProblem.reachOwnMidWithEnemyInsight(self, gameState, self.index)
            else:
              # print("EscapeProblem2:", actions)
              action = actions[0]
      return action
    #TODO: pac man is of blue side
    else:
      timer = None  # None for not using capsule logic
      if (enemyScaredTimer[0] > 0 or enemyScaredTimer[1] > 0) and curPos[0] < self.midX:  # enemy is scared
        # todo: 吃过capsule以后看到capsule绕路? capsule堵关键路口怎么办？
        if enemyScaredTimer[0] > 0 and enemyPos[0] != None:
          if enemyScaredTimer[1] > 0 and enemyPos[1] != None:
            timer = min(enemyScaredTimer[0], enemyScaredTimer[1])
          elif enemyPos[1] == None:
            timer = enemyScaredTimer[0]
          if timer != None and timer <= minDistToOwnMid + 1:
            action = myProblem.reachOwnMidList(self, gameState, self.index)
          elif timer != None and timer > minDistToOwnMid + 1:
            action = myProblem.eatCloseFood(self, gameState, self.index)
        elif enemyPos[0] == None:
          if enemyScaredTimer[1] > 0 and enemyPos[1] != None:
            timer = enemyScaredTimer[1]
          if timer != None and timer <= minDistToOwnMid + 1:
            action = myProblem.reachOwnMidList(self, gameState, self.index)
          elif timer != None and timer > minDistToOwnMid + 1:
            action = myProblem.eatCloseFood(self, gameState, self.index)
        if timer != None:
          return action

      close = False
      for enemy in enemyPos:
        if not (enemy is None):
          close = close or (self.distancer.getDistance(curPos, enemy) <= 5)
      # if enemyPos == [None, None] or (not close):
      if enemyPos == [None, None]:
        if (minDistToFood > minDistToOwnMid and numOfFoodCarried > 0) or numOfFoodLeft <= 2:
          # go back to midline
          action = myProblem.reachOwnMidList(self, gameState, self.index)
        else:
          # separate two pacman
          if self.index // 2 == 0 and self.randomSelectFood:
            # teammate may eat one food when crossing midline and led to bug
            if curPos[0] <= self.enemyMidX or teammatePos[0] <= self.enemyMidX:
              self.randomSelectFood = False
            if self.randomSelectFood:
              action = myProblem.eatRandomFood(self, gameState, self.index)
            else:
              action = myProblem.eatCloseFood(self, gameState, self.index)
          else:
            action = myProblem.eatCloseFood(self, gameState, self.index)
      else:
        # judge enemy is ghost or pacman
        for enemy in enemyPos:
          if not (enemy is None) and enemy[0] >= self.midX:  # any one of enemies is PACMAN
            action = myProblem.eatClosestEnemyPacman(self, gameState, self.index)
            return action
        if curPos[0] > self.midX:
          action = myProblem.reachOwnMidList(self, gameState, self.index)
        elif curPos in self.midLine:
          action = myProblem.breakStalemate(self, gameState, self.index)
        else:  # close and pacman on enemy's field
          if numOfFoodLeft > 2:
            problem = myProblem.EatOneSafeFoodProblem(gameState, self)
            actions = self.aStarSearch(problem, gameState, problem.eatOneSafeHeuristic)
            if actions == None or actions == "TIMEEXCEED":
              escapeProblem = myProblem.EscapeProblem1(gameState, self)
              actions = self.aStarSearch(escapeProblem, gameState, escapeProblem.EscapeHeuristic)
              if actions == None:
                action = myProblem.reachOwnMidWithEnemyInsight(self, gameState, self.index)
              else:
                action = actions[0]
            else:
              action = actions[0]
          else:
            escapeProblem = myProblem.EscapeProblem1(gameState, self)
            actions = self.aStarSearch(escapeProblem, gameState, escapeProblem.EscapeHeuristic)
            if actions == None:
              action = myProblem.reachOwnMidWithEnemyInsight(self, gameState, self.index)
            else:
              action = actions[0]
      return action

  def aStarSearch(self, problem, gameState, heuristic):
    start = time.clock()
    """Search the node that has the lowest combined cost and heuristic first."""
    # init
    visited = set()
    best_g = dict()
    """state: [position, foodGrid, food]"""
    """state, action list, cost value g"""
    start_node = (problem.getStartState(gameState, self.getFood(gameState)), [], 0)
    frontier = util.PriorityQueue()
    priority = heuristic(problem.getStartState(gameState, self.getFood(gameState)))  # f = h + g(start is 0)
    frontier.push(start_node, priority)

    while not frontier.isEmpty():
      elapsed = (time.clock() - start)
      # print("Time used:", elapsed)
      # todo : if elapsed >= 0.8 return None
      if elapsed >= 0.8:
        # print("time exceed")
        return "TIMEEXCEED" # for eatOneSafeFood time exceed

      current_node = frontier.pop()
      if current_node[0] in best_g.keys():  # reopen
        if best_g[current_node[0]] > current_node[2]:
          best_g[current_node[0]] = current_node[2]
          for successor in problem.getSuccessors(current_node[0]):
            cost_g = current_node[2] + successor[2]
            priority = cost_g + heuristic(successor[0])
            path = current_node[1] + [successor[1]]
            frontier.push((successor[0], path, cost_g), priority)
      elif current_node[0] not in visited:
        best_g[current_node[0]] = current_node[2]
        visited.add(current_node[0])
        if problem.isGoalState(gameState, current_node[0]):
          return current_node[1]
        else:
          for successor in problem.getSuccessors(current_node[0]):
            cost_g = current_node[2] + successor[2]
            priority = cost_g + heuristic(successor[0])
            path = current_node[1] + [successor[1]]
            frontier.push((successor[0], path, cost_g), priority)





