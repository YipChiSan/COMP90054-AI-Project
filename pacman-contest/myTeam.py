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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#global variable for store currently carried food number of every agent
carriedFood = dict()

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AttackAgent', second = 'AttackAgent'):
  # TODO: for each agent:explore/eat/escape/...
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
    global carriedFood
    carriedFood[self.index] = 0
    self.walls = gameState.getWalls()
    CaptureAgent.registerInitialState(self, gameState)

  def getMiddleX(self, gameState):
    mapWidth = gameState.data.layout.width
    if self.red:
      x = int((mapWidth - 2) / 2)
    else:
      x = int((mapWidth - 2) / 2 + 1)
    return x

  def getMiddleLine(self, gameState):
    middleLine = []
    mapHeight = gameState.data.layout.height
    x = self.getMiddleX(gameState)
    wallList = gameState.getWalls().asList()
    for y in range(1, mapHeight):
      if (x, y) not in wallList:
        middleLine.append((x,y))
    return middleLine

  def chooseAction(self, gameState):
    # TODO:
    #  go to middle Line,
    #  eat up to 10 [if ghost in sight then run back,
    #  or go back to middle line when pac man is with food],
    #  go back to middle line.
    # 10 is setting for target number of food

    if self.red:
      # TODO: if ghost in sight of 5 real distance, go back to middleLine

      if carriedFood[self.index] == 10:
        if gameState.getAgentPosition(self.index)[0] <= self.getMiddleX(gameState):
          carriedFood[self.index] = 0
        else:
          # TODO: go back to midline[consider midline and ghost]
          pass
      else: # need to eat more food
        if gameState.getAgentPosition(self.index)[0] <= self.getMiddleX(gameState):
          # TODO: reach middle list
          pass
        else:
          return self.aStarSearch(gameState)[0]
    else:
      # TODO: if ghost in sight of 5 real distance, go back to middleLine

      if carriedFood[self.index] == 10:
        if gameState.getAgentPosition(self.index)[0] >= self.getMiddleX(gameState):
          carriedFood[self.index] = 0
        else:
          # TODO: go back to midline[consider midline and ghost]
          pass
      else: # need to eat more food
        if gameState.getAgentPosition(self.index)[0] >= self.getMiddleX(gameState):
          # TODO: reach middle list
          pass
        else:
          return self.aStarSearch(gameState)[0]

  def isGoalState(self, state):
    global carriedFood
    return state[0] in self.getMiddleLine() and carriedFood[self.index] == 10

  def getSuccessors(self, state):
    successors = []
    # self._expanded += 1  # DO NOT CHANGE
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = state[0]
      dx, dy = game.Actions.directionToVector(direction)
      nextx, nexty = int(x + dx), int(y + dy)
      if not self.walls[nextx][nexty]:
        # step 2: find all food
        nextFood = state[1].copy()
        if (nextx,nexty) in state[1].asList(): # successor in enemy's place
          nextFood[nextx][nexty] = False
        successors.append((((nextx, nexty), nextFood), direction, 1))
    return successors

  def attackHeuristic(self, gameState, state):
    """
    used for attack agent
    dist(P,Food) TODO: change to the nearest x food positions[x = numOfFoodNeeded]
      - x1 * dist(P,Ghost)  TODO:change to ghost in sight[not consider ghost in attack mode]
      + x2 * dist(P,middleLine)(mean for distances to middle line positions)
      - x3 * dist(P,P2)
    @:param index: index of agent the heuristic is used on
            state: [(x, y), foodGrid]
    """
    curPos, foodGrid = state
    teamIds = self.getTeam(gameState) #teammate index
    # enemyIds = self.getOpponents(gameState) #enemy index

    minDistToFood = 999999
    foodList = foodGrid.asList()
    for food in foodList:
      newDist = self.getMazeDistance(state[0], food)
      if newDist < minDistToFood:
        minDistToFood = newDist
    # minDistToEnemy = 999999
    # for idx in enemyIds:
    #   enemyPos = gameState.getAgentPosition(idx)
    #   newDist = self.getMazeDistance(curPos, enemyPos)
    #   if newDist < minDistToEnemy:
    #     minDistToEnemy = newDist
    for idx in teamIds:
      if idx != self.index:
        tmPos = gameState.getAgentPosition(idx)
        # find pos of the other pac man and calculate distance
        distToTm = self.getMazeDistance(curPos, tmPos)
        break

    midAccesses = self.getMiddleLine(gameState)
    sumDistToMid = 0
    for midPos in midAccesses:
      newDist = self.getMazeDistance(curPos, midPos)
      sumDistToMid += newDist
    distToMid = sumDistToMid/len(midAccesses)

    x1 = 1
    x2 = 0.5
    x3 = 0.5

    # return minDistToFood - x1 * minDistToEnemy + x2 * distToMid - x3 * distToTm
    return minDistToFood + x2 * distToMid - x3 * distToTm

  def aStarSearch(self, gameState, heuristic=attackHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    # init
    visited = set()
    best_g = dict()
    """state, action list, cost value g"""
    start_node = ((gameState.getAgentPosition(self.index),gameState.getFood()), [], 0)
    frontier = util.PriorityQueue()
    priority = heuristic(gameState, [gameState.getAgentPosition(self.index), self.getFood(gameState)])  # f = h + g(start is 0)
    frontier.push(start_node, priority)

    while not frontier.isEmpty():
      current_node = frontier.pop()
      if current_node[0] in best_g.keys():  # reopen
        if best_g[current_node[0]] > current_node[2]:
          best_g[current_node[0]] = current_node[2]
          for successor in self.getSuccessors(current_node[0]):
            cost_g = current_node[2] + successor[2]
            priority = cost_g + heuristic(gameState, successor[0])
            path = current_node[1] + [successor[1]]
            frontier.push((successor[0], path, cost_g), priority)
      elif current_node[0] not in visited:
        best_g[current_node[0]] = current_node[2]
        visited.add(current_node[0])
        if self.isGoalState(current_node[0]):
          return current_node[1]
        else:
          for successor in self.getSuccessors(current_node[0]):
            cost_g = current_node[2] + successor[2]
            priority = cost_g + heuristic(gameState, successor[0])
            path = current_node[1] + [successor[1]]
            frontier.push((successor[0], path, cost_g), priority)

