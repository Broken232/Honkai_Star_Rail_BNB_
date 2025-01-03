import pygame as py
import sys
import create_map
import game_rule
import time
from PIL import Image
from PIL import ImageSequence
import random

#初始化pygame
py.init()

#设置屏幕大小
N=14
screen_width = 1000
screen_height = 750
screen = py.display.set_mode((screen_width, screen_height))
py.display.set_caption("崩坏·星穹泡泡堂")

#图片初始化
images = {
    "path" : py.image.load("path.png"),
    "wall" : py.image.load("wall.png"),
    "box" : py.image.load("box.png"),
    "boom0" :py.image.load("boom_0.png"),
    "boom1" :py.image.load("boom_1.png"),
    "fire" :py.image.load("fire.png"),
    "note" :py.image.load("note.png"),
    "dead" :py.image.load("dead.png"),
    "glue" :py.image.load("福灵胶.png"),
    "juice" :py.image.load("粉红冲撞.png"),
    "prism" :py.image.load("时空棱镜.png"),
    "fx" : py.image.load("符玄.png"),
    "kfk" : py.image.load("卡芙卡.png"),
    "zgn" : py.image.load("知更鸟.png"),
    "hh" : py.image.load("花火.png"),
    "r" : py.image.load("刃.png"),
    "ly" : py.image.load("流萤.png"),
    "yl" : py.image.load("银狼.png"),
    "robot1" : py.image.load("robot1.png"),
    "robot2" : py.image.load("robot2.png"),
    "robot3" : py.image.load("robot3.png"),
    "play" : py.image.load("play_button.png"),
    "pause" : py.image.load("pause_button.png"),
    "prev" : py.image.load("prev_button.png"),
    "next" : py.image.load("next_button.png")
}
for key,image in images.items():
    images[key] = py.transform.smoothscale(image, (50,50))

map_images={
    "map1":py.image.load("map0.png"),
    "map2":py.image.load("map1.png"),
    "map3":py.image.load("map2.png"),
    "map4":py.image.load("map3.png")
}
for key,image in map_images.items():
    map_images[key] = py.transform.smoothscale(image, (200,150))

bombs = []
fires = []
players=[]
class Fire:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.placed_time = time.time()

    def update(self,map):
        draw(4, self.x, self.y)  # 绘制火焰，但无实际效果，所以不需要和map联动
        if time.time() - self.placed_time >= 0.2:
            draw(1,self.x,self.y)
            draw(map[self.x][self.y],self.x,self.y)#爆炸后会恢复成地图原样
            global fires
            fires.remove(self)

class Bomb:
    def __init__(self, x, y ,who):
        self.x = x
        self.y = y
        self.master = who
        self.placed_time = time.time()  # 记录炸弹放置的系统时间
        self.star = False

    def update(self,map,boom_range,flag_kfk):
        if self.star:
            self.star = False
            screen.blit(images["boom0"], (self.y * 50, self.x * 50))
        else :
            self.star = True
            screen.blit(images["boom1"], (self.y * 50, self.x * 50))
        if time.time() - self.placed_time >= 2 or flag_kfk==True:  # 检查是否达到2秒
            if flag_kfk:
                return self.explode(map, boom_range),False
            else:
                return self.explode(map, boom_range),flag_kfk

        return map,flag_kfk


    def explode(self,map,boom_range):
        present=[self.x,self.y]
        map=self.spread(map,boom_range,present,[0,1])
        map=self.spread(map,boom_range,present,[0,-1])
        map=self.spread(map,boom_range,present,[1,0])
        map=self.spread(map,boom_range,present,[-1,0])
        # 爆炸后移除炸弹
        map[self.x][self.y]=1
        draw(1,self.x,self.y)
        global bombs
        bombs.remove(self)
        return map

    def spread(self,map,boom_range,present,move):
        global fires
        if boom_range<abs(present[0]-self.x) or boom_range<abs(present[1]-self.y) or map[present[0]][present[1]]==0:
            return map  #超范围或者遇到墙就无事发生
        if map[present[0]][present[1]]==2:
            #遇到箱子就会将其炸掉，并且停止蔓延
            map[present[0]][present[1]]=1
            draw(1, present[0], present[1])
            #箱子炸毁会有概率爆装备
            for player in players[:]:
                if self.master==player.who:
                    map,player=game_rule.break_box(map,present,player)
            draw(map[present[0]][present[1]],present[0],present[1])
            new_fire = Fire(present[0], present[1])
            fires.append(new_fire)
            return map
        if map[present[0]][present[1]]==5:
            map[present[0]][present[1]] = 1
            draw(1, present[0], present[1])
            return map
        new_fire = Fire(present[0], present[1])
        fires.append(new_fire)

        #判断是否命中角色
        for player in players[:]:
            if player.player_pos == present:
                player.life=0

        #火焰蔓延
        map=self.spread(map,boom_range,[present[0]+move[0],present[1]+move[1]],move)
        return map

