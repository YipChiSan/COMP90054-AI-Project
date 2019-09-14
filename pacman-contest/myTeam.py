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

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent'):
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

