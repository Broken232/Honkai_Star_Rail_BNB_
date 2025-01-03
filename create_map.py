import random
N=14
def duicheng_xy(map,x,y,lei):
    map[x][y]=lei;map[N-x][y]=lei;map[x][N-y]=lei;map[N-x][N-y]=lei
    return map

def duicheng_x(map,x,y,lei):
    map[x][y]=lei;map[x][N-y]=lei
    return map

def duicheng_xyz(map,x,y,lei):
    map[x][y]=lei;map[N-x][y]=lei;map[x][N-y]=lei;map[N-x][N-y]=lei;map[y][x]=lei;map[y][N-x]=lei;map[N-y][x]=lei;map[N-y][N-x]=lei
    return map



def chose_map(mod):
    if mod=='map1':
        return creat_map_0()
    elif mod=='map2':
        return creat_map_1()
    elif mod=='map3':
        return creat_map_2()
    elif mod=='map4':
        return creat_map_3()




def creat_map_0():#0是墙，1是路，2是箱
    map=[[0 for _ in range(N+1)] for _ in range(N+1)]
    for i in range(1,N):
        for j in range(1,N):
            map[i][j]=1
    for i in range(3,8):
        map = duicheng_xy(map, i, 3, (i - 1) % 2 * 2)
        map = duicheng_xy(map, i, 4, (i - 1) % 2 * 2)
        map = duicheng_xy(map, i, 5, (i - 1) % 2 * 2)
    for i in range (3,8):
        map = duicheng_xy(map, i, 7, i % 2 * 2)

    map = duicheng_xy(map,2,6,0)
    map = duicheng_xy(map,2,2,2)

    return map

def creat_map_1():#0是墙，1是路，2是箱
    map=[[0 for _ in range(N+1)] for _ in range(N+1)]
    for i in range(1,N):
        for j in range(1,N):
            map[i][j]=1
    for i in range(4,11):
        for j in range(4, 11):
            map[i][j] = 2
    map = duicheng_x(map, 5, 7, 0)
    map = duicheng_x(map, 4, 6, 0)
    map = duicheng_x(map, 4, 5, 0)
    map = duicheng_x(map, 5, 4, 0)
    map = duicheng_x(map, 6, 4, 0)
    map = duicheng_x(map, 7, 4, 0)
    map = duicheng_x(map, 8, 5, 0)
    map = duicheng_x(map, 9, 6, 0)
    map = duicheng_x(map, 10, 7, 0)
    map = duicheng_x(map, 4, 4, 1)
    map = duicheng_x(map, 8, 4, 1)
    map = duicheng_x(map, 9, 5, 1)
    map = duicheng_x(map, 10, 6, 1)
    map = duicheng_x(map, 4, 7, 1)
    map = duicheng_xyz(map, 2, 2, 0)
    map = duicheng_xyz(map, 2, 3, 0)
    map = duicheng_xyz(map, 1, 3, 2)
    map = duicheng_xyz(map, 1, 4, 2)
    map = duicheng_xyz(map, 2, 4, 2)

    return map

def creat_map_2():  # 0是墙，1是路，2是箱
    map = [[0 for _ in range(N+1)] for _ in range(N+1)]
    for i in range(1, N):
        for j in range(1, N):
            map[i][j] = 1

    # 添加箱子和墙的特定布局
    for i in range(2, 6):
        map = duicheng_xy(map, i, 2, 2)
        map = duicheng_xy(map, i, 3, 2)
        map = duicheng_xy(map, i, 4, 2)
        map = duicheng_xy(map, i, 5, 2)

    map = duicheng_xyz(map, 8, 8, 0)
    map = duicheng_xyz(map, 9, 8, 0)
    map = duicheng_xyz(map, 10, 8, 0)
    map = duicheng_xyz(map, 11, 8, 0)

    map = duicheng_x(map, 8, 2, 1)
    map = duicheng_x(map, 8, 3, 1)
    map = duicheng_x(map, 8, 4, 1)
    map = duicheng_x(map, 8, 5, 1)

    return map

def creat_map_3():
    map = [[0 for _ in range(N + 1)] for _ in range(N + 1)]
    for i in range(1, N):
        for j in range(1, N):
            map[i][j] = 1

    for i in range(1,N):
        for j in range(1,N):
            if i==1 or i==N-1 or j==1 or j==N-1:
                map[i][j] = 1
            elif i==j or i==j-1 or i==j+1:
                map[i][j] = 1
            elif i+j==15 or i+j==14 or i+j==13:
                map[i][j] = 1
            else:
                map[i][j] = 2
    map=duicheng_xy(map,2,4,0)
    map=duicheng_xy(map,2,5,0)
    map=duicheng_xy(map,2,6,0)
    map=duicheng_xy(map,3,5,0)
    map=duicheng_xy(map,4,6,0)
    map = duicheng_xy(map, 4, 2, 0)
    map = duicheng_xy(map, 5, 2, 0)
    map = duicheng_xy(map, 6, 2, 0)
    map = duicheng_xy(map, 5, 3, 0)
    map = duicheng_xy(map, 6, 4, 0)
    map[1][13]=2
    map[13][1]=2
    return map
