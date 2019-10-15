# Pacman Contest

![Python Version](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue)

# Table of Contents

* [Team Name](#team-name)
* [Team Members](#team-members)
* [Challenges and Design Decisions](#challenges-and-design-decisions)
* [Approaches](#approaches)
* [Possible Improvements](#possible-improvements)
* [Analysis](#analysis)

---

## Team Name

```
kdbnb
```

## Team Members

```
Xu Wang - xuwang2@student.unimelb.edu.au - 979895
Jun Wang - jun2@student.unimelb.edu.au - 1001457
Li Shen - shels@student.unimelb.edu.au - 1001920
```

## Challenges and Design Decisions

Before going to decide which technique to use in this proeject, it is important to identify the challenges in this project. Therefore, in this pages, we would firstly identifying the challenges based on the game restrictions and then carefully analysis different techniques and finally make our decision about which techniques are more suitable for this contest.

### Challenges

There are several restrictions in this project:

* Each step should be calculated within one second, so we need to find techniques that can calculate each step within 1 sec and the output should be relatively rational.
* The tournament would run in random maps, so our pacman should be able to play in different maps.
* We only have 15 seconds to do initial set-up before game start, so it is important to make use of the 15 seconds to retrieve more information about the map before game start.
* We only have 4 weeks to do this project, so the training time of agents should be less than three weeks.

### Design Decisions

<!-- Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc semper pretium eros, sit amet ornare dolor finibus non. Pellentesque at mi ac sapien euismod lobortis eu volutpat magna. Pellentesque vulputate eget ex sit amet efficitur. Mauris id finibus elit, in fermentum felis. Etiam ex est, vulputate eu tincidunt at, finibus sed sapien. Nulla consequat, nunc nec ultrices auctor, tortor felis porttitor diam, eget volutpat arcu enim nec enim. Sed laoreet nulla vitae nunc tristique accumsan. Duis metus erat, vulputate vel sem eget, finibus cursus sem. Nunc vel porttitor ligula, eget sollicitudin est. Donec porta urna eros, et elementum ligula blandit in. -->


## Approaches

This section introduces the AI methods that we have tried in this project.

<!-- Sed nec felis dapibus, porttitor quam vel, imperdiet purus. Curabitur pellentesque interdum vehicula. Nullam vestibulum tristique dui, a ultrices velit ultrices id. Quisque nec tortor consequat erat fermentum pulvinar. Quisque vestibulum lorem massa, a placerat felis interdum vel. Nulla lacinia sed ex quis elementum. Aliquam consequat, purus nec venenatis efficitur, massa elit facilisis neque, in mollis metus libero sed metus. Nunc ut consectetur felis. Ut volutpat eu odio vel placerat. Nunc in est orci. Duis purus enim, eleifend sollicitudin facilisis sed, consequat viverra massa. Fusce elementum quis enim vel tincidunt. Sed metus ante, pellentesque nec venenatis et, ultricies vel leo. Proin sodales rhoncus pharetra. -->


## Possible Improvements

<!-- Praesent finibus, justo sed commodo lacinia, lacus sem lacinia nisi, id egestas purus ligula et ante. Sed non lacinia leo. Praesent pulvinar sit amet ante non fermentum. Proin in odio nec ante molestie tempor. Mauris interdum odio justo, quis rhoncus mauris vestibulum ac. Vivamus vitae est nec nisl pellentesque ullamcorper a eu eros. Interdum et malesuada fames ac ante ipsum primis in faucibus. Maecenas eu dictum dolor. Curabitur pellentesque, urna at lacinia suscipit, magna purus semper augue, at tristique tellus eros vitae ex. -->

## Analysis

<!-- Cras eget ligula at massa vehicula sollicitudin. Aliquam vitae vulputate dui, ut mattis purus. Quisque tempus sapien ut nisi vehicula sodales. Curabitur pretium ligula et placerat faucibus. Quisque sagittis mi ac lobortis dignissim. Curabitur fringilla luctus feugiat. Suspendisse a felis mi. Proin nec tortor mattis, porttitor velit sed, consectetur libero. Quisque id fringilla ante, feugiat varius diam. Phasellus tempus sodales ligula, in aliquet arcu finibus at. Pellentesque efficitur porttitor metus ac ornare. Curabitur at pulvinar ex. Proin sit amet sapien posuere, facilisis sapien ac, tempus orci. -->

|     | Computation Time (In-Game) | Training Time | Implementation Difficulty |
| --- | --- | --- | --- |
| Heuristic search | short | - | Easy |
| Monte Carlo tree search | long (need long computation time for tree search) | 