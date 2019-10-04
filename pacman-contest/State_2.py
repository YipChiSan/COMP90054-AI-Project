class State_2:

    def __init__(self, Agent, gameState, score, foodCarrying):
        self.Agent = Agent
        self.gameState = gameState
        self.myIndex = Agent.index
        # 自己的位置 (左下角开始)
        self.myCurPosition = gameState.getAgentPosition(self.myIndex)
        # 豆子位置 (左上角)
        self.enemyFood = gameState.getRedFood().asList() if Agent.index & 1 else gameState.getBlueFood().asList()
        # 中线位置
        self.middleLineX = int((gameState.data.layout.width - 2) / 2) if Agent.red else int((gameState.data.layout.width - 2) / 2 + 1)
        # 分数
        self.prevScore = score
        self.curScore = gameState.getScore()
        # 自己吃了多少豆子
        self.prevFoodCarrying = foodCarrying
        self.curFoodCarrying = gameState.data.agentStates[self.myIndex].numCarrying

    def getPossibleActions(self):
        actions = self.gameState.getLegalActions(self.Agent.index)
        print(self.Agent.index, self.myCurPosition, actions) if not self.Agent.index & 1 else None
        return actions

    def takeAction(self, action):
        return State_2(self.Agent, self.gameState.generateSuccessor(self.Agent.index, action), self.curScore, self.curFoodCarrying)

    def getReward(self):
        discountFactor = -0.01
        reward = 0
        reward += discountFactor * min(map(lambda x: self.Agent.getMazeDistance(self.myCurPosition, x), self.getOurMiddleLine()))

        carryChange = self.curFoodCarrying - self.prevFoodCarrying
        if carryChange > 0:
            print("=============\n", carryChange)
            reward += 0.5 * carryChange
        else:
            reward += discountFactor * min(map(lambda x: self.Agent.getMazeDistance(self.myCurPosition, x), self.enemyFood))
        reward += (self.curScore - self.prevScore)

        return reward

    def getIndex(self, index):
        new_index = index + self.Agent.index
        if new_index > 3:
            new_index = new_index - 4
        return new_index

    def returnedHome(self, x):
        return x <= self.middleLineX if self.Agent.red else x >= self.middleLineX

    def getOurMiddleLine(self):
        middleLine = []
        mapWidth = self.gameState.data.layout.width
        mapHeight = self.gameState.data.layout.height
        if self.Agent.red:
          x = int((mapWidth - 2) / 2)
        else:
          x = int((mapWidth - 2) / 2 + 1)
        wallList = self.gameState.getWalls().asList()
        for y in range(1, mapHeight):
          if (x, y) not in wallList:
            middleLine.append((x,y))
        return middleLine
