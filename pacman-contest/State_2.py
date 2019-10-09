class State_2:

    def __init__(self, isRed, index, getMazeDistance, gameState, score, foodCarrying):
        self.gameState = gameState
        self.isRed = isRed
        self.getMazeDistance = getMazeDistance
        self.myIndex = index
        # 自己的位置 (左下角开始)
        self.myCurPosition = gameState.getAgentPosition(self.myIndex)
        # 豆子位置 (左上角)
        self.enemyFood = gameState.getRedFood().asList() if index & 1 else gameState.getBlueFood().asList()
        # 中线位置
        self.middleLineX = int((gameState.data.layout.width - 2) / 2) if isRed else int((gameState.data.layout.width - 2) / 2 + 1)
        # 分数
        self.prevScore = score
        self.curScore = gameState.getScore()
        # 自己吃了多少豆子
        self.prevFoodCarrying = foodCarrying
        self.curFoodCarrying = gameState.data.agentStates[self.myIndex].numCarrying

    def getPossibleActions(self):
        actions = self.gameState.getLegalActions(self.myIndex)
        # print(self.index, self.myCurPosition, actions) if not self.index & 1 else None
        return actions

    def takeAction(self, action):
        # newState = self.gameState.generateSuccessor(self.myIndex, action)
        # newState = self.gaemState.generateSuccessor(3,action)
        s = State_2(self.isRed, self.myIndex, self.getMazeDistance, self.gameState.generateSuccessor(self.myIndex, action), self.curScore, self.curFoodCarrying)
        return s
    def getReward(self):
        discountFactor = 0.000001
        reward = 0
        reward += discountFactor * (100 - min(map(lambda x: self.getMazeDistance(self.myCurPosition, x), self.getOurMiddleLine())))

        # carryChange = self.curFoodCarrying - self.prevFoodCarrying
        # if carryChange > 0:
        #     reward += 10 * carryChange
        # else:
        reward += self.curFoodCarrying*10
        reward += discountFactor * (100 - min(map(lambda x: self.getMazeDistance(self.myCurPosition, x), self.enemyFood)))
        reward += (self.curScore - self.prevScore)*20

        return reward

    def getIndex(self, index):
        new_index = index + self.myIndex
        if new_index > 3:
            new_index = new_index - 4
        return new_index

    def returnedHome(self, x):
        return x <= self.middleLineX if self.isRed else x >= self.middleLineX

    def isTerminal(self):
        if self.curScore - self.prevScore > 0:
            return True
        return False

    def getOurMiddleLine(self):
        middleLine = []
        mapWidth = self.gameState.data.layout.width
        mapHeight = self.gameState.data.layout.height
        if self.isRed:
          x = int((mapWidth - 2) / 2)
        else:
          x = int((mapWidth - 2) / 2 + 1)
        wallList = self.gameState.getWalls().asList()
        for y in range(1, mapHeight):
          if (x, y) not in wallList:
            middleLine.append((x,y))
        return middleLine