class Character:
    def __init__(self, pos,player_char ,who,boom_max=1, boom_range=1, skill=1 ,life=1):
        self.player_pos = pos                   # 玩家位置，用列表表示 [x, y]
        self.player_boom_max = boom_max         # 玩家放置炸弹数量上限
        self.player_boom_range = boom_range     # 玩家炸弹爆炸范围
        self.skill = skill                      # 玩家是否拥有技能
        self.player_char = player_char          # 玩家使用的是什么角色
        self.life = life                        # 玩家生命值
        self.who = who                          # 代表玩家是P几

def sam_skill(map):
    want_pos = [0, 0]
    want_pos[0] = random.randint(1,13)
    want_pos[1] = random.randint(1, 13)
    player=Character([0,0],'kong',10086)
    for x in range(1,14):
        for y in range(1,14):
            if abs(want_pos[0]-x)+abs(want_pos[1]-y)<=3:
                if map[x][y]==2:
                    map,player=game_rule.break_box(map,[x,y],player)
                elif map[x][y]==5:
                    map[x][y]=1
    return map,want_pos

def exit_game():
    py.quit()
    sys.exit()

def get_boom_num(who):
    a=0
    for bomb in bombs[:]:
        if bomb.master == who:
            a+=1
    return a

def get_player_num():
    a=0
    for player in players[:]:
        if player.who<=1:
            a+=1
    return a

def draw(lei,x,y):
    if lei == 0:
        screen.blit(images["wall"], (y * 50, x * 50))
    elif lei == 1:
        screen.blit(images["path"], (y * 50, x * 50))
    elif lei == 2:
        screen.blit(images["box"], (y * 50, x * 50))
    elif lei == 4:
        screen.blit(images["fire"], (y * 50, x * 50))
    elif lei == 5:
        screen.blit(images["note"], (y * 50, x * 50))
    elif lei == 6:
        screen.blit(images["glue"], (y * 50, x * 50))
    elif lei == 7:
        screen.blit(images["juice"], (y * 50, x * 50))
    elif lei == 8:
        screen.blit(images["prism"], (y * 50, x * 50))
    elif lei == 9:
        screen.blit(images["dead"], (y * 50, x * 50))

def start_screen():   #开始游戏-> 选择模式 ->选择角色-> 选择地图 ->进入游戏
    running = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                exit_game()
            elif event.type == py.MOUSEBUTTONDOWN:
                #检测鼠标点击是否在开始游戏按钮上
                if start_button.collidepoint(event.pos):
                    running=False
                    choose_game_mode()
                elif music_button.collidepoint(event.pos):
                    music_setting()
        #填充屏幕背景色
        screen.fill((255, 255, 255))
        #绘制开始游戏按钮
        py.draw.rect(screen, (255, 255, 255), start_button)
        #绘制开始游戏文本
        font = py.font.Font('SIMFANG.TTF', 50)  #设置字体
        text = font.render('开始游戏', True, (0, 0, 0))
        text_rect = text.get_rect(center=start_button.center)
        screen.blit(text, text_rect)
        text = font.render('音乐设置', True, (0, 0, 0))
        text_rect = text.get_rect(center=music_button.center)
        screen.blit(text, text_rect)
        #更新屏幕显示
        py.display.flip()
    return False

