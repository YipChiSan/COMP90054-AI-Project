class State_2:

    def __init__(self, Agent, gameState):
        self.Agent = Agent
        self.gameState = gameState
        self.myIndex = Agent.index
        # 自己的位置 (左下角开始)
        self.myCurPosition = gameState.getAgentPosition(self.myIndex)
        # 豆子位置 (左上角)
        self.enemyFood = gameState.getRedFood() if Agent.index & 1 else gameState.getBlueFood()
         # 中线位置
        self.middleLineX = int((gameState.data.layout.width - 2) / 2) if Agent.red else int((gameState.data.layout.width - 2) / 2 + 1)
        # 自己吃了多少豆子
        self.foodCarrying = gameState.data.agentStates[self.myIndex].numCarrying

    def getPossibleActions(self):
        return self.gameState.getLegalActions(self.Agent.index)

    def takeAction(self, action):
        return State_2(self.Agent, self.gameState.generateSuccessor(action))

    def getReward(self):
        reward = 0
        x, y = self.myCurPosition
        if self.enemyFood[x][y]:
            reward += 0.1
        if self.foodCarrying > 0 and self.returnedHome(x):
            reward += 1

        discountFactor = -0.01
        reward += discountFactor * abs(x - self.middleLineX)

        return reward

    def getIndex(self, index):
        new_index = index + self.Agent.index
        if new_index>3:
            new_index = new_index-4
        return new_index

    def returnedHome(self, x):
        return x <= self.middleLineX if self.Agent.red else x >= self.middleLineX
