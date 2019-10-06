from captureAgents import CaptureAgent
from newUCT import mcts
from State_2_back import State_2

def createTeam(firstIndex, secondIndex, isRed, first = 'MCTsAgent', second = 'MCTsAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

class MCTsAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        # self.agentActions = pickle.load(open('./replayAgentActions','rb'), encoding="bytes")
        # self.action = [action for i, action in enumerate(self.agentActions) if self.index == action[0]]
        # self.test = mcts(iterationLimit=10)
        self.test = mcts(timeLimit=800)
    def chooseAction(self, gameState):
        score = gameState.getScore()
        t = State_2(self, gameState, self.getScore(gameState), gameState.data.agentStates[self.index].numCarrying)
        # print("position and food:",self.getFood(gameState).asList())
        return self.test.search(t)

        ##################################################################
        # return self.action.pop(0)[1]
