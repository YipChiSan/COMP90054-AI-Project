def searchDeadEnd(map):
    # 0: Walls
    # 1: Available movements
    # 2: RedFood
    # 3: RedCapsule
    # 4: BlueFood
    # 5: BlueCapsule
    #
    # blueCapsule = {}
    # redCapsule = {}
    deadEnd = []
    for i in range(1,len(map)-1):
        for j in range(1,len(map[i])-1):
            if map[i][j] != 0:
                if moveNum(map,i,j,deadEnd) == 1:
                    deadEnd = moveEnd(map,i,j,deadEnd)
    # for i in range(1,len(map)-1):
    #     for j in range(1,len(map[i])-1):
    #         if map[i,j] == 3:
    #             blueCapsule[(i,j)] = capsuleMove(map,i,j,deadEnd,[])
    #         if map[i,j] == 5:
    #             redCapsule[(i,j)] = capsuleMove(map,i,j,deadEnd,[])
    for i in range(0,len(map)):
        for j in range(0,len(map[i])):
            if map[i][j] == 0:
                print("%",end='')
            else:
                if (i,j) in deadEnd:
                    print("*",end = "")
                else:
                    print("#",end = "")
        print()
    return deadEnd
def capsuleMove(map,x,y,deadEnd,caList):
    if (x,y) in deadEnd:
        caList.append((x,y))
        moves = [(-1,0),(+1,0),(0,-1),(0,+1)]
        for i in moves:
            if (x+i[0],y+i[1]) in deadEnd:
                if moveNum(map,x,y,deadEnd) >0:
                    caList = capsuleMove(map,x,y,deadEnd,caList)
    return caList


def moveNum(map,x,y,deadEnd):
    numDead = ((x-1,y) in deadEnd) + ((x+1,y) in deadEnd) + ((x,y-1) in deadEnd)+((x,y+1) in deadEnd)
    return (map[x-1][y] != 0) + (map[x+1][y] != 0 ) + (map[x][y-1] !=0) + (map[x][y+1] !=0) - numDead

def moveEnd(map,x,y,deadEnd):
    deadEnd.append((x,y))
    moves = [(-1,0),(+1,0),(0,-1),(0,+1)]
    for i in moves:
        if map[x+i[0]][y+i[1]] != 0:
            if moveNum(map,x+i[0],y+i[1],deadEnd) == 1:
                # deadEnd.append((x+i[0],y+i[1]))
                deadEnd = moveEnd(map,x+i[0],y+i[1],deadEnd)
    return deadEnd
