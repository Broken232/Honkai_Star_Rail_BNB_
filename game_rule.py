import sys
import pygame as py
import time
import random

def break_box(Map,break_pos,player):
    i=random.randint(1,100)
    if player.player_char == 'fx' and player.skill==1:              #fx技能
        i=random.randint(1,23)
        player.skill=0
    c=1
    if i<4:
        c=8                         #棱镜，拥有时表示有技能
    elif i<14:
        c=6                         #福灵胶，炸弹上限+1
    elif i<24:
        c=7                         #饮料，炸弹范围+1
    Map[break_pos[0]][break_pos[1]]=c
    return Map,player

def move_rule(Map,player_pos,move,flag_yl):#0是墙，1是路，2是箱,3是炸,4是火，5是音符，6是福灵胶，7是饮料，8是棱镜，9是死亡
    want_pos=[0,0]
    want_pos[0]=player_pos[0]+move[0]
    want_pos[1]=player_pos[1]+move[1]
    if (Map[want_pos[0]][want_pos[1]]==0 or Map[want_pos[0]][want_pos[1]]==2 or
            Map[want_pos[0]][want_pos[1]]==3 or Map[want_pos[0]][want_pos[1]]==5) :
        if flag_yl==False:
            return Map,player_pos,False
        else :
            Map[want_pos[0]][want_pos[1]]=1
            return Map,want_pos,False
    else:
        return Map,want_pos,flag_yl

def eat(map,player): # 需要知道吃了什么，然后返回吃完后角色的面板
    lei=map[player.player_pos[0]][player.player_pos[1]]
    if lei == 6:
        player.player_boom_max += 1
        map[player.player_pos[0]][player.player_pos[1]]=1
    elif lei == 7:
        player.player_boom_range += 1
        map[player.player_pos[0]][player.player_pos[1]]=1
    elif lei == 8:
        player.skill = 1
        map[player.player_pos[0]][player.player_pos[1]]=1
    return map,player