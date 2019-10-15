# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

import sys

sys.path.append('teams/kdbnb/')

import copy
from util import manhattanDistance
import InitialMap
from captureAgents import CaptureAgent
import random, time, util
from game import *
import game
from layout import Grid
import myProblem
from State_1 import *
import random, collections, time
import getEnemyPosition
import util
import gameData
#################
# Team creation #
#################
debug = False
# debug = True
enemyPosition = getEnemyPosition.enemyPosition()
gameData = gameData.gamedata()
deadEnemy = {}
teammateState = {}
enemyCarryFoodNumber = collections.defaultdict(float)
actionHistory = {}
agentMod = {}
positionHistory  ={}

def createTeam(firstIndex, secondIndex, isRed,
               first='AttackAgent', second='AttackAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########


class AttackAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)  # must be put ahead to set value of self.red
        self.walls = gameState.getWalls()
        self.mapMatrix = self.getMapMatrix(gameState)
        self.midX = self.getMiddleX(gameState)
        self.enemyMidX = self.getEnemyMiddleX(gameState)
        self.ourRegionX = range(0, self.midX + 1) if self.red else range(self.midX, len(self.mapMatrix[0]))
        self.enemyRegionX = range(self.midX + 1, len(self.mapMatrix[0])) if self.red else range(0, self.midX)
        self.midLine = self.getMiddleLine(gameState)
        self.enemyMidLine = self.getEnemyMiddleLine(gameState)
        self.capsules = self.getCapsules(gameState)
        self.deadEnd = InitialMap.searchDeadEnd(self.mapMatrix)  # keys are deadEnds, values are corresponding depth
        self.sumOfFood = len(self.getFood(gameState).asList())
        # used for separate pacman
        self.randomFoodIndex = random.randint(0, self.sumOfFood - 1)
        self.manhattanSight = self.getManhattanSight()
        self.randomSelectFood = True
        self.allienIndex = (self.index + 2) % 4
        self.lastAction = None
        # list of Xs of region for different sidee
        if self.red:
            self.enemyIndex = [1, 3]
            deadEnemy[1] = 0
            deadEnemy[3] = 0
        else:
            self.enemyIndex = [0, 2]
            deadEnemy[0] = 0
            deadEnemy[2] = 0
        if gameState.data.timeleft == 1200:
            enemyPosition.start = True
            enemyPosition.initial(gameState, self.red, self.mapMatrix)
        self.enemyDied = {}
        self.enemyDied[self.enemyIndex[0]] = False
        self.enemyDied[self.enemyIndex[1]] = False

        actionHistory[self.index] = []
        agentMod[self.index] = []

    def getMapMatrix(self, gameState):
        """
        Start counting from the top-left corner

        0 1 2 ➡
        1
        2
        ⬇

        0: Walls
        1: Available movements
        2: RedFood
        3: RedCapsule
        4: BlueFood
        5: BlueCapsule
        """
        mapMatrix = gameState.deepCopy().data.layout.layoutText
        mapHeight = len(mapMatrix)
        for i in range(mapHeight):
            mapMatrix[i] = mapMatrix[i].replace('%', '0')
            mapMatrix[i] = mapMatrix[i].replace(' ', '1')
            mapMatrix[i] = mapMatrix[i].replace('.', '1')
            mapMatrix[i] = mapMatrix[i].replace('o', '1')
            mapMatrix[i] = mapMatrix[i].replace('1', '1')
            mapMatrix[i] = mapMatrix[i].replace('2', '1')
            mapMatrix[i] = mapMatrix[i].replace('3', '1')
            mapMatrix[i] = mapMatrix[i].replace('4', '1')
            mapMatrix[i] = list(mapMatrix[i])
            mapMatrix[i] = list(map(float, mapMatrix[i]))
        for redFood in gameState.getRedFood().asList():
            x = redFood[0]
            y = mapHeight - 1 - redFood[1]
            mapMatrix[y][x] = 2.0
        for redCapsule in gameState.getRedCapsules():
            if not redCapsule:
                continue
            x = redCapsule[0]
            y = mapHeight - 1 - redCapsule[1]
            mapMatrix[y][x] = 3.0
        for blueFood in gameState.getBlueFood().asList():
            x = blueFood[0]
            y = mapHeight - 1 - blueFood[1]
            mapMatrix[y][x] = 4.0
        for blueCapsule in gameState.getBlueCapsules():
            if not blueCapsule:
                continue
            x = blueCapsule[0]
            y = mapHeight - 1 - blueCapsule[1]
            mapMatrix[y][x] = 5.0
        return mapMatrix

    def getMiddleX(self, gameState):
        mapWidth = gameState.data.layout.width
        if self.red:
            x = int((mapWidth - 2) / 2)
        else:
            x = int((mapWidth - 2) / 2 + 1)
        return x

    def getEnemyMiddleX(self, gameState):  # x of middle line on enemy's side
        mapWidth = gameState.data.layout.width
        if self.red:
            enemyX = int((mapWidth - 2) / 2 + 1)
        else:
            enemyX = int((mapWidth - 2) / 2)
        return enemyX

    def getMiddleLine(self, gameState):
        midLine = []
        mapHeight = gameState.data.layout.height
        x = self.midX
        wallList = gameState.getWalls().asList()
        for y in range(1, mapHeight):
            if (x, y) not in wallList:
                midLine.append((x, y))
        return midLine

    def getEnemyMiddleLine(self, gameState):
        enemyMidLine = []
        mapHeight = gameState.data.layout.height
        x = self.enemyMidX
        wallList = gameState.getWalls().asList()
        for y in range(1, mapHeight):
            if (x, y) not in wallList:
                enemyMidLine.append((x, y))
        return enemyMidLine

    def getIndex(self, index):  # 0:self;2:teammate;1/3:enemy
        new_index = index + self.index
        if new_index > 3:
            new_index = new_index - 4
        return new_index

    def getMinDistToEnemy(self, curPos, enemyList):
        curMinDist = 99999
        for enemy in enemyList:
            dist = self.distancer.getDistance(enemy, curPos)
            curMinDist = min(dist, curMinDist)
        return curMinDist

    def getAgentIndexCloseToTarget(self, gameState, curPos, teammatePos, targetList):
        curMinDist = 99999
        for target in targetList:
            dist = self.distancer.getDistance(curPos, target)
            curMinDist = min(dist, curMinDist)
        teammateMinDist = 99999
        for target in targetList:
            dist = self.distancer.getDistance(teammatePos, target)
            teammateMinDist = min(dist, teammateMinDist)
        if curMinDist <= teammateMinDist:
            return self.index
        else:
            return self.getIndex(2)

    # def capsuleEatenLastMove(self, gameState):
    #   prevGameState = self.getPreviousObservation()
    #   if prevGameState != None:
    #     prevCapsules = self.getCapsules(prevGameState)
    #     curCapsules = self.getCapsules(gameState)
    #     for capsule in prevCapsules:
    #       if capsule not in curCapsules:
    #         return True
    #   return False

    def pacmanEnemy(self, enemyList):
        res = []
        for pos in enemyList:
            if pos != None and pos[0] in self.ourRegionX:
                res.append(pos)
        return res

    def ghostEnemy(self, enemyList):
        res = []
        for pos in enemyList:
            if pos != None and pos[0] in self.enemyRegionX:
                res.append(pos)
        return res

    def enemySucide(self, gameState):
        eatEnemy = {}
        for i in self.enemyIndex:
            eatEnemy[i] = False
        if gameState.data.timeleft < 1190:
            preGameState = self.getPreviousObservation()
            curPos = gameState.getAgentPosition(self.index)
            curPosTeammate = gameState.getAgentPosition(self.allienIndex)
            for enemyIndex in self.enemyIndex:
                curPosE = gameState.getAgentPosition(enemyIndex)
                prePosE = preGameState.getAgentPosition(enemyIndex)
                if curPosE is None and (not prePosE is None):
                    distance1 = self.distancer.getDistance(curPos, prePosE)
                    distance2 = self.distancer.getDistance(curPosTeammate, prePosE)
                    if (distance1 == 1) or (distance2 == 1):
                        eatEnemy[enemyIndex] = True
        return eatEnemy

    def eatEnemy1(self, gameState, action):
        eatEnemy = {}
        nextGameState = gameState.generateSuccessor(self.index, action)
        nextPos = nextGameState.getAgentPosition(self.index)
        for index in self.enemyIndex:
            curPosE = gameState.getAgentPosition(index)
            nextPosE = nextGameState.getAgentPosition(index)
            # if debug:
            #     print("Sel next pos:", nextPos, "Enemy Current", curPosE, "Enemy Next", nextPosE)
            if (gameState.getInitialAgentPosition(index) == nextPosE):
                eatEnemy[index] = True
            else:
                eatEnemy[index] = False
        return eatEnemy

    def eatEnemy(self, gameState):
        eatEnemy = {}
        preGameState = self.getPreviousObservation()
        for index in self.enemyIndex:
            eatEnemy[index] = False
            if gameState.data.timeleft < 1190:
                enemyCur = gameState.getAgentPosition(index)
                enemyPre = preGameState.getAgentPosition(index)
                posPre = preGameState.getAgentPosition(self.index)
                allienPre = preGameState.getAgentPosition(self.allienIndex)
                if enemyCur is None and (not enemyPre is None) and (
                    gameState.getAgentPosition(self.index) != gameState.getInitialAgentPosition(self.index)):
                    distance = self.distancer.getDistance(posPre, enemyPre)
                    distance2 = self.distancer.getDistance(allienPre, enemyPre)
                    if (distance < 2) or (distance2 < 2):
                        eatEnemy[index] = True
                    else:
                        eatEnemy[index] = False
                else:
                    if (not enemyPre is None) and (enemyCur is None):
                        distance = self.distancer.getDistance(posPre, enemyPre)
                        if distance > 2:
                            eatEnemy[index] = True
                        else:
                            eatEnemy[index] = False
                    else:
                        eatEnemy[index] = False
        return eatEnemy

    def getEnemyTrueP(self, gameState):
        enemyPosition = {}
        if self.red:
            enemyPosition[1] = gameState.getAgentPosition(1)
            enemyPosition[3] = gameState.getAgentPosition(3)
        else:
            enemyPosition[0] = gameState.getAgentPosition(0)
            enemyPosition[2] = gameState.getAgentPosition(2)
        return enemyPosition

    def foodBeenEaten(self, gameState):
        if gameState.data.timeleft < 1190:
            curFoods = self.getFoodYouAreDefending(gameState).asList()
                                                  # self.getPreviousObservation()
            preFoods = self.getFoodYouAreDefending(teammateState[self.allienIndex]).asList()
        else:
            return set()
        return set(preFoods) - set(curFoods)

    def capsuleBeenEaten(self, gameState):
        if gameState.data.timeleft < 1190:
            curCap = self.getCapsulesYouAreDefending(gameState)
            preCap = self.getCapsulesYouAreDefending(self.getPreviousObservation())
        else:
            return set()
        return set(preCap) - set(curCap)

    def getEnemyPosition(self, gameState):
        curPos = gameState.getAgentPosition(self.index)
        noiseDistance = gameState.agentDistances
        if gameState.data.timeleft < 1200:
            eatEnemy = self.enemySucide(gameState)
            for i in eatEnemy:
                if eatEnemy[i] and deadEnemy[i] == 0:
                    enemyPosition.updateWithDeath(i)
                    deadEnemy[i] = 4
                else:
                    enemyPosition.updateWithNoise(noiseDistance, self.index, curPos, i)
            enemyTruePosition = self.getEnemyTrueP(gameState)
            for i in enemyTruePosition:
                if not enemyTruePosition[i] is None:
                    enemyPosition.updateWithVision(i, enemyTruePosition[i])
            if len(self.foodBeenEaten(gameState)) != 0:
                enemyPosition.updateWithEatenFood(list(self.foodBeenEaten(gameState))[0])
            if len(self.capsuleBeenEaten(gameState)) != 0:
                enemyPosition.updateWithEatenFood(list(self.capsuleBeenEaten(gameState))[0])
            a = enemyPosition.enemyPosition
        #     return a
        # return {}

    def getEnemyInRegion(self, enemyPosition):
        enemyInRegion = {}
        enemy = {}
        for index in self.enemyIndex:
            enemyInRegion[index] = [0,0]
            for pos in enemyPosition[index]:
                if pos[0] in self.ourRegionX:
                    enemyInRegion[index][0] += 1
                else:
                    enemyInRegion[index][1] +=1
            total = enemyInRegion[index][0]+enemyInRegion[index][1]
            pro = enemyInRegion[index][0]/total
            if pro>0.8:
                enemy[index] = "Our"
            else:
                if pro > 0.5:
                    enemy[index] = "Mid"
                else:
                    enemy[index] = "Enemy"
        return enemy

    def updateDeath(self, gameState, action):
        enemyDeath = self.eatEnemy1(gameState, action)
        for i in enemyDeath:
            if enemyDeath[i]:
                enemyPosition.updateWithDeath(i)
                deadEnemy[i] = 4

    def getBlockRegions(self, gameState):
        block = []
        cur = gameState.getAgentPosition(self.index)
        for i in self.enemyIndex:
            enemy = gameState.getAgentPosition(i)
            if not enemy is None:
                enemyDistance = self.distancer.getDistance(cur, enemy)
                depth = enemyDistance / 2
                for cell in self.deadEnd:
                    if self.deadEnd[cell] >= depth:
                        block.append(cell)
        return list(set(block))

    def getNeedOfDefenceEnemyPosition(self, gameState, enemyPosition):
        curFoods = self.getFoodYouAreDefending(gameState).asList()
        enemyPositionDict = {}
        for index in self.enemyIndex:
            minDis = 999999
            minPos = None
            for food in curFoods:
                for pos in enemyPosition[index]:
                    dis = self.distancer.getDistance(food, pos)
                    if dis < minDis:
                        minDis = dis
                        minPos = pos
            enemyPositionDict[index] = minPos
        # if debug:
        #     for i in enemyPositionList:
        #         self.debugDraw(i, [.9,0,0]) if i else None
        return enemyPositionDict

    def getFoodFarFromEnemy(self, curPos, enemyPositionToDefend):
        curFoods = self.foodGrid.asList()
        minDis = 999999
        minPos = None
        enemyList = []
        for i in enemyPositionToDefend:
            enemyList.append(enemyPositionToDefend[i])
        for i in curFoods:
            distanceToFood = self.distancer.getDistance(curPos, i)
            distanceToGhost = min(map(lambda x: self.distancer.getDistance(x, curPos), enemyList))
            dis = distanceToFood - distanceToGhost
            if dis < minDis:
                minDis = dis
                minPos = i
        # if debug:
        #     self.debugDraw(minPos, [.98,.41,.07]) if minPos else None
        return minPos

    def getMiddleLinePositionToAttack(self, enemyPositionToDefend):
        curFoods = self.foodGrid.asList()
        maxDis = float("-inf")
        maxPos = None
        enemyList = []
        for i in enemyPositionToDefend:
            enemyList.append(enemyPositionToDefend[i])
        for i in curFoods:
            for j in self.midLine:
                distanceToFood = self.distancer.getDistance(j, i)
                distanceToGhost = min(map(lambda x: self.distancer.getDistance(x, j), enemyList))
                dis = distanceToGhost - distanceToFood
                if dis > maxDis:
                    maxDis = dis
                    maxPos = j
        return maxPos

    def getManhattanSight(self):
        v = []
        for i in range(-5,6):
            for j in range(-5, 6):
                if abs(i) + abs(j) <= 5:
                    v.append((i,j))
        return v

    def getEnemySight(self, enemyPosition):
        sights = {}
        sight = collections.defaultdict(int)
        for index in self.enemyIndex:
            for enemyX, enemyY in enemyPosition[index]:
                for sightX, sightY in self.manhattanSight:
                    s = (enemyX + sightX, enemyY + sightY)
                    sight[s] += 1
            sights[index] = sight
        return sights

    def scoreChanged(self, gameState):
        myCurScore = 0
        teammateNextMoveScore = 0
        if gameState.data.timeleft < 1190:
            myCurScore = gameState.data.score
            teammateNextMoveScore = teammateState[self.allienIndex].data.score
        scoreChange = myCurScore - teammateNextMoveScore
        return scoreChange

    def getEnemyCarryFoodNumber(self, gameState, enemyPosition):
        enemyKeys = list(enemyPosition.keys())
        foodBeenEaten = list(self.foodBeenEaten(gameState))
        if len(foodBeenEaten) != 0:
            food = foodBeenEaten[0]
            if food in enemyPosition[enemyKeys[0]] and food not in enemyPosition[enemyKeys[1]]:
                enemyCarryFoodNumber[enemyKeys[0]] += 1
            elif food in enemyPosition[enemyKeys[1]] and food not in enemyPosition[enemyKeys[0]]:
                enemyCarryFoodNumber[enemyKeys[1]] += 1
            elif food in enemyPosition[enemyKeys[0]] and food in enemyPosition[enemyKeys[1]]:
                enemyCarryFoodNumber[enemyKeys[1]] += 0.5
        scoreChanged = self.scoreChanged(gameState)
        if scoreChanged:
            for pos in enemyPosition[enemyKeys[0]]:
                if pos in self.enemyMidLine:
                    enemyCarryFoodNumber[enemyKeys[0]] = 0
            for pos in enemyPosition[enemyKeys[1]]:
                if pos in self.enemyMidLine:
                    enemyCarryFoodNumber[enemyKeys[1]] = 0
        if deadEnemy[enemyKeys[0]]:
            enemyCarryFoodNumber[enemyKeys[0]] = 0
        if deadEnemy[enemyKeys[1]]:
            enemyCarryFoodNumber[enemyKeys[1]] = 0

    def getClostestMidDistance(self,curPos):
        minDist = 999
        closestMid = random.choice(self.midLine)
        for i in self.midLine:
            dist = self.distancer.getDistance(curPos,i)
            if minDist > dist:
                minDist = dist
                closestMid = i
        return minDist,closestMid

    def updateEnemyDied(self):
        for index in self.enemyDied:
            if self.enemyDied[index]:
                if self.enemyInRegion[index] != "Enemy":
                    self.enemyDied[index] = False
            else:
                if deadEnemy[index]> 0:
                    self.enemyDied[index] = True
                else:
                    self.enemyDied[index] = False
                if self.enemyDied[index]:
                    print("enemy Died")

    def getSafeFood(self,gameState,block):
        foodList = self.getFood(gameState).asList()
        return list(set(foodList) - set(block))

    def getEnemyAllatHome(self):
        enemyAllHome = True
        for enemy in self.enemyInRegion:
            enemyAllHome = enemyAllHome & (self.enemyInRegion[enemy] != "Our")
        return enemyAllHome

    def getEnemyOneAtHome(self):
        enemyOneAtHome = False
        for enemy in self.enemyInRegion:
            enemyOneAtHome = enemyOneAtHome or (self.enemyInRegion[enemy] == "Our")
        return enemyOneAtHome

    def getEnemyAllAtOur(self):
        enemyAllOur = True
        for enemy in self.enemyInRegion:
            enemyAllOur = enemyAllOur & (self.enemyInRegion[enemy] == "Our")
        return enemyAllOur

    def getEnemyNeedToTrace(self):
        minDist = 999999
        enemy = self.enemyIndex[0]
        for index in self.enemyIndex:
            if self.enemyInRegion[index] == "Our":
                minDist = min(minDist,self.distancer.getDistance(self.enemyPositionsToDefend[index],self.curPos))
                enemy = index
        return enemy

    def getClosedFood(self):
        minDist = 999999
        foods = self.foodGrid.asList()
        food = foods[0]
        for i in foods:
            dist = self.distancer.getDistance(i,self.curPos)
            if dist < minDist:
                food = i
                minDist = dist
        return food

    def getTeammateTargetRegion(self,gameState):
        foodCluster = []
        if agentMod[self.allienIndex] != []:
            if agentMod[self.allienIndex][0] == "eatFood":
                foodCluster = InitialMap.cluster1(gameState,agentMod[self.allienIndex][1],self)
                # self.debugClear()
                # for i in foodCluster:
                #     self.debugDraw(i,[0.3,self.index / 4,.5])
                # self.debugDraw(agentMod[self.allienIndex][1],[0.9,0.6,0.1])
        return foodCluster

    def getEnemyInsightTogether(self,enemyInsight):
        posInsight = {}
        for i in enemyInsight:
            for j in enemyInsight[i]:
                if j in posInsight:
                    posInsight[j] = posInsight[j] + enemyInsight[i][j]
                else:
                    posInsight[j] = enemyInsight[i][j]
        return posInsight

    def getFoodsAroundCapsules(self, gameState):
        d = dict()
        foodList = self.getFood(gameState).asList()
        for capsule in self.capsules:
            l = []
            for food in foodList:
                if self.distancer.getDistance(food, capsule) <= 20:
                    l.append(food)
            d[capsule] = l
        return d

    def getCapsuleScore(self, gameState):
        foodList = self.getFood(gameState).asList()
        d = collections.defaultdict(int)
        deadEnd = self.deadEnd.keys()
        for capsule in self.capsules:
            for food in foodList:
                if self.distancer.getDistance(food, capsule) <= 20:
                    if food in deadEnd:
                        d[capsule] += self.deadEnd[food]
        return d

    def curInsightOfEnemy(self, curPos, enemyList):
        insight = False
        for enemy in enemyList:
            if enemy != None:
                insight = insight or (manhattanDistance(curPos, enemy) <= 5)
        return insight

    def convertActionsToPath(self, startPos, actions):
        x, y = startPos
        pathList = []
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            pathList.append((nextx, nexty))
            x = nextx
            y = nexty
        return pathList

    def pathToCloseFoodFromEnemy(self, gameState, enemyPos):
        problem = myProblem.EnemyEatCloseFoodProblem(gameState, self, enemyPos)
        actions, target = self.aStarSearch(problem, gameState, problem.EnemyEatCloseFoodHeuristic, 0.3)
        if actions == [] or actions == "TIMEEXCEED" or actions == None:
            return []
        else:
            pathList = self.convertActionsToPath(enemyPos, actions)
        return pathList

    def pathToMidEnemy(self,gameState,enemyPos):
        problem = myProblem.EnemyBackToMid(gameState, self, enemyPos)
        actions, target = self.aStarSearch(problem, gameState, problem.BackToMidHeuristic, 0.3)
        if actions == [] or actions == "TIMEEXCEED" or actions == None:
            return []
        else:
            pathList = self.convertActionsToPath(enemyPos, actions)
        return pathList


    def getClosedEnemy(self,gameState):
        enemyPos = self.getEnemyTrueP(gameState)
        chasePos = None
        food = -1
        for i in self.enemyIndex:
            if (self.enemyInRegion[i] == "Our" or enemyPos[i] in self.enemyMidLine) and (not enemyPos[i] is None):
                if food < self.enemyCarryFood[i]:
                    food = self.enemyCarryFood[i]
                    chasePos = enemyPos[i]
        return chasePos

    def interceptToMid(self,gameState):
        enemyChase = self.getClosedEnemy(gameState)
        if not enemyChase is None:
            print("*************intercept****************")
            path = self.pathToMidEnemy(gameState,enemyChase)
            # action,target = myProblem.minDistance(self.curPos,path,self.walls,self)
            for i in path:
                if debug:
                    self.debugDraw(i,[0.6,0.3,0.7])
            minDist = 9999
            action,target = myProblem.minDistance(self.curPos,[enemyChase],self.walls,self)
            (x,y) = self.curPos
            if path != []:
                for direction in [Directions.NORTH, Directions.SOUTH, Directions.WEST,Directions.EAST,Directions.STOP]:  # , Directions.EAST]:
                    dx, dy = Actions.directionToVector(direction)
                    nextx, nexty = int(x + dx), int(y + dy)
                    # print("test",self.curPos,(nextx,nexty),path)
                    if not (nextx,nexty) in self.walls.asList() and (not (nextx,nexty) in self.enemyMidLine):
                        distToPath = min(map(lambda a: self.distancer.getDistance(a, (nextx,nexty)), path))
                        distToEnemy = self.distancer.getDistance((nextx,nexty),enemyChase)
                        dist = distToEnemy + distToPath
                        if dist < minDist:
                            minDist = dist
                            action = direction
                            target = (nextx,nexty)
            mode = (action,("trace",target))
        else:
            mode = ()
        return mode

    def intercept(self,gameState):

        enemyChase = self.getClosedEnemy(gameState)
        if not enemyChase is None:
            print("*************intercept****************")
            path = self.pathToCloseFoodFromEnemy(gameState,enemyChase)
            # action,target = myProblem.minDistance(self.curPos,path,self.walls,self)
            for i in path:
                if debug:
                    self.debugDraw(i,[0.6,0.3,0.7])
            minDist = 9999
            action,target = myProblem.minDistance(self.curPos,[enemyChase],self.walls,self)
            (x,y) = self.curPos
            if path != []:
                for direction in [Directions.NORTH, Directions.SOUTH, Directions.WEST,Directions.EAST,Directions.STOP]:  # , Directions.EAST]:
                    dx, dy = Actions.directionToVector(direction)
                    nextx, nexty = int(x + dx), int(y + dy)
                    # print("test",self.curPos,(nextx,nexty),path)
                    if not (nextx,nexty) in self.walls.asList() and (not (nextx,nexty) in self.enemyMidLine):
                        distToPath = min(map(lambda a: self.distancer.getDistance(a, (nextx,nexty)), path))
                        distToEnemy = self.distancer.getDistance((nextx,nexty),enemyChase)
                        dist = distToEnemy + distToPath
                        if dist < minDist:
                            minDist = dist
                            action = direction
                            target = (nextx,nexty)
            mode = (action,("trace",target))
        else:
            mode = ()
        return mode

    def curCloseToEnemy(self, curPos, enemyList):
        close = False
        for enemy in enemyList:
            if not (enemy is None):
                close = close or (self.distancer.getDistance(curPos, enemy) <= 2)
        return close

    def removeFoodsForTeammate(self,foodCluster):
        for i in foodCluster:
            dist1 = self.distancer.getDistance(i,self.curPos)
            dist2 = self.distancer.getDistance(i,self.teammatePos)
            # print(self.curPos,self.teammatePos,i,dist1,dist2)
            if dist1 > dist2 - 5:
                self.foodGrid[i[0]][i[1]] = False

    ####################################################################################################################
    def chooseAction(self, gameState):
        print("=============",self.index,"==============")
        for i in deadEnemy:
            if deadEnemy[i] > 0:
                deadEnemy[i] += -1
        self.debugClear()
        self.capsules = self.getCapsules(gameState)
        self.curPos = gameState.getAgentPosition(self.index)
        teammateCluster = self.getTeammateTargetRegion(gameState)
        enemyIndices = self.getOpponents(gameState)
        self.enemyPos = []
        for idx in enemyIndices:
            self.enemyPos.append(gameState.getAgentPosition(idx))
        self.foodGrid = self.getFood(gameState)
        self.carryFoods = gameState.data.agentStates[self.index].numCarrying
        teammateIndex = self.getIndex(2)
        self.teammatePos = gameState.getAgentPosition(teammateIndex)
        self.curInDangerous = self.inDanger(self.curPos)
        self.teammateInDangerous = self.curInsightOfEnemy(self.teammatePos,self.enemyPos)
        self.enemyPositionsToDefend = self.getNeedOfDefenceEnemyPosition(gameState, enemyPosition.enemyPosition)
        enemySight = self.getEnemySight(enemyPosition.enemyPosition) # [ [(),(),()...], [(),(),(),...] ]
        posInsight = self.getEnemyInsightTogether(enemySight)
        foodCluster = self.getTeammateTargetRegion(gameState)
        self.getEnemyPosition(gameState)
        self.enemyInRegion = self.getEnemyInRegion(enemyPosition.enemyPosition)
        self.enemyAllHome = self.getEnemyAllatHome()
        self.getEnemyCarryFoodNumber(gameState, enemyPosition.enemyPosition)
        # self.ghostEnemy = self.ghostEnemy(self.enemyPos)
        # self.pacmanEnemy = self.pacmanEnemy(self.enemyPos)
        self.teammateCarryFood = gameState.data.agentStates[self.allienIndex].numCarrying
        self.enemyCarryFood = {}
        self.canAttact = self.foodGrid.asList() != [] and len(self.getFood(gameState).asList()) > 2
        for i in self.enemyIndex:
            self.enemyCarryFood[i] = gameState.data.agentStates[i].numCarrying
        self.block = self.getBlockRegions(gameState)
        self.ownScaredTimer = gameState.data.agentStates[self.index].scaredTimer
        self.enemyScaredTimer = [gameState.data.agentStates[idx].scaredTimer for idx in enemyIndices]
        self.numOfFoodCarried = gameState.data.agentStates[self.index].numCarrying
        self.foodGrid = self.getFood(gameState)
        self.numOfFoodLeft = len(self.foodGrid.asList())
        self.removeFoodsForTeammate(foodCluster)
        self.foodList = self.foodGrid.asList()
        for i in self.foodGrid.asList():
            if debug:
                self.debugDraw(i,[0,self.index / 3,self.index / 2])
        # distance to the closest point in own middle line
        minDistToOwnMid = 999999
        for midPoint in self.midLine:
            newDist = self.distancer.getDistance(self.curPos, midPoint)
            if newDist < minDistToOwnMid:
                minDistToOwnMid = newDist
                # closestOwnMidPos = midPoint
        minDistToFood = 999999
        for foodPos in self.foodList:
            newDist = self.distancer.getDistance(self.curPos, foodPos)
            if newDist < minDistToFood:
                minDistToFood = newDist

        close = self.curCloseToEnemy(self.curPos, self.enemyPos)
        insight = self.curInsightOfEnemy(self.curPos, self.enemyPos)
        self.updateEnemyDied()
        ### BEGIN
        mode = self.helpTeammate(gameState)
        if mode != ():
            action, agentMod[self.index] = mode
        else:
            mode = self.inOurRegion(gameState)
            if mode != ():
                action, agentMod[self.index] = mode
            else:
                mode = self.enemyScaredPolicy(gameState)
                print('@@@@@@@@', mode)
                if mode != ():
                    action, agentMod[self.index] = mode
                else:
                    mode = self.attack(gameState)
                    if mode != ():
                        action, agentMod[self.index] = mode
                    else:
                        action = 'Stop'
                        agentMod[self.index] = ("stop",self.curPos)
        self.updateDeath(gameState, action)
        teammateState[self.index] = gameState.generateSuccessor(self.index,action)
        actionHistory[self.index].append(action)
        self.lastAction = action
        return action

    def enemyScaredPolicy(self, gameState):
        minPos, minDistToOwnMid = self.getDistanceToOurMid(self.curPos)
        # enemy scared
        mode = ()
        timer = None  # None for not using capsule logic
        if (self.enemyScaredTimer[0] > 0 or self.enemyScaredTimer[1] > 0) and self.curPos[0] in self.enemyRegionX:  # enemy is scared
            if len(self.foodGrid.asList()) <= 2:
                action, target = myProblem.reachOwnMidList(self, gameState, self.index)
                mode = action, ("backToMid", target)
                print('scared1',self.index, mode)
                return mode
            if self.enemyScaredTimer[0] > 0 and self.enemyPos[0] != None:
                if self.enemyScaredTimer[1] > 0 and self.enemyPos[1] != None:
                    timer = min(self.enemyScaredTimer[0], self.enemyScaredTimer[1])
                elif self.enemyPos[1] == None:
                    timer = self.enemyScaredTimer[0]
                elif self.enemyScaredTimer[1] == 0 and self.enemyPos[1] != None:
                    # fixme: 5 need to be modified
                    if self.distancer.getDistance(self.curPos, self.enemyPos[1]) > 5:
                        timer = self.enemyScaredTimer[0]
                if timer != None and timer <= minDistToOwnMid + 1:
                    action, target = myProblem.reachOwnMidList(self, gameState, self.index)
                    mode = action, ("backToMid", target)
                    print('scared2',self.index, mode)
                elif timer != None and timer > minDistToOwnMid + 1:
                    action, target = myProblem.minDistance(self.curPos,self.foodGrid.asList(),self.walls,self)
                        # eatCloseFood(self, gameState, self.index)
                    mode = action, ("eatFood", target)
                    print('scared3',self.index, mode)
            elif self.enemyPos[0] == None:
                if self.enemyScaredTimer[1] > 0 and self.enemyPos[1] != None:
                    timer = self.enemyScaredTimer[1]
                if timer != None and timer <= minDistToOwnMid + 1:
                    action, target = myProblem.reachOwnMidList(self, gameState, self.index)
                    mode = action, ("backToMid", target)
                    print('scared4',self.index, mode)
                elif timer != None and timer > minDistToOwnMid + 1:
                    action, target = myProblem.minDistance(self.curPos,self.foodGrid.asList(),self.walls,self)

                    # action, target = myProblem.eatCloseFood(self, gameState, self.index)
                    mode = action, ("eatFood", target)
                    print('scared5',self.index, mode)
            else:  # self.enemyScaredTimer[0] == 0 and enemyPos[0] != None
                # fixme: 5 need to be modified
                if self.distancer.getDistance(self.curPos, self.enemyPos[0]) > 5:
                    timer = self.enemyScaredTimer[1]
                if timer != None and timer <= minDistToOwnMid + 1:
                    action, target = myProblem.reachOwnMidList(self, gameState, self.index)
                    mode = action, ("backToMid", target)
                    print('scared6',self.index, mode)
                elif timer != None and timer > minDistToOwnMid + 1:
                    # action, target = myProblem.eatCloseFood(self, gameState, self.index)
                    action, target = myProblem.minDistance(self.curPos,self.foodGrid.asList(),self.walls,self)
                    mode = action, ("eatFood", target)
                    print('scared7',self.index, mode)
        # print('scared1',self.index, mode)
        return mode

    def legalAction(self, action):
        return not (action == [] or action == None or action == "TIMEEXCEED")

    def attack(self, gameState):
        mode = ()
        if self.foodGrid.asList() != [] and len(self.getFood(gameState).asList()) > 2:
            if self.curInDangerous:
                problem = myProblem.EatOneSafeFoodProblem(gameState,self)
                actions1, target1 = self.aStarSearch(problem,gameState,problem.eatOneSafeHeuristic, 0.4)
                hasSafefood = self.legalAction(actions1)

                problem = myProblem.EatCapsuleProblem(gameState, self)
                actions2, target2 = self.aStarSearch(problem, gameState, problem.eatCapsuleHeuristic, 0.2)
                hasCapsule = self.legalAction(actions2)

                problem = myProblem.EscapeProblem1(gameState, self)
                actions3, target3 = self.aStarSearch(problem, gameState, problem.EscapeHeuristic, 0.2)
                hasPathToEscape = self.legalAction(actions3)

                distanceToNearestFood = len(actions1) if actions1 else 999999
                distanceToNearestCapsule = len(actions2) if actions2 else 999999
                distanceToEscape = len(actions3) if actions3 else 999999
                print("========= attack ============")
                print(hasCapsule)
                if hasSafefood and not hasCapsule and not hasPathToEscape:
                    mode = (actions1[0], ("eatFood",target1))
                    print('1',mode)

                elif not hasSafefood and hasCapsule and not hasPathToEscape:

                    mode = (actions2[0], ("eatCapsule",target2))
                    print('2',mode)
                elif not hasSafefood and not hasCapsule and hasPathToEscape:
                    mode = (actions3[0], ("backToMid",target3))
                    print('3',mode)
                elif not hasSafefood and hasCapsule and hasPathToEscape:
                    if self.carryFoods > (len(self.getFood(gameState).asList()) / 3) :
                        # if distanceToEscape < distanceToNearestCapsule + (len(self.getFoodsAroundCapsules(gameState)[target2]) / 5):
                        #     print('4')
                        #     mode = (actions3[0], ("backToMid",target3))
                        # else:
                        mode = (actions2[0], ("eatCapsule",target2))
                        print('5',mode)
                    else:
                        mode = (actions2[0], ("eatCapsule",target2))
                        print('5.5',mode)
                elif hasSafefood and hasCapsule and hasPathToEscape:
                    if self.carryFoods > 0:
                        # (len(self.getFood(gameState).asList()) / 3) :
                        if distanceToEscape <= 1:
                                # distanceToNearestCapsule + (len(self.getFoodsAroundCapsules(gameState)[target2])):
                            mode = (actions3[0], ("backToMid",target3))
                            print('6',mode)
                        else:
                            mode = (actions2[0], ("eatCapsule",target2))
                            print('7',mode)
                    else:
                        # if self.carryFoods > 0:
                        #     map = {
                        #         distanceToNearestFood: (actions1[0], ("eatFood", target1)),
                        #         distanceToNearestCapsule: (actions2[0], ("eatCapsule", target2)),
                        #         distanceToEscape+10: (actions3[0], ("backToMid", target3))
                        #     }
                        #     minDis = min(distanceToNearestFood, distanceToNearestCapsule,distanceToEscape+10)
                        # else:
                        map = {
                            distanceToNearestFood: (actions1[0], ("eatFood", target1)),
                            distanceToNearestCapsule: (actions2[0], ("eatCapsule", target2))
                        }
                        minDis = min(distanceToNearestFood, distanceToNearestCapsule)
                        mode = map[minDis]
                        print("8",mode)
                elif hasSafefood and hasCapsule and not hasPathToEscape:
                    if self.carryFoods >= len(self.getFood(gameState).asList()) :

                        mode = (actions2[0], ("eatCapsule",target2))
                        print('9',mode)
                    elif hasSafefood:
                        if distanceToNearestFood + 3 < distanceToNearestCapsule:

                            mode = (actions1[0], ("eatFood",target1))
                            print('10',mode)
                        else:

                            mode = (actions2[0], ("eatCapsule",target2))
                            print('11',mode)
                elif hasSafefood and not hasCapsule and hasPathToEscape:
                    if self.carryFoods >= len(self.getFood(gameState).asList()):
                        mode = (actions3[0], ("backToMid",target3))
                        print('12',mode)
                    else:
                        # if distanceToNearestFood + 3 < distanceToEscape:
                        mode = (actions1[0], ("eatFood",target1))
                        print('13', mode)
                        # else:
                        #     print('14')
                        #     mode = (actions3[0], ("backToMid",target3))
                elif not hasSafefood and not hasCapsule and not hasPathToEscape:
                    action, target = myProblem.reachOwnMidWithEnemyInsight(self, gameState, self.index)
                    mode = (action, ("needHelp",target))
                    print('15', mode)
                else:
                    print('ERROR @'*40)
            else:
                # foodFarFromEnemy = self.getFoodFarFromEnemy(self.curPos, self.enemyPositionsToDefend)
                closestFood = self.getClosedFood()
                if debug:
                    self.debugDraw(closestFood,[self.index/3,0.3,0.6])
                midDis, midPos = self.getClostestMidDistance(self.curPos)
                foodDis = self.distancer.getDistance(closestFood, self.curPos)
                if (foodDis > midDis + 5) and (self.carryFoods > 0) and (midDis < 2):
                    action, target = myProblem.minDistance(self.curPos, [midPos], self.walls, self)
                    mode = (action, ("backToMid", target))
                    print(self.index,mode)
                else:
                    action, target = myProblem.minDistance(self.curPos, self.foodGrid.asList(), self.walls, self)
                    mode = (action, ("eatFood", target))
                    print(self.index,mode)
        else:
            if self.curInDangerous:
                action, target = myProblem.reachOwnMidWithEnemyInsight(self, gameState, self.index)
            else:
                action, target = myProblem.minDistance(self.curPos, self.midLine, self.walls, self)
            mode = (action, ("backToMid", target))
            print(self.index, mode)
        return mode

    def getDistanceToOurMid(self, pos):
        minDis = 999999
        minPos = None
        for i in self.midLine:
            dis = self.distancer.getDistance(pos, i)
            if dis < minDis:
                minDis = dis
                minPos = pos
        return minPos, minDis

    def inDanger(self, pos):
        inFiveSteps = False
        for i in self.enemyPos:
            if not i is None:
                if i[0] in self.enemyRegionX or i in self.midLine:
                    inFiveSteps = inFiveSteps or self.distancer.getDistance(pos, i) <= 5
        beSeen = self.curInsightOfEnemy(pos, self.enemyPos)
        return beSeen and inFiveSteps and (pos[0] in self.enemyRegionX or (pos in self.midLine))

    # def whenBackToMid(self):
    #

    def inOurRegion(self, gameState):
        mode = ()
        if self.curPos[0] in self.ourRegionX:
            mode = self.beenScared(gameState)
        if mode != ():
            return mode
        elif (self.curPos[0] in self.ourRegionX) and mode == ():
            print("^^^^^^^^^^^^^^^^ in our region ^^^^^^^^^^^^^^^^^")
            if self.enemyAllHome:
                if self.canAttact:
                    if (self.enemyDied[self.enemyIndex[0]] or self.enemyDied[self.enemyIndex[1]]) or (self.index == 0 or self.index == 1):
                        if (not self.curPos in self.midLine):
                            midPos = self.getMiddleLinePositionToAttack(self.enemyPositionsToDefend)
                            action,target = myProblem.minDistance(self.curPos,[midPos],self.walls,self)
                            if debug:
                                self.debugDraw(midPos,[1,0,0])
                            mode = (action,("eatFood",target))
                            return mode
                        else:
                            return ()
                    else:
                        # action, target = self.defence()
                        # mode = (action, ("defence", target))
                        mode = self.intercept(gameState)
                        enemyNeedToTrace = self.getEnemyNeedToTrace()
                        enemyPos = self.enemyPositionsToDefend[enemyNeedToTrace]
                        if self.shouldITrace(enemyPos,gameState):
                            if mode == ():
                                mode = self.trace(enemyNeedToTrace)
                        else:
                            action, target = self.defence()
                            mode = (action, ("defence", target))
                else:
                    # action, target = self.defence()
                    # mode = (action, ("defence", target))
                    enemyNeedToTrace = self.getEnemyNeedToTrace()
                    enemyPos = self.enemyPositionsToDefend[enemyNeedToTrace]
                    mode = self.intercept(gameState)
                    if mode == ():
                        action, target = self.defence()
                        mode = (action, ("defence", target))
            elif self.getEnemyOneAtHome():
                enemyNeedToTrace = self.getEnemyNeedToTrace()
                enemyPos = self.enemyPositionsToDefend[enemyNeedToTrace]
                if not self.canAttact:
                     #改追击的目标，不能用离豆子最近
                    mode = self.interceptToMid(gameState)
                    if mode == ():
                        mode = self.trace(enemyNeedToTrace)
                else:
                    if self.shouldITrace(enemyPos,gameState):
                        mode = self.interceptToMid(gameState)
                        if mode == ():
                            mode = self.trace(enemyNeedToTrace)
                    else:
                        return ()
            elif self.getEnemyAllAtOur():
                enemyNeedToTrace = self.getEnemyNeedToTrace()
                enemyPos = self.enemyPositionsToDefend[enemyNeedToTrace]
                if not self.canAttact:
                     #改追击的目标，不能用离豆子最近
                    mode = self.interceptToMid(gameState)
                    if mode == ():
                        mode = self.trace(enemyNeedToTrace)
                else:
                    if self.shouldITrace(enemyPos,gameState):
                        mode = self.interceptToMid(gameState)
                        if mode == ():
                            mode = self.trace(enemyNeedToTrace)
                    else:
                        return ()
        else:
            return ()
        return mode

    def getNewWalls(self,newBlocking):
        walls = copy.deepcopy(self.walls)
        for pos in newBlocking:
            walls[pos[0]][pos[1]] = True
            # self.debugDraw(pos,[1,0,0])
        return walls


    def beenScared(self,gameState):
        mode = ()
        if self.ownScaredTimer>0:
            # print(self.foodGrid.asList())
            if self.canAttact:
                mode = self.attack(gameState)
            else:
                print("**********")
                enemy = self.getEnemyNeedToTrace()
                enemyPosDic = {}
                for i in self.enemyIndex:
                    enemyPosDic[i] = gameState.getAgentPosition(i)
                if not enemyPosDic[enemy] is None:
                    (x,y) = enemyPosDic[enemy]
                else:
                    (x,y) = self.enemyPositionsToDefend[enemy]
                blocks = []
                for direction in [Directions.NORTH, Directions.SOUTH, Directions.WEST,Directions.EAST,Directions.STOP]:  # , Directions.EAST]:
                    dx, dy = Actions.directionToVector(direction)
                    nextx, nexty = int(x + dx), int(y + dy)
                    blocks.append((nextx,nexty))
                newWalls = self.getNewWalls(blocks)
                for i in blocks:
                    if debug:
                        self.debugDraw(i,[0.5,0.5,0.5])
                action,target = myProblem.minDistance(self.curPos,[self.enemyPositionsToDefend[enemy]],newWalls,self)
                mode = (action,("trace",target))
        return mode

    # def goBackToDefence(self, gameState):
    #
    #     if self.
    #     if self.getEnemyOneAtHome():
    #
    #     if self.foodGrid.asList() == [] or len(self.getFood(gameState).asList) <= 2:
    #         enemyNeedToTrace = self.getEnemyNeedToTrace()
    #         enemyPos = self.enemyPositionsToDefend[enemyNeedToTrace]
    #         mode = self.trace(enemyNeedToTrace)



    def helpTeammate(self,gameState):
        mode = ()
        # print("number of capsule",self.capsules)
        if agentMod[self.allienIndex] != []:
            if (agentMod[self.allienIndex][0] == "needHelp") and (len(self.capsules) > 0):
                problem = myProblem.EatCapsuleProblem(gameState, self)
                actions2, target2 = self.aStarSearch(problem, gameState, problem.eatCapsuleHeuristic, 0.2)
                hasCapsule = self.legalAction(actions2)
                if hasCapsule:
                    mode = (actions2[0],("eatCapsule",target2))
        return mode

    def shouldITrace(self, enemyPos,gameState):
        manyDeadEnd = True
        # print('@@@@@@@@@@@@@@@',enemyPos)
        if manyDeadEnd:
            distToFood = min(map(lambda a: self.distancer.getDistance(a, self.curPos), self.getFoodYouAreDefending(gameState).asList()))
            enemyToFood = min(map(lambda a: self.distancer.getDistance(a, enemyPos), self.getFoodYouAreDefending(gameState).asList()))
            if distToFood > enemyToFood:
                return False
        if (self.curPos[0] in self.ourRegionX) and (self.teammatePos[0] in self.ourRegionX):
            if self.distancer.getDistance(enemyPos, self.curPos) > self.distancer.getDistance(enemyPos, self.teammatePos):
                return False
            else:
                return True
        else:
            return True

    # def wining(self):

    def defence(self):
        minDist = 999999
        closestMid = random.choice(self.midLine)
        for pos in self.midLine:
            for index in self.enemyIndex:
                dist = self.distancer.getDistance(self.enemyPositionsToDefend[index],pos)
                if dist < minDist:
                    minDist = dist
                    closestMid = pos
        action,target = myProblem.minDistance(self.curPos, [closestMid], self.walls, self)
        if debug:
            self.debugDraw(target,[0.8,0.4,0.2])
        return action,target

    def trace(self, enemyIndex):
        enemyPos = self.enemyPositionsToDefend[enemyIndex]
        action, target = myProblem.minDistance(self.curPos, [enemyPos], self.walls, self)
        mode = action, ("traceEnemy", target)
        return mode

    def aStarSearch(self, problem, gameState, heuristic, timeLimit):
        start = time.clock()
        """Search the node that has the lowest combined cost and heuristic first."""
        # init
        visited = set()
        best_g = dict()
        """state: [position, foodGrid, food]"""
        """state, action list, cost value g"""
        start_node = (problem.getStartState(gameState, self.foodGrid), [], 0)
        frontier = util.PriorityQueue()
        priority = heuristic(problem.getStartState(gameState, self.foodGrid))  # f = h + g(start is 0)
        frontier.push(start_node, priority)

        while not frontier.isEmpty():
            elapsed = (time.clock() - start)
            if elapsed >= timeLimit:
                if debug:
                    print("Time used:", elapsed)
                    print("time exceed")
                return "TIMEEXCEED", None  # for eatOneSafeFood time exceed
            else:
                current_node = frontier.pop()
                if current_node[0] in best_g.keys():  # reopen
                    if best_g[current_node[0]] > current_node[2]:
                        best_g[current_node[0]] = current_node[2]
                        for successor in problem.getSuccessors(current_node[0]):
                            cost_g = current_node[2] + successor[2]
                            priority = cost_g + heuristic(successor[0])
                            path = current_node[1] + [successor[1]]
                            frontier.push((successor[0], path, cost_g), priority)
                elif current_node[0] not in visited:
                    best_g[current_node[0]] = current_node[2]
                    visited.add(current_node[0])
                    if problem.isGoalState(gameState, current_node[0]):
                        return current_node[1], current_node[0][0]
                    else:
                        for successor in problem.getSuccessors(current_node[0]):
                            cost_g = current_node[2] + successor[2]
                            priority = cost_g + heuristic(successor[0])
                            path = current_node[1] + [successor[1]]
                            frontier.push((successor[0], path, cost_g), priority)
        return None, None
