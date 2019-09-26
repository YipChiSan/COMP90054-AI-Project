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
import InitialMap
from captureAgents import CaptureAgent
import random, time, util
import game
from myProblem import *

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

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
    return random.choice(actions)

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
    global carriedFood
    carriedFood[self.index] = 0
    # TODO: 添加一个dict，包含两个agent index各自目标food的position，在算heuristic的时候从foodList中剔除dict中的值再进行计算
    self.walls = gameState.getWalls()
    self.middleX = self.getMiddleX(gameState)
    self.enemyMiddleX = self.getEnemyMiddleX(gameState)
    self.middleLine = self.getMiddleLine(gameState)
    self.enemyMiddleLine = self.getEnemyMiddleLine(gameState)
    self.deadEnds = InitialMap.searchDeadEnd(getMapMatrix(gameState))

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
    curPos = gameState.getAgentPosition(self.index)
    # initialize attack problem for new gameState
    #TODO: switch to any suitable eat policy[targetFoodNum is determined by the problem]
    attackProblem = EatOneProblem(gameState, self.index, self.middleX, self.enemyMiddleX, self.middleLine, self.enemyMiddleLine)
    """judge if the pac man died in last turn to reset carriedFood value"""
    prevGameState = self.getPreviousObservation()
    if prevGameState != None:
      if (prevGameState.getAgentPosition(self.index)[0] - self.middleX) * (curPos[0] - self.middleX) < 0:
        print("pacman ",self.index," died!")# TODO：有时死了不会清零
        carriedFood[self.index] = 0

    #TODO: use getAgentPosition(enemy.index) to judge if ghost is within agent's sight:
    # if not, the func will return a noneType value;
    if self.red:
      # TODO: if ghost in sight of 5 real distance, go back to middleLine[consider midline and ghost]
      #   if distance to middle list smaller than distance to the closest ghost
      print("test if go back branch can be reached, carriedFood for",self.index,":",carriedFood[self.index])
      print("curPos",curPos)
      if carriedFood[self.index] >= attackProblem.targetFoodNum:
        if curPos[0] <= self.middleX:
          print("test if go back branch can be reached - if")
          carriedFood[self.index] = 0
        else:
          #go back to midline
          print("test if go back branch can be reached - else")
          backToMiddleListProblem = BackToMiddleListProblem(gameState, self.index, self.middleX, self.enemyMiddleX, self.middleLine, self.enemyMiddleLine)
          return self.aStarSearch(backToMiddleListProblem, gameState, self.backToMiddleListHeuristic)[0]
      # else: # need to eat more food
        #go across the middle line
      if curPos[0] <= self.middleX:
        print("go to middle line to start searching, agent index:", self.index, "carriedFood:", carriedFood[self.index])
        reachMiddleListProblem = ReachMiddleListProblem(gameState, self.index, self.middleX, self.enemyMiddleX, self.middleLine, self.enemyMiddleLine)
        return self.aStarSearch(reachMiddleListProblem, gameState, self.reachMiddleListHeuristic)[0]
      else: # search for more food
        print("search for food, agent index:", self.index, "carriedFood:", carriedFood[self.index])
        action = self.aStarSearch(attackProblem, gameState, self.eatOneHeuristic)[0]
        # action = self.aStarSearch(eatOneProblem, gameState, self.eatOneHeuristic)[0]
        dx, dy = game.Actions.directionToVector(action)
        print("dx:",dx,"dy:",dy)
        # getFood是到达点后更新过的list，curPos永远不会在里面
        if (curPos[0]+dx,curPos[1]+dy) in self.getFood(gameState).asList():
          print("find a food")
          carriedFood[self.index] += 1 # manually update carried food number
        return action
    else: # pac man is of blue side
      # TODO: if ghost in sight of 5 real distance, go back to middleLine[consider midline and ghost]
      #   if distance to middle list smaller than distance to the closest ghost
      print("test if go back branch can be reached, carriedFood for",self.index,":",carriedFood[self.index])
      if carriedFood[self.index] >= attackProblem.targetFoodNum:
        if curPos[0] >= self.middleX:
          carriedFood[self.index] = 0
        else:
          #go back to midline
          print("test if go back branch can be reached")
          backToMiddleListProblem = BackToMiddleListProblem(gameState, self.index, self.middleX, self.enemyMiddleX, self.middleLine, self.enemyMiddleLine)
          return self.aStarSearch(backToMiddleListProblem, gameState, self.backToMiddleListHeuristic)[0]
      # else: # need to eat more food
        # go across the middle line
      if curPos[0] >= self.middleX:
        reachMiddleListProblem = ReachMiddleListProblem(gameState, self.index, self.middleX, self.enemyMiddleX, self.middleLine, self.enemyMiddleLine)
        return self.aStarSearch(reachMiddleListProblem, gameState, self.reachMiddleListHeuristic)[0]
      else: # search for more food
        action = self.aStarSearch(attackProblem, gameState, self.eatOneHeuristic)[0]
        dx, dy = game.Actions.directionToVector(action)
        # getFood是到达点后更新过的list，curPos永远不会在里面
        if (curPos[0] + dx, curPos[1] + dy) in self.getFood(gameState).asList():
          carriedFood[self.index] += 1  # manually update carried food number
        return action

  def aStarSearch(self, problem, gameState, heuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    # init
    visited = set()
    best_g = dict()
    """state: [position, ...]"""
    """state, action list, cost value g"""
    start_node = (problem.getStartState(gameState, self.getFood(gameState)), [], 0)
    frontier = util.PriorityQueue()
    priority = heuristic(problem.getStartState(gameState, self.getFood(gameState)))  # f = h + g(start is 0)
    frontier.push(start_node, priority)

    while not frontier.isEmpty():
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
          return current_node[1] # fixme: return index[0] since only the first action is needed
        else:
          for successor in problem.getSuccessors(current_node[0]):
            cost_g = current_node[2] + successor[2]
            priority = cost_g + heuristic(successor[0])
            path = current_node[1] + [successor[1]]
            frontier.push((successor[0], path, cost_g), priority)

    # if no result, calculate four adjacent positions
    # fixme: return index[0] since only the first action is needed
    return self.forcedReturn(problem, start_node[0])

  def forcedReturn(self, problem, state):
    #fixme: currently used for escape heuristic
    maxDistToEnemy = 0
    prevMinDistToMid = 999999
    for successor in problem.getSuccessors(state):
      distList = problem.getInSightEnemyDistances(successor[0][0])
      sumDistToEnemy = 0
      for dist in distList:
        sumDistToEnemy += dist

      if sumDistToEnemy > maxDistToEnemy:
        maxDistToEnemy = sumDistToEnemy
        action = successor[1]
        prevMinDistToMid = 999999
      elif sumDistToEnemy == maxDistToEnemy:
        minDistToMid = 999999
        for midPos in self.middleLine:
          newDist = self.getMazeDistance(successor[0][0], midPos)
          if newDist < minDistToMid:
            minDistToMid = newDist
        if minDistToMid < prevMinDistToMid:
          prevMinDistToMid = minDistToMid
          action = successor[1]

    return action