def music_setting():
    def play_song(song_index):
        py.mixer.music.load(songs[song_index])
        py.mixer.music.play()

    def prev_song(song_index,songs_length):
        song_index = (song_index-1)%songs_length
        play_song(song_index)
        return song_index

    def next_song(song_index,songs_length):
        song_index = (song_index + 1) % songs_length
        play_song(song_index)
        return song_index

    def toggle_play(flag,song_index):
        if py.mixer.music.get_busy():
            if flag:
                py.mixer.music.unpause()
                return False
            else:
                py.mixer.music.pause()
                return True
        else :
            play_song(song_index)
            return False

    screen.fill((255, 255, 255))  # 填充背景色
    song_index = 0
    songs = ["流沙.mp3","爱情转移.mp3","爱错.mp3","东风破.mp3","关于爱的定义.mp3","恭喜发财.mp3"]
    songs_length = len(songs)

    py.draw.rect(screen, (255, 255, 255), music_function_button[0])
    screen.blit(images["prev"], music_function_button[0].topleft)
    py.draw.rect(screen, (255, 255, 255), music_function_button[1])
    screen.blit(images["play"], music_function_button[1].topleft)
    py.draw.rect(screen, (255, 255, 255), music_function_button[2])
    screen.blit(images["next"], music_function_button[2].topleft)

    font = py.font.Font('SIMFANG.TTF', 30)
    py.draw.rect(screen, (255, 255, 255), confirm_button)
    text = font.render('返回', True, (0, 0, 0))
    text_rect = text.get_rect(center=confirm_button.center)
    screen.blit(text, text_rect)  # 四行代码全是按钮可视化

    running = True
    flag = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                exit_game()
            elif event.type == py.MOUSEBUTTONDOWN:
                if confirm_button.collidepoint(event.pos):                                    # 返回键
                    running = False
                elif music_function_button[0].collidepoint(event.pos):                          # 上一首
                    song_index=prev_song(song_index,songs_length)
                elif music_function_button[1].collidepoint(event.pos):                          # 播放/暂停
                    flag = toggle_play(flag,song_index)
                    if flag:
                        screen.blit(images["play"], music_function_button[1].topleft)
                    else :
                        screen.blit(images["pause"], music_function_button[1].topleft)
                elif music_function_button[2].collidepoint(event.pos):                          # 下一首
                    song_index = next_song(song_index, songs_length)

        # 更新显示
        py.display.flip()

#选择游戏模式界面函数 （双人模式或单人模式）
def choose_game_mode():
    running = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                exit_game()
            elif event.type == py.MOUSEBUTTONDOWN:
                if mode_button[0].collidepoint(event.pos):
                    player1_char, player2_char = choose_character(0)
                    map_id = choose_map()
                    game_main(player1_char, player2_char, map_id)          #本地双人模式
                    running = False
                elif mode_button[1].collidepoint(event.pos):
                    player1_char, _ = choose_character(1)
                    map_id=choose_map()
                    game_main(player1_char, _, map_id)
                    running = False

        screen.fill((255, 255, 255))
        #绘制双人游戏和联机游戏的按钮
        for i,button in enumerate(mode_button):
            py.draw.rect(screen, (255, 255, 255), button)
            font = py.font.Font('SIMFANG.TTF', 40)
            if i==0:
                text=font.render('双人游戏', True, (0, 0, 0))
            else:
                text=font.render('单人游戏', True, (0, 0, 0))
            text_rect=text.get_rect(center=button.center)
            screen.blit(text, text_rect)
        py.display.flip()

