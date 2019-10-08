class State_2:

    def __init__(self,
                 gameState,
                 score,
                 foodCarrying,
                 index,
                 isRed,
                 enemyFoodList,
                 getDistance,
                 middleLineX,
                 ourMiddleLine,
                 wallList):
        self.gameState = gameState
        self.myIndex = index
        self.isRed = isRed
        self.getDistance = getDistance
        self.wallList = wallList
        # 自己的位置 (左下角开始)
        self.myCurPosition = gameState.getAgentPosition(self.myIndex)
        # 豆子位置 (左下角)
        self.enemyFoodList = enemyFoodList
        # 中线x位置
        self.middleLineX = middleLineX
        self.ourMiddleLine = ourMiddleLine
        # 分数
        self.prevScore = score
        self.curScore = gameState.getScore()
        # 自己吃了多少豆子
        self.prevFoodCarrying = foodCarrying
        self.curFoodCarrying = gameState.data.agentStates[self.myIndex].numCarrying

    def isTerminal(self):

        return False
            # (self.prevFoodCarrying > 0) and (self.myCurPosition[0] == self.middleLineX)
            # self.curScore != self.prevScore

    def getPossibleActions(self):
        actions = self.gameState.getLegalActions(self.myIndex)
        actions.remove('Stop')
        # print(self.myIndex, self.myCurPosition, actions) if not self.myIndex & 1 else None
        return actions

    def takeAction(self, action):
        return State_2(self.gameState.generateSuccessor(self.myIndex, action),
                       self.curScore,
                       self.curFoodCarrying,
                       self.myIndex,
                       self.isRed,
                       self.enemyFoodList,
                       self.getDistance,
                       self.middleLineX,
                       self.ourMiddleLine,
                       self.wallList)

    def getReward(self):
        discountFactor = 0.001
        reward = 0
        distMid = 0
        minDist = 100
        for i in self.ourMiddleLine:
            minDist = min(minDist,self.getDistance(self.myCurPosition,i))
        distMid = discountFactor * (100 - minDist)*0.1
        minDist = 1000
        for i in self.enemyFoodList:
            minDist = min(minDist,self.getDistance(self.myCurPosition,i))
        distFood = discountFactor* (100 - minDist)
        carry = self.curFoodCarrying*0.3
        score = self.gameState.getScore()
        reward = distFood + carry + score + distMid

        # for i,row in enumerate(self.mapMatrix):
        #     print(row)
        # print('-'*40)

        # reward = score / 100
        # print("index",self.myIndex,"Total:", reward, "Position:",self.myCurPosition," mid: ", distMid," food:", distFood, " carry:",carry," score:",score)
        return reward

    def getIndex(self, index):
        new_index = index + self.myIndex
        if new_index > 3:
            new_index = new_index - 4
        return new_index

    def returnedHome(self, x):
        return x <= self.middleLineX if self.isRed else x >= self.middleLineX
