from captureAgents import CaptureAgent
from UCT import mcts
from State_2 import State_2

def createTeam(firstIndex, secondIndex, isRed, first = 'MCTsAgent', second = 'MCTsAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

class MCTsAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        # self.agentActions = pickle.load(open('./replayAgentActions','rb'), encoding="bytes")
        # self.action = [action for i, action in enumerate(self.agentActions) if self.index == action[0]]
        self.test = mcts(timeLimit=800)

    def chooseAction(self, gameState):
        score = gameState.getScore()
        t = State_2(self, gameState, 0, 0)
        print('-'*40)
        return self.test.search(t)

        ##################################################################
        # return self.action.pop(0)[1]