#选择角色界面函数
def choose_character(mod):
    characters=["fx","kfk","zgn","hh","r","ly","yl"]
    #角色技能
    skills = {
        "fx":"用穷观阵算破了天机：下一次打碎箱子时一定会掉落特殊道具",# OK
        "kfk":"听我说~：立即引爆场上最早释放的炸弹",# ok
        "zgn":"welcome to my ...：在原地放置音符，效果等效于箱子，但炸毁后不会有掉落物",# OK
        "hh":"因为发了太多“相互保证毁灭按钮”，太过熟练：炸弹放置上限永久提高2",# ok
        "r":"魔阴身发作：死亡后立即复活",# ok
        "ly":"启动萨姆：往地图随机地方砸落，击碎范围内所有箱子，并将自身传送到相应位置",
        "yl":"进入百分百弱点击破状态：下一次撞到墙或箱子时会直接撞碎障碍物"# ok
    }

    player1_char=None
    player2_char=None
    current_player='player1'
    confirm = True
    while confirm:
        for event in py.event.get():
            if event.type == py.QUIT:
                exit_game()
            elif event.type == py.MOUSEBUTTONDOWN:
                for i,char in enumerate(characters):
                    if char_button[i].collidepoint(event.pos):
                        if current_player=='player1':
                            player1_char=char
                            if mod==0:
                                current_player='player2'
                        else:
                            player2_char=char
                    elif confirm_button.collidepoint(event.pos):
                        if player1_char is not None and( player2_char is not None or mod==1):
                            confirm=False

        screen.fill((255, 255, 255))
        #绘制角色按钮和技能介绍
        for i,char in enumerate(characters):
            py.draw.rect(screen, (255, 255, 255), char_button[i])
            screen.blit(images[char],char_button[i].topleft)
            #文本展示
            skill_text = skills[char]
            font = py.font.Font('SIMFANG.TTF', 18)
            skill_surf=font.render(skill_text,True,(0,0,0))
            text_rect = skill_surf.get_rect()
            text_rect.topleft=(char_button[i].topleft[0]+60,char_button[i].topleft[1]+60)
            screen.blit(skill_surf,text_rect)

            #显示选择的角色编号
            if char == player1_char:
                font = py.font.Font('SIMFANG.TTF', 30)
                text = font.render('P1', True, (255, 0, 0))
                text_rect = text.get_rect(center=(char_button[i].center[0] + 20, char_button[i].center[1] - 20))
                screen.blit(text, text_rect)
            elif char == player2_char:
                font = py.font.Font('SIMFANG.TTF', 30)
                text = font.render('P2', True, (0, 255, 0))
                text_rect = text.get_rect(center=(char_button[i].center[0] + 20, char_button[i].center[1] - 20))
                screen.blit(text, text_rect)

        font = py.font.Font('SIMFANG.TTF', 30)
        py.draw.rect(screen,(255,255,255),confirm_button)
        text=font.render('确定',True,(0,0,0))
        text_rect=text.get_rect(center=confirm_button.center)
        screen.blit(text,text_rect)         #四行代码全是按钮可视化
        #显示当前玩家选择
        font=py.font.Font('SIMFANG.TTF', 30)
        if current_player=='player1':
            text=font.render('Player 1选择',True,(0,0,0))
        else:
            text=font.render('Player 2选择',True,(0,0,0))
        text_rect=text.get_rect(center=(screen_width//2,50))
        screen.blit(text,text_rect)
        py.display.flip()
    return player1_char,player2_char

#选择地图函数
def choose_map():
    #显示地图选项，等待玩家选择地图
    map_id=None
    running = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
                py.quit()
                sys.exit()
            elif event.type == py.MOUSEBUTTONDOWN:
                for map_name,rect in map_buttons.items():
                    if rect.collidepoint(event.pos):
                        map_id=map_name
                        running = False
                        break
        screen.fill((255, 255, 255))
        #绘制地图按钮
        font = py.font.Font('SIMFANG.TTF', 40)
        text = font.render('选择地图', True, (0, 0, 0))
        text_rect = text.get_rect()
        screen.blit(text, ((screen_width - text_rect.width) // 2,(screen_height - text_rect.height) // 8))
        for map_name,image in map_images.items():
            button=map_buttons[map_name]
            screen.blit(image,button)
            py.draw.rect(screen,(0,0,0),button,2)
        py.display.flip()
    return map_id

#游戏主函数
def game_main(player1_char,player2_char,map_id):
    screen.fill((255, 255, 255))
    MAP = create_map.chose_map(map_id)
    for x in range(15):  # 15个格子 + 1边距
        for y in range(15):
            draw(MAP[x][y],x,y)

    global bombs,fires,players
    bombs.clear()
    fires.clear()
    players.clear()
    flag_yl=[False,False]
    flag_kfk=[False,False]
    players.append(Character([1,1],player1_char,0))
    if player2_char is not None:
        players.append(Character([len(MAP)-2,len(MAP[0])-2],player2_char,1))
    else :
        players.append(Character([1, len(MAP[0]) - 2], "robot1", 2))
        players.append(Character([len(MAP[0]) - 2, 1], "robot2", 3))
        players.append(Character([len(MAP[0]) - 2, len(MAP[0]) - 2], "robot3", 4))   # 初始化角色

    running = True
    while running:
        for event in py.event.get():        # for循环是因为同一时间可能会发生多个事件，这样能全部处理
            if event.type == py.QUIT:
                exit_game()
            elif event.type == py.KEYDOWN:
                move = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
                Move=[[0,1],[0,-1],[1,0],[-1,0]]
                move[2]=random.choice(Move)
                move[3]=random.choice(Move)
                move[4]=random.choice(Move)
                if event.key == py.K_LEFT:
                    move[0] = [0, -1]
                if event.key == py.K_RIGHT:
                    move[0] = [0, 1]
                if event.key == py.K_UP:
                    move[0] = [-1, 0]
                if event.key == py.K_DOWN:
                    move[0] = [1, 0]
                if event.key == py.K_a:
                    move[1] = [0, -1]
                if event.key == py.K_d:
                    move[1] = [0, 1]
                if event.key == py.K_w:
                    move[1] = [-1, 0]
                if event.key == py.K_s:
                    move[1] = [1, 0]
                if event.key == py.K_SLASH:
                    add=0
                    if players[0].player_char=='hh' and players[0].skill==1:
                        add=2
                    if players[0].player_boom_max+add > get_boom_num(0):
                        MAP[players[0].player_pos[0]][players[0].player_pos[1]]=3
                        new_boom = Bomb(players[0].player_pos[0],players[0].player_pos[1],0)
                        bombs.append(new_boom)
                if event.key == py.K_SPACE:
                    add = 0
                    if players[1].player_char == 'hh' and players[1].skill == 1:
                        add = 2
                    if players[1].player_boom_max+add > get_boom_num(1) and player2_char is not None:
                        MAP[players[1].player_pos[0]][players[1].player_pos[1]] = 3
                        new_boom = Bomb(players[1].player_pos[0], players[1].player_pos[1],1)
                        bombs.append(new_boom)
                if event.key == py.K_0:
                    if players[0].player_char=='zgn' and players[0].skill==1:
                        players[0].skill=0
                        MAP[players[0].player_pos[0]][players[0].player_pos[1]] = 5
                        draw(1, players[0].player_pos[0], players[0].player_pos[1])
                        draw(5,players[0].player_pos[0],players[0].player_pos[1])
                    if players[0].player_char=='yl' and players[0].skill==1:
                        players[0].skill = 0
                        flag_yl[0]=True
                    if players[0].player_char=='kfk' and players[0].skill==1:
                        players[0].skill = 0
                        flag_kfk[0]=True
                    if players[0].player_char == 'ly' and players[0].skill == 1:
                        print(len(MAP[0]),len(MAP))
                        players[0].skill = 0
                        MAP,players[0].player_pos = sam_skill(MAP)
                        for x in range(15):  # 15个格子 + 1边距
                            for y in range(15):
                                draw(1,x,y)
                                draw(MAP[x][y], x, y)

                if event.key == py.K_e:
                    if players[1].player_char == 'zgn' and players[1].skill == 1:
                        players[1].skill = 0
                        MAP[players[1].player_pos[0]][players[1].player_pos[1]] = 5
                        draw(1, players[1].player_pos[0], players[1].player_pos[1])
                        draw(5, players[1].player_pos[0], players[1].player_pos[1])
                    if players[1].player_char=='yl' and players[1].skill==1:
                        players[1].skill = 0
                        flag_yl[1]=True
                    if players[1].player_char=='kfk' and players[1].skill==1:
                        players[1].skill = 0
                        flag_kfk[1]=True
                    if players[1].player_char == 'ly' and players[1].skill == 1:
                        players[1].skill = 0
                        MAP, players[1].player_pos = sam_skill(MAP)
                        for x in range(15):  # 15个格子 + 1边距
                            for y in range(15):
                                draw(MAP[x][y], x, y)
                # 移动：将原位置覆盖为真实地图，并在下一个位置生成角色
                for player in players[:]:
                    if player.who<2:
                        draw(1,player.player_pos[0],player.player_pos[1])
                        draw(MAP[player.player_pos[0]][player.player_pos[1]],player.player_pos[0],player.player_pos[1])
                        MAP,player.player_pos,flag_yl[player.who] = game_rule.move_rule(MAP, player.player_pos, move[player.who],flag_yl[player.who])          # 移动
                        player.player_pos[0] = max(0, min(player.player_pos[0], N))
                        player.player_pos[1] = max(0, min(player.player_pos[1], N))  # 防止数组越界
                        MAP,player = game_rule.eat(MAP, player)
                        draw(MAP[player.player_pos[0]][player.player_pos[1]],player.player_pos[0],player.player_pos[1])# 吃东西
                    elif player.who>=2:
                        draw(1, player.player_pos[0], player.player_pos[1])
                        draw(MAP[player.player_pos[0]][player.player_pos[1]], player.player_pos[0],player.player_pos[1])
                        MAP, player.player_pos, flag_yl[0] = game_rule.move_rule(MAP, player.player_pos,move[player.who],flag_yl[0])  # 移动
                        player.player_pos[0] = max(0, min(player.player_pos[0], N))
                        player.player_pos[1] = max(0, min(player.player_pos[1], N))  # 防止数组越界
                        MAP, player = game_rule.eat(MAP, player)
                        draw(MAP[player.player_pos[0]][player.player_pos[1]], player.player_pos[0],player.player_pos[1])  # 吃东西
                        if random.randint(0, 1) < 0.1 and player.player_boom_max > get_boom_num(player.who):
                            MAP[player.player_pos[0]][player.player_pos[1]] = 3
                            new_boom = Bomb(player.player_pos[0], player.player_pos[1], player.who)
                            bombs.append(new_boom)

        for player in players[:]:
            screen.blit(images[player.player_char], (player.player_pos[1] * 50, player.player_pos[0] * 50))

        for bomb in bombs[:]:
            if player2_char is not None:
                MAP, flag_kfk[bomb.master] = bomb.update(MAP, players[bomb.master].player_boom_range,
                                                        flag_kfk[bomb.master])
            elif player2_char is None:
                for player in players[:]:
                    if bomb.master==player.who:
                        MAP, flag_kfk[1] = bomb.update(MAP, player.player_boom_range,
                                                                flag_kfk[1])


        for fire in fires[:]:
            fire.update(MAP)

        for player in players[:]:
            if player.life <= 0 :
                if  player.player_char== 'r' and player.skill== 1:
                    player.life=1
                    player.skill=0
                else:
                    draw(1, player.player_pos[0], player.player_pos[1])
                    draw(9, player.player_pos[0], player.player_pos[1])
                    players.remove(player)
        if get_player_num()==0 or (get_player_num()==1 and len(players)==1) :
            running=False
        py.display.update()

    time.sleep(2)
    game_finish()

def game_finish():
    MVP_gif = Image.open('结算界面.gif')
    frames = [frame.copy().resize((453, 240)) for frame in ImageSequence.Iterator(MVP_gif)]
    frames = frames[1:]
    frame_rate = 1 / MVP_gif.info['duration']

    screen.fill((255,255,255))
    font = py.font.SysFont('SIMFANG.TTF', 74,True)
    game_over_text = font.render('GAME OVER', True, (255, 0, 0))
    screen.blit(game_over_text, (500 // 2, 10))

    font = py.font.Font('SIMFANG.TTF', 40)
    text = font.render('返回主菜单', True, (0, 0, 0))
    text_rect = text.get_rect(center=back_to_menu_button.center)
    screen.blit(text, text_rect)
    text = font.render('结束游戏', True, (0, 0, 0))
    text_rect = text.get_rect(center=quit_game_button.center)
    screen.blit(text, text_rect)

    clock = py.time.Clock()
    py.time.set_timer(py.USEREVENT, int(1000 / frame_rate))

    running = True
    frame_index = 0
    while running:
        for event in py.event.get():        # for循环是因为同一时间可能会发生多个事件，这样能全部处理
            if event.type == py.QUIT:
                exit_game()
            elif event.type == py.MOUSEBUTTONDOWN:
                if back_to_menu_button.collidepoint(event.pos):
                    running=False
                    start_screen()
                elif quit_game_button.collidepoint(event.pos):
                    running=False

        py.draw.rect(screen, (255,255,255), (148, 100, 453, 240))
        # 显示当前帧
        frame = py.image.fromstring(
            frames[frame_index].tobytes(),
            frames[frame_index].size,
            frames[frame_index].mode
        )
        screen.blit(frame, (148, 100))
        py.display.flip()
        frame_index = (frame_index + 1) % len(frames)  # 循环播放

        # 限制帧率
        clock.tick(60)

        py.display.flip()

start_button = py.Rect(screen_width // 2 -100 ,screen_height // 2 - 50, 200, 50)            # 开始游戏按钮

music_button = py.Rect(screen_width // 2 -100 ,screen_height // 2 + 50, 200 ,50)            # 音乐设置按钮

music_function_button =[py.Rect(screen_width // 2 -150,screen_height // 2 + 150, 50, 50),
                        py.Rect(screen_width // 2 -50,screen_height // 2 + 150, 50, 50),
                        py.Rect(screen_width // 2 +50,screen_height // 2 + 150, 50, 50)]    # 播放器按钮

mode_button=[py.Rect(screen_width//2-100,screen_height//2-50,200,50),
             py.Rect(screen_width//2-100,screen_height//2+50,200,50)]                       # 游戏模式按钮


confirm_button = py.Rect(screen_width - 150, screen_height - 70, 100, 50)                   # 确定键

back_to_menu_button = py.Rect(screen_width // 2 - 350,screen_height // 2+100 , 200, 50)     # 返回主菜单

quit_game_button = py.Rect(screen_width // 2 ,screen_height // 2+100 , 200, 50)             # 结束游戏

map_buttons={
    "map1":py.Rect(150,150,200,150),
    "map2":py.Rect(650,150,200,150),
    "map3":py.Rect(150,450,200,150),
    "map4":py.Rect(650,450,200,150)
}                                                                                           # 选择地图按钮

char_button=[]
for i in range(7):
    x=50
    y=i*95+50
    char_button.append(py.Rect(x, y, 100, 75))

#显示开始界面并等待玩家点击开始游戏
#玩家点击了开始游戏，运行游戏主函数
start_screen()

exit_game()