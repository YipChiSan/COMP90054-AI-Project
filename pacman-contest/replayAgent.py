from captureAgents import CaptureAgent
import pickle

def createTeam(firstIndex, secondIndex, isRed, first = 'RecordAgent', second = 'RecordAgent'):
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

class RecordAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.agentActions = pickle.load(open('./replayAgentActions','rb'), encoding="bytes")
    self.action = [action for i, action in enumerate(self.agentActions) if self.index == action[0]]

  def chooseAction(self, gameState):

    return self.action.pop(0)[1]
