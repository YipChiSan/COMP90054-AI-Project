from captureAgents import CaptureAgent
from UCT import mcts
from State_2 import State_2

def createTeam(firstIndex, secondIndex, isRed, first = 'MCTsAgent', second = 'MCTsAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

class MCTsAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.test = mcts(timeLimit=800)
        # self.test = mcts(iterationLimit=100)

    def chooseAction(self, gameState):
        t = State_2(self.red, self.index, self.getMazeDistance, gameState, 0, 0)
        return self.test.search(t)

        ##################################################################
        # return self.action.pop(0)[1]
