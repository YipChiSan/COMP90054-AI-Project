# Pacman Contest

![Python Version](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue)

Heuristic Search vs. baselineTeam
```
python capture.py -r myTeam -b baselineTeam -l RANDOM
```

Upper Confidence Trees vs. baselineTeam
```
python capture.py -r MCTsAgent -b baselineTeam -l RANDOM
```

# Youtube presentation
Please click [HERE](https://www.youtube.com/watch?v=UWmcxLgjz84) to watch the video

# Table of Contents

* [Team Name](#team-name)  
* [Team Members](#team-members)  
* [Introduction](#introduction)  
* [Project Analysis and Design Decisions](#project-analysis-and-design-decisions)  
* [Approaches](#approaches)  
    * [Support Functions](#support-functions)  
        * [Blind Search](#blind-search)
        * [Goal Recognition Techniques](#goal-recognition-techniques)
        * [Cluster](#cluster)
    * [Main Techniques](#main-techniques)  
        * [Heuristic Search (A star)](#heuristic-search-a-star)
        * [Upper Confidence Trees](#upper-confidence-trees)
        * [Q-Approximate Learning](#q-approximate-learning)
* [Experimental Result](#experimental-result)
* [Possible Improvements](#possible-improvements)  

---
<!-- ---------------------------------------------------------- -->
# Team Name

```
kdbnb
```
<!-- ---------------------------------------------------------- -->

# Team Members

```
Xu Wang - xuwang2@student.unimelb.edu.au - 979895
Jun Wang - jun2@student.unimelb.edu.au - 1001457
Li Shen - shels@student.unimelb.edu.au - 1001920
```
<!-- ---------------------------------------------------------- -->

# Introduction
In this project, we need to implement Pacman-agents to play competition Pacman tournament. About 200 teams participate in 4 groups and use their agents to compete.

<!-- ---------------------------------------------------------- -->

# Project Analysis and Design Decisions
By analyzing the rules, we summarize these points, which may affect our choice of technology:

* **Multi-agents and Multi-functions**: In the game, each team can control two Pacman-agent in a game, so this is a multi-agent problem. Also, a team needs to balance attack and defence. Thus, our agents need to have two main modules. One is responsible for attacking, eating foods and avoiding the enemy's ghost; another module is responsible for defence and capturing enemy's Pacman. These two modules can let two agents take charge of one, or an agent can switch between attack and defence.

* **Generalization**: The map of each game selects from 10000 random maps, it's impossible to model and train with a specific map. Also, it's an adversarial game, and we need to compete with different teams. The tactics of the different team are different, so there is no clear rule in the enemy's movements. Therefore, our agents need to have a strong generalization ability to compete with different enemies on different maps.
 
 * **Time limit**: There is a 15 second preparation time at the beginning of the game. Therefore, for some models that need to map specific training, it needs to be completed in 15 seconds. Each agent has only one second of action decision per round, so the agent needs the ability to make decisions in a short time. Furthermore, we need to implement 2 methods in about 3 weeks.

## Design Decisions

From project analysis above, we compared some AI methods below:

|     | Computation Time (In-Game) | Training Time | Ability of Generalization | Implementation Difficulty |
| --- | --- | --- | --- | --- |
| Heuristic search | short | - | - | easy |
| Model-based MDP | long - need long computation time to get the best policy for entire map | need more than one hour for each map | impossible to convert policy between maps | medium |
| Model-free MDP | long (need long computation time for tree search) | - | high | medium |
| Q-learning | short | long | low | easy |
| Q-approximate learning | short | medium | high | medium - need to carefully select features |
| Q-learning with neural network | short | extremely long, might take monthes | high if well trained | hard |

<!-- 加一些分析 -->

<!-- ---------------------------------------------------------- -->

# Approaches

This section introduces the AI methods that we have tried in this project.

## Support Functions

### Blind Search

In each game, every team has 15 seconds to initialization, so used this time to calculate the dead-end in the map. First, we calculate the degree (number of neighbours not wall) of each grid and mark the grid with only one neighbour as a dead-end. Then start with one dead-end grid, used Deep-first-search (DFS) to find the depth of the dead end. The result is shown below.

![wiki-deadEnd](uploads/fba31aaf1074fd056abf3ba1089ef512/wiki-deadEnd.png)

### Goal Recognition Techniques

The game is imperfect information. We can't know the exact location of the enemy's agents unless we are close to them. But the game still provides a noisy distance for enemy's agents. Noisy distance gives an imprecise position. It is a random value in the range (- 6, + 6) Manhattan distance to real distance of the enemy. And each agent can only take one step in each round. Thus, we got the noisy distance of enemy agents through our two agents, and then use noisy distance and steps information to calculate the approximate positions of the enemy's agent. Based on the position information obtained, we calculated the most likely intentions and target position of enemy agents. This ensures that even the enemies are outside of our version, we can still make a decision based on the estimated value.

![image](uploads/08a6da4cc00f3684c407e26a9b18715b/image.png)


### Cluster

In the game, we need to control two agents, so it’s a multi-agent problem. So, we need to balance the behaviours of the two agents, especially when both agents attack. If they all catch the same food, it will significantly reduce the efficiency and lead to the failure of the game. Therefore, we clustered the food on distances of food. If an agent wants to eat one food, the other agent will calculate other food in the same cluster as the target, to choose other goals. This way can effectively avoid the conflict between the two agents.

![image](uploads/54732a36f7ea2f24d1282793fd759bad/image.png)

## Main Techniques

### Heuristic Search (A star)
A star is a typical heuristic search algorithm for classical planning. When the heuristic function of A star is admissible, the result will be optimal.


<!-- 难点 -->
In pacman games, we decompose the main process and problem into multiple subproblems and conquer them one by one. The output of A star for solving each subproblem will be a list of actions to goal state and a target position corresponding to the problem input. Since there is a time limit of one second for calculating every step of actions for our agents, and most of the game maps are in size of 16 * 32, which is not small, a good heuristic function can be of great importance. Therefore, all we need is to define and optimize corresponding goal state and heuristic function. 
These problems can be classified and used in two main strategies, attack and defend. 

<!-- 实现 -->
#### A star Attack
1.   Eat One Safe Food Problem: 
Find a path for own agent to nearest food that can be eaten safely if any exists
2.   Eat Capsule Problem: 
Find a path for own agent to nearest capsule if any exists
3.   Escape Problem: 
Find a path for own agent back to our nearest middle line point if any exists
4.   Implementation: 
Expanded states from enemy positions should be expanded every time A star get successor states, and A star can achieve the effect of simulating the enemy's following our agent. Besides, since the real maze distances are calculated and stored before the game starts, the algorithm just applies the distances as heuristics as it can truly reflect the distance to target.

![1](uploads/b32c0746d0509edca8e78951154cfb92/1.png)

#### A star Defend
1.   Enemy Eat Closest Food Problem: path for enemy agent to nearest food from their current position
2.   Enemy Go Back To Closest Middle Line: path for enemy agent to nearest enemy middle line point after eating food
3.   Implementation:
Paths calculated here are used for simulating enemy's actions without being affected by our agents. Our agents can then intercept their path by reaching toward the closest position in the path and from their current position.

![image](uploads/74f3ce32c53ebf6e7fbaa150f2c43919/image.png)
   
<!-- 结果 & A*分析优缺点 -->
#### Analysis 
Since multiple subproblems are separated in this pacman game, using A star conforms to the attribute that calculate fast.
Pros: A star can easily find optimal path for problems, and is quite fast compared to other techniques.
Cons: A star requires us to plan ahead with domain knowledge.



### Upper Confidence Trees
UCT is a model-free MDP algorithm. It used ucb to select the node to expansion for  mento carol tree search. Therefore, compared with UCT, it performs better in the balance of exploration and exploration. It's model-free algorithm which means the UCT agents doesn't need the transition probability distribution. The model tries to simulate and then evaluates the action based on the reward returned by the environment. 

#### Exploration and exploitation 
The most important thing of UCT is to use UCB for node selection, so that exploration and exploration can be well balanced. Thus as not to fall into the local optimal solution. In UCB, we chose 1 / sqrt (2) as the value of C as the parameter of exploration.

#### Reward
The reward is the most important factor for a model-free algorithm. According to the interaction with the environment, the UCT agent gets a reward to decide the next action. For Pacman games, the reward of the game is very sparse, so it becomes a challenge. For the attacking agent, there is not much food agent can eat on the map, and they are all in the enemy half. In the initial point, it may take more than 30 actions to eat the first food, so it is difficult for UCT agent to make a decision. To solve this problem, we add reward shaping. Here are our rewards:

1. Distance to mid: (100 - maze distance) * 0.1
2. Distance to food: (100 - maze distance) * 0.001
3. Food carries: number of food carry * 0.3
4. Score: the score of the game

Also, here is the reward for defence:
1. Distance to enemy Pacman: (100 - maze distance) * 0.1
2. Number of defending foods: (100 - food number) * 0.1
3. Ate enemy: 1

We found the reward shaping works well. With the addition of reward shaping, agents can move smoothly towards food even at our half.

#### Analysis
UCT is a model-free algorithm, which does not need planning algorithm like a * and uses a lot of experience to implement. It has a good generalization ability and can interact with the environment by itself, so it only needs less domain knowledge. The disadvantage of UCT is that it can not get good results for the sparse environment of reward. Secondly, each step of the decision needs a lot of simulation, and the number of simulation directly determines the quality of the decision. For Pacman, we only have one second of computing time each time. So we can only limit the simulation time to 0.9 seconds, which leads to some times agent cannot make the best choice.



### Q-Approximate Learning
In the process of trying to reinforcement learning technology, considering the generalization ability, we use approximate Q-learning. Compared with q-learning, approximate Q-learning can estimate the Q value of unknown states, which significantly improves the generalization ability.
We start with a simple task. First, we trained the model to eat foods, and then we trained the agent to bring foods back after eating food. According to the results, we made a preliminary evaluation of approximate Q-learning.

We start with a simple task. First, we trained the model to eat foods, and then we trained the agent to bring foods back after eating food. According to the results, we made a preliminary evaluation of approximate Q-learning.

#### Feature extraction and feature transformation
The most crucial thing about approximate Q-learning is feature extraction.

Approximate Q-learning uses an approximate function to predict Q-value: According to the current game, state to extract features, then calculate the Q value through weights. 

Unlike Q-learning to record all the Q-values corresponding to state and action, Approximate Q-learning can give a good estimate Q-value for the state and action that has not been seen before.

Therefore, the feature is the key to approximate function. Feature extraction needs to depend on domain knowledge and experiments. These are the combinations of the features we extracted for two different tasks.

The first task: eat foods
1.   distance to ghost
2.   distance to foods
3.   number of remain foods
 
The Second task: bring back foods
1.   distance to ghost
2.   distance to foods
3.   distance to mid
4.   distance to mid when carrying foods
5.   number of remain foods

***distance to mid when carry foods*** is a combination of features after feature transformation. Because we used the linear function, agent can't learn the relationship between features, so we do some feature transformation based on our experience.

#### Rewards
Rewards are the key factor of most learning approaches. For this project, the obvious reward is the score. But this reward is very sparsed,  we need to do the reward shaping and also give a negative reward for death. Here are the rewards for two tasks.

For eating food task
1.   Eat one food: +1
2.   Death: -1
 
For bringing back food task:
1.   Eat one food: +1
2.   Death: -1
3.   Bring back one food: +2
 
#### Training:
Because we are training for simpler subproblems, so first we try to test on the map of mediumCapture. There is an amount of food on this map, which can let the agent learn how to eat food and how to bring it back quickly.
We run the game and extract the feature from the game state, and calculate Q-value and update the q-value based on the reward from the game state. Here is the update function. We run the game and extract the feature from the game state, and calculate Q-value and update the q-value based on the reward from the game state. Here is the update function.

#### Analysis
After trying two different feature combinations, we found the defect of approximate Q-learning. Because we used the linear combination, the model can't learn the relationships of features. For example, when Pacman brings foods back to the middle line, the agent will get rewards. But because of the linear function, the weight of the distance to boundary and carry food number will be adjusted. After a certain amount of training, it will miscalculate the weight of the feature distance to boundary, and stay at the boundary. These problems can be solved by better feature transformation, or by using nonlinear approve function, such as the neural network, which is the deep Q network (DQN). But because of time, we didn't try any further.

# Experimental Result

We competed and compared our three agents to choose which agent should we use for the final contest. The A Star Agent uses support functions described above and A Star Search Algorithm with a decision tree for action choice. The UCT Agent calculates scores based on food, enemy, middle line, etc. and chooses action within 1 second. Results are shown below:


| Own vs Enemy | Average Score | Average Time | Win Rate | Win | Tie | Lose | Average Dead Times | Average Enemy Dead Times |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A star vs Baseline| 25.80 | 59.68s | 95% | 19 | 0 | 1 | 0.14 | 2.65 |
| UCT vs Baseline| 14.40 | 303.75s | 85% | 17 | 0 | 3 | 0.30 | 0.75 |
| A star vs UCT | 13.13 | 282.10s | 90% | 18 | 0 | 2 | 0.45 | 1.55 |


From the above tables, we can see that both A Star Agent and UCT Agent can defeat baselineTeam well. However, A Star Agent is more consistent in different maps and can eat faster than UCT Agent because of the support functions provided, not only embodied in the win rate but also shown in the average scores.

Besides, UCT does show good ability to escape from enemy, and we found it has a good ability to chase enemy but may not have a good policy to eliminate them. Compared with UCT, A Star has an overall higher efficiency of avoiding enemy and eating enemy because of the enemy position prediction and intercept support function above.

Furthermore, with one second time-limited, model-free MDP cannot simulate too deep to make the most suitable action.

In conclusion, we decided to use A Star agent for our final contest agent.

<!-- ---------------------------------------------------------- -->
# Possible Improvements
1. A star: In the attack strategy of Astar, we only search for the closest food, because searching all food may take a long time. However, based on the food cluster, we can try to use A star to find the optimal path to finish eating a food cluster. This may improve our attack efficiency.
2. UCT: Due to time limit, UCT does not have a real food cluster and enemy position recognition. In the agent of a star, we see the performance of these support functions. If we can add these auxiliary functions to the UCT, it may be helpful. Secondly, we choose reward shaping to solve the problem of reward spark. Another way to improve is to use the heuristic function instead of random choose policy when simulating. 
3.Q-learning: We tried approximate Q-learning, but we didn’t achieve good performance, and it was not introduced in this presentation because of the time limit. But we found the model can’t learn the relationship between features if we used the linear approximate function. Thus, we can try feature transformation or use a non-linear function, such as Deep Q network if we have more time.
