from captureAgents import CaptureAgent
import pickle

def createTeam(firstIndex, secondIndex, isRed, first = 'MCTsAgent', second = 'MCTsAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

class RecordAgent(CaptureAgent):
    # STEP 1: import
    from State_1 import State_1
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.agentActions = pickle.load(open('./replayAgentActions','rb'), encoding="bytes")
        self.action = [action for i, action in enumerate(self.agentActions) if self.index == action[0]]

        # STEP 2: Initial variables
        self.initState = self.State_1(self, gameState).getInitialStates_1()
        self.previousState = {0: [], 1: [], 2: [], 3: []}

    def chooseAction(self, gameState):
        # STEP 3: Get state features
        currentState = self.State_1(self, gameState).getCurrentState(self.initState)
        row = self.previousState[self.index] + currentState
        self.previousState[self.index] = currentState

        # STEP 4: Append each row to a list (?)
        print(row) if len(row) > len(currentState) else None
        ##################################################################
        return self.action.pop(0)[1]

class MCTsAgent(CaptureAgent):
    # STEP 1: import
    from State_2 import State_2
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.agentActions = pickle.load(open('./replayAgentActions','rb'), encoding="bytes")
        self.action = [action for i, action in enumerate(self.agentActions) if self.index == action[0]]

    def chooseAction(self, gameState):
        mcts = self.State_2(self, gameState)
        currentState = mcts.getCurrentState()
        legalActions = gameState.getLegalActions(self.index)
        for action in legalActions:
            nextState = mcts.getNextState(currentState, action)
            print(action, nextState)
        print('-'*30)
        ##################################################################
        return self.action.pop(0)[1]
