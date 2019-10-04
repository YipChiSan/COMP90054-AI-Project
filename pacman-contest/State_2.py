class State_2:

    def __init__(self, Agent, gameState):
        self.Agent = Agent
        self.gameState = gameState

    def getCurrentState(self):
        myIndex = self.Agent.index

        # 自己的位置 (左下角开始)
        myCurPosition = self.gameState.getAgentPosition(myIndex)

        # 豆子位置 (左上角)
        enemyFood = self.gameState.getRedFood() if self.Agent.index & 1 else self.gameState.getBlueFood()

        # 中线位置
        middleLineX = int((self.gameState.data.layout.width - 2) / 2) if self.Agent.red else int((self.gameState.data.layout.width - 2) / 2 + 1)

        # 自己吃了多少豆子
        foodCarrying = self.gameState.data.agentStates[myIndex].numCarrying

        currentState = [
            myCurPosition,
            enemyFood,
            middleLineX,
            foodCarrying
        ]

        return currentState

    def getNextState(self, currentState, action):
        myPrevX, myPrevY = currentState[0]
        enemyFood = currentState[1]
        middleLineX = currentState[2]
        foodCarrying = currentState[3]

        nextEnemyFood = enemyFood.copy()
        nextFoodCarrying = foodCarrying

        if action == 'North':
            nextX = myPrevX
            nextY = myPrevY + 1
        elif action == 'East':
            nextX = myPrevX + 1
            nextY = myPrevY

        elif action == 'South':
            nextX = myPrevX
            nextY = myPrevY - 1

        elif action == 'West':
            nextX = myPrevX - 1
            nextY = myPrevY
        else:
            return currentState

        if enemyFood[nextX][nextY]:
            nextEnemyFood[nextX][nextY] = False
            if self.Agent.red:
                if nextX < middleLineX:
                    nextFoodCarrying = nextFoodCarrying + 1
            else:
                if nextX > middleLineX:
                    nextFoodCarrying = nextFoodCarrying + 1

        nextState = [
            (nextX, nextY),
            nextEnemyFood,
            middleLineX,
            nextFoodCarrying
        ]
        return nextState

    def getReward(self):
        pass

    def getIndex(self, index):
        new_index = index + self.Agent.index
        if new_index>3:
            new_index = new_index-4
        return new_index
