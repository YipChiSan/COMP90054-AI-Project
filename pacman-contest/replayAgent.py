from captureAgents import CaptureAgent
import pickle

def createTeam(firstIndex, secondIndex, isRed, first = 'RecordAgent', second = 'RecordAgent'):
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

class RecordAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.agentActions = pickle.load(open('./replayAgentActions','rb'), encoding="bytes")
    self.action = [action for i, action in enumerate(self.agentActions) if self.index == action[0]]
    self.ourMiddleLine = self.getOurMiddleLine(gameState)
    self.enemyMiddleLine = self.getEnemyMiddleLine(gameState)
    self.initEnemyFood = gameState.getRedFood() if self.index & 1 else gameState.getBlueFood()
    self.initOurFood =  gameState.getBlueFood() if self.index & 1 else gameState.getRedFood()
    self.initEnemyCapsules = gameState.getRedCapsules() if self.index & 1 else gameState.getBlueCapsules()
    self.initOurCapsules =  gameState.getBlueCapsules() if self.index & 1 else gameState.getRedCapsules()

    self.recordData = []
    self.preAction = None
    self.preState = []
    self.curState = []

  def getOurMiddleLine(self, gameState):
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

  def getEnemyMiddleLine(self, gameState):
    middleLine = []
    mapWidth = gameState.data.layout.width
    mapHeight = gameState.data.layout.height
    if self.red:
      x = int((mapWidth - 2) / 2 + 1)
    else:
      x = int((mapWidth - 2) / 2 - 1)
    wallList = gameState.getWalls().asList()
    for y in range(1, mapHeight):
      if (x, y) not in wallList:
        middleLine.append((x,y))
    return middleLine

  def getIndex(self,index):
    new_index = index + self.index
    if new_index>3:
      new_index = new_index-4
    return new_index

  def getEnemyNearestFood(self, getMazeDistance, ourFood, firstEnemyCurPosition, secondEnemyCurPosition):
      minDistance = 99999
      minFood = None
      for i, food in enumerate(ourFood.asList()):
        dis1 = getMazeDistance(firstEnemyCurPosition, food) if firstEnemyCurPosition else 99999
        dis2 = getMazeDistance(secondEnemyCurPosition, food) if secondEnemyCurPosition else 99999
        dis = min(dis1, dis2)
        if dis < minDistance:
          minDistance = dis
          minFood = food
      return (minDistance, minFood)

  def chooseAction(self, gameState):

    # ['agentDistances', 'blueTeam', 'data', 'deepCopy', 'generateSuccessor', 'getAgentDistances', 'getAgentPosition',
    #  'getAgentState', 'getBlueCapsules', 'getBlueFood', 'getBlueTeamIndices', 'getCapsules', 'getDistanceProb',
    #  'getInitialAgentPosition', 'getLegalActions', 'getNumAgents', 'getRedCapsules', 'getRedFood', 'getRedTeamIndices',
    #  'getScore', 'getWalls', 'hasFood', 'hasWall', 'initialize', 'isOnRedTeam', 'isOver', 'isRed', 'makeObservation',
    #  'redTeam', 'teams']

    myIndex = self.index
    teammateIndex = self.getIndex(2)
    firstEnemyIndex = self.getIndex(1)
    secondEnemyIndex = self.getIndex(3)

    myAgentState = gameState.getAgentState(myIndex)
    teammateAgentState = gameState.getAgentState(teammateIndex)
    firstEnemyAgentState = gameState.getAgentState(firstEnemyIndex)
    secondEnemyAgentState = gameState.getAgentState(secondEnemyIndex)

    myInitialAgentPosition = gameState.getInitialAgentPosition(myIndex)
    teammateInitialAgentPosition = gameState.getInitialAgentPosition(teammateIndex)
    firstEnemyInitialAgentPosition = gameState.getInitialAgentPosition(firstEnemyIndex)
    secondEnemyInitialAgentPosition = gameState.getInitialAgentPosition(secondEnemyIndex)

    myCurPosition = gameState.getAgentPosition(myIndex)
    teammateCurPosition = gameState.getAgentPosition(teammateIndex)
    firstEnemyCurPosition = gameState.getAgentPosition(firstEnemyIndex)
    secondEnemyCurPosition = gameState.getAgentPosition(secondEnemyIndex)

    enemyFood = gameState.getRedFood() if self.index & 1 else gameState.getBlueFood()
    ourFood =  gameState.getBlueFood() if self.index & 1 else gameState.getRedFood()
    enemyCapsules = gameState.getRedCapsules() if self.index & 1 else gameState.getBlueCapsules()
    ourCapsules =  gameState.getBlueCapsules() if self.index & 1 else gameState.getRedCapsules()


    ##################################################################
    # 分数
    score = gameState.data.score

    # 剩余时间
    timeleft = gameState.data.timeleft

    # 是不是红方
    isRed = gameState.isOnRedTeam(myIndex)
    teammateIsRed = gameState.isOnRedTeam(teammateIndex)
    firstEnemyIsRed = gameState.isOnRedTeam(firstEnemyIndex)
    secondEnemyIsRed = gameState.isOnRedTeam(secondEnemyIndex)

    # 自己是不是鬼
    isGhost = str(myAgentState).startswith('G')
    # 队友是不是鬼
    teammateIsGhost = str(teammateAgentState).startswith('G')
    # 第一个敌人是不是鬼
    firstEnemyIsGhost = str(firstEnemyAgentState).startswith('G')
    # 第二个敌人是不是鬼
    secondEnemyIsGhost = str(secondEnemyAgentState).startswith('G')

    # 自己是不是Pacman
    isPacman = str(myAgentState).startswith('P')
    # 队友是不是Pacman
    teammateIsPacman = str(teammateAgentState).startswith('P')
    # 第一个敌人是不是Pacman
    firstEnemyIsPacman = str(firstEnemyAgentState).startswith('P')
    # 第二个敌人是不是Pacman
    secondEnemyIsPacman = str(secondEnemyAgentState).startswith('P')

    # 自己是不是白鬼
    isScaredGhost = isGhost and (myAgentState.scaredTimer != 0)
    # 队友是不是白鬼
    teammateIsScaredGhost = teammateIsGhost and (teammateAgentState.scaredTimer != 0)
    # 第一个敌人是不是白鬼
    firstEnemyIsScaredGhost = firstEnemyIsGhost and (firstEnemyAgentState.scaredTimer != 0)
    # 第二个敌人是不是白鬼
    secondEnemyIsScaredGhost = secondEnemyIsGhost and (secondEnemyAgentState.scaredTimer != 0)

    # 自己离我方出生地距离
    myDistanceFromHome = self.getMazeDistance(myInitialAgentPosition, myCurPosition)
    # 队友离我方出生地距离
    teammateDistanceFromHome = self.getMazeDistance(teammateInitialAgentPosition, teammateCurPosition)
    # 第一个敌人离我方出生地距离
    firstEnemyDistanceFromHome = self.getMazeDistance(firstEnemyInitialAgentPosition, firstEnemyCurPosition) if firstEnemyCurPosition else -1
    # 第二个敌人离我方出生地距离
    secondEnemyDistanceFromHome = self.getMazeDistance(secondEnemyInitialAgentPosition, secondEnemyCurPosition) if secondEnemyCurPosition else -1

    # 自己离第一个敌人的真实距离
    distanceBetweenMeAndFirstEnemy = self.getMazeDistance(myCurPosition, firstEnemyCurPosition) if firstEnemyCurPosition else -1
    # 自己离第二个敌人的真实距离
    distanceBetweenMeAndSecondEnemy = self.getMazeDistance(myCurPosition, secondEnemyCurPosition) if secondEnemyCurPosition else -1
    # 自己离队友的真实距离
    distanceBetweenMeAndTeammate = self.getMazeDistance(myCurPosition, teammateCurPosition)

    # 自己与第一个敌人的noisy distance
    noisyDistanceBetweenMeAndFirstEnemy = gameState.agentDistances[firstEnemyIndex]
    # 自己与第一个敌人的noisy distance
    noisyDistanceBetweenMeAndSecondEnemy = gameState.agentDistances[secondEnemyIndex]

    # 自己距离我方中线的最近点距离
    distanceToOurMiddleLine = min(map(lambda x: self.getMazeDistance(myCurPosition, x), self.ourMiddleLine))
    # 自己距离敌方中线的最近点距离
    distanceToEnemyMiddleLine = min(map(lambda x: self.getMazeDistance(myCurPosition, x), self.enemyMiddleLine))

    # 自己距离敌方最近capsule的距离
    distanceToEnemyCapsule = min(map(lambda x: self.getMazeDistance(myCurPosition, x), enemyCapsules)) if enemyCapsules else 99999
    # 第一个敌人距离我方capsule的最近距离
    distanceFromFirstEnemyToOurCapsule = min(map(lambda x: self.getMazeDistance(firstEnemyCurPosition, x), ourCapsules)) if firstEnemyCurPosition and ourCapsules else 99999
    # 第二个敌人距离我方capsule的最近距离
    distanceFromSecondEnemyToOurCapsule = min(map(lambda x: self.getMazeDistance(secondEnemyCurPosition, x), ourCapsules)) if secondEnemyCurPosition and ourCapsules else 99999

    # 我方剩余豆子个数
    ourRestFoodCount = ourFood.count()
    # 敌方剩余豆子个数
    enemyRestFoodCount = enemyFood.count()
    # 我方豆子总数
    ourFoodTotal = self.initOurFood.count()
    # 敌方豆子总数
    enemyFoodTotal = self.initEnemyFood.count()

    # 自己身上吃了几个豆子
    foodCarrying = gameState.data.agentStates[myIndex].numCarrying

    # 敌人无敌时间
    myScaredTimer = gameState.data.agentStates[myIndex].scaredTimer
    # 自己无敌时间
    myInvincibleTimer = min(gameState.data.agentStates[firstEnemyIndex].scaredTimer, gameState.data.agentStates[secondEnemyIndex].scaredTimer)

    __enemyNearestFoodAndDistance = self.getEnemyNearestFood(self.getMazeDistance, ourFood, firstEnemyCurPosition, secondEnemyCurPosition)
    # 敌人到我方豆子最近到豆子(如果可见到话), 坐标从左上角开始
    distanceFromFirstEnemyToOurFood = __enemyNearestFoodAndDistance[0]
    # 我方到离敌人最近豆子到距离
    distanceToEnemyNearestFood = min(self.getMazeDistance(myCurPosition, __enemyNearestFoodAndDistance[1]), self.getMazeDistance(teammateCurPosition, __enemyNearestFoodAndDistance[1])) if __enemyNearestFoodAndDistance[1] else 99999

    print('------')
    ##################################################################
    # self.curState.append()
    return self.action.pop(0)[1]

