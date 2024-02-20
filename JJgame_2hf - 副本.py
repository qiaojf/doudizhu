import time
import socket,sys
import os
import matplotlib.pyplot as plt
import pyautogui as pg
import win32api
import win32con
import win32gui
from PIL import Image, ImageGrab
from skimage import io
import threading
import struct
import hashlib
import json

import shutil  
pg.FAILSAFE = False
pg.PAUSE = 0.5

players = ['player1','player2','player3']
game_num = 0
# win_num = 0

tmp_path = './tmp/'
if not os.path.exists(tmp_path):
    os.mkdir(tmp_path)
else:
    shutil.rmtree(tmp_path)
    os.mkdir(tmp_path)

def get_img(i,record):
    while True:
        img = ImageGrab.grab((200, 0, 1640, 990))  # x=1440 y=990
        file = r'./{}.jpg'.format(i)
        try:
            img.save(file)
        except:
            print('wrong')
            img.save(file)
        img = io.imread(file)
        if img[50,640,0]>220 and img[50,640,1]>220 and img[50,640,2]>220: # 有地主牌
            if img[590,760,0]<10 or img[590,760,2]:   #计时器在当前玩家
                time.sleep(0.8)
                img = ImageGrab.grab((200, 0, 1640, 990))  # x=1440 y=990
                file = r'./{}.jpg'.format(i)
                try:
                    img.save(file)
                except:
                    img.save(file)
                img = io.imread(file)
                break
            elif img[383,340,0]<10:   #计时器在上家
                break
            elif img[383,1180,0]<10:    #计时器在下家
                break
            elif img[720,225,0]>200 and img[160,270,0]>200 and img[160,1090,0]>200:  # 没有计时器,游戏结束
                record = []
                time.sleep(0.5)
                img = ImageGrab.grab((200, 0, 1640, 990))  # x=1440 y=990
                file = r'./{}.jpg'.format(i)
                try:
                    img.save(file)
                except:
                    img.save(file)
                img = io.imread(file)
                if pg.pixelMatchesColor(425, 720, (255, 181, 14), tolerance=10): 
                    win_num += 1
                time.sleep(3)
                break
        elif pg.pixelMatchesColor(950, 350, (135, 62, 45), tolerance=10):
            record = []
            time.sleep(3)
            break
        elif pg.pixelMatchesColor(1000, 290, (248, 217, 124), tolerance=10):
            record = []
            time.sleep(3)
            break
        elif pg.pixelMatchesColor(1300, 965, (49, 175, 91), tolerance=10):         #有再来一局按钮
            record = []
            time.sleep(3)
            break
        elif pg.pixelMatchesColor(1300, 880, (48, 166, 90), tolerance=10):         #有再来一局按钮
            record = []
            time.sleep(3)
            break
    if i == 1:
        io.imsave(r'./1.jpg', img)
    else:
        old_img = io.imread(r'./{}.jpg'.format(i-1))
        if img[590,760,0]<10: 
            if img[590,760,0]==old_img[590,760,0] and img[383,1180,0]==old_img[383,1180,0]:
                pass
            else:
                io.imsave(r'./tmp/{}.jpg'.format(i), img)
        elif img[383,340,0]<10:
            if img[383,340,0]==old_img[383,340,0] and img[590,760,0]==old_img[590,760,0]:
                pass
            else:
                io.imsave(r'./tmp/{}.jpg'.format(i), img)
        elif img[383,1180,0]<10:
            if img[383,340,0]==old_img[383,340,0] and img[383,1180,0]==old_img[383,1180,0]:
                pass
            else:
                io.imsave(r'./tmp/{}.jpg'.format(i), img)
        elif img[720,225,0]>200 and img[160,270,0]>200 and img[160,1090,0]>200:
            if img[720,225,0]==old_img[720,225,0] and img[160,270,0]==old_img[160,270,0] and img[160,1090,0]==old_img[160,1090,0]:
                pass
            else:
                io.imsave(r'./tmp/{}.jpg'.format(i), img)
        try:
            os.remove('./{}.jpg'.format(i-1))
        except:
            print('wrong')
            os.remove('./{}.jpg'.format(i-1))
    return record

def act_pokes(act_data,my_left_cards):
    chain_cards = ['solo_chain_5','solo_chain_6','solo_chain_7','solo_chain_8','solo_chain_9','solo_chain_10','solo_chain_11','solo_chain_12',
    'pair_chain_3','pair_chain_4','pair_chain_5','pair_chain_6','pair_chain_7','pair_chain_8','pair_chain_9','pair_chain_10',
    'trio_chain_2','trio_chain_3','trio_chain_4','trio_chain_5','trio_chain_6','rocket',
    ]
    with_one = ['trio_solo','trio_solo_chain_2','trio_solo_chain_3','trio_solo_chain_4','trio_solo_chain_5','four_two_solo',]
    with_two = ['trio_pair','trio_pair_chain_2','trio_pair_chain_3','trio_pair_chain_4','four_two_pair',]

    def single_click(x,y):
        pg.moveTo(float(x)*1440+200,float(y)*990,0.2)
        pg.click()

    def drag_rec(x1,y1,x2,y2):
        pg.moveTo(float(x1)*1440+200,float(y1)*990,0.2)
        if len(act_data[1]) >= 5:
            pg.dragTo(float(x2)*1440+200,float(y2)*990,1.5,button='left')
        else:
            pg.dragTo(float(x2)*1440+200,float(y2)*990,1,button='left')
    # print(my_left_cards)
    if act_data == ['PASS']:
        pg.moveTo(960,670,0.3)
        pg.click()
    else:
        if act_data[1] == 'solo':           #出单
            for i in my_left_cards:
                if i[0] == act_data[0][0]:
                    x1 = i[1][0]
                    y1 = i[1][1]
                    break
            my_only_cards = [i[0] for i in my_left_cards]
            if 'BJ' in my_only_cards and 'CJ' in my_only_cards and act_data[0][0] in ['BJ','CJ']:
                single_click(x1,y1)
                time.sleep(1)
                single_click(xi,y1)
            else:
                single_click(x1,y1)
        elif act_data[1] == 'pair':
            for j in set(act_data[0]):
                cand_cards = [x for x in my_left_cards if x[0]==j]
                x1 = cand_cards[0][1][0]
                y1 = cand_cards[0][1][1]
                x2 = cand_cards[1][1][0]
                y2 = cand_cards[1][1][1]
                drag_rec(x1,y1,x2,y2)
        elif act_data[1] == 'trio':
            for j in set(act_data[0]):
                cand_cards = [x for x in my_left_cards if x[0]==j]
                x1 = cand_cards[0][1][0]
                y1 = cand_cards[0][1][1]
                x2 = cand_cards[2][1][0]
                y2 = cand_cards[2][1][1]
                drag_rec(x1,y1,x2,y2)
        elif act_data[1] == 'bomb':        #出炸弹
            x = [i[1][0] for i in my_left_cards if i[0]==act_data[0][0]]
            y = [i[1][1] for i in my_left_cards if i[0]==act_data[0][0]]
            x1 = max(x)
            y1 = y[x.index(x1)]
            x2 = min(x)
            y2 = y[x.index(x2)]
            drag_rec(x1,y1,x2,y2)
        elif act_data[1] in chain_cards:        #出顺,出火箭
            x = [i[1][0] for i in my_left_cards if i[0] in act_data[0]]
            y = [i[1][1] for i in my_left_cards if i[0] in act_data[0]]
            # print(my_left_cards)
            # print(x,y)
            x1 = max(x)
            y1 = y[x.index(x1)]
            x2 = min(x)
            y2 = y[x.index(x2)]
            drag_rec(x1,y1,x2,y2)
            # print(x1,y1,x2,y2)
        elif act_data[1] in with_one:               #出带单
            d_list = [x for x in act_data[0] if act_data[0].count(x)>=3]
            x = [i[1][0] for i in my_left_cards if i[0] in d_list]
            y = [i[1][1] for i in my_left_cards if i[0] in d_list]
            x1 = max(x)
            y1 = y[x.index(x1)]
            x2 = min(x)
            y2 = y[x.index(x2)]
            drag_rec(x1,y1,x2,y2)
            for i in set(act_data[0]):
                if act_data[0].count(i) == 1:
                    for j in my_left_cards:
                        if j[0] == i:
                            x1 = j[1][0]
                            y1 = j[1][1]
                            break
                    single_click(x1,y1)
        elif act_data[1] in with_two:               #出带对
            d_list = [x for x in act_data[0] if act_data[0].count(x)>=3]
            x = [i[1][0] for i in my_left_cards if i[0] in d_list]
            y = [i[1][1] for i in my_left_cards if i[0] in d_list]
            x1 = max(x)
            y1 = y[x.index(x1)]
            x2 = min(x)
            y2 = y[x.index(x2)]
            drag_rec(x1,y1,x2,y2)
            p_list = [x for x in act_data[0] if act_data[0].count(x)==2]
            for j in set(p_list):
                cand_cards = [x for x in my_left_cards if x[0]==j]
                x1 = cand_cards[0][1][0]
                y1 = cand_cards[0][1][1]
                x2 = cand_cards[1][1][0]
                y2 = cand_cards[1][1][1]
                drag_rec(x1,y1,x2,y2)
        pg.moveTo(680,670,0.2)
        pg.click()

def deal_data(dt_boxes,rec_res):
    lord_cards = []
    forward_player_cards = []
    back_player_cards = []
    my_cards = []
    my_left_cards = []
    bbox = sorted(dt_boxes,key=lambda x: x[0],reverse=True)
    act_flag = False
    for i in bbox:
        if float(i[1]) < 0.11111:  #地主牌 y<110
            lord_cards.append(rec_res[dt_boxes.index(i)])
        elif float(i[0]) < 0.5417 and float(i[1]) < 0.48485 and float(i[1]) > 0.15152:  #上家出牌 x<780,150<y<480
            forward_player_cards.append(rec_res[dt_boxes.index(i)])
        elif float(i[0]) > 0.5417 and float(i[1]) < 0.48485 and float(i[1]) > 0.15152:  #下家出牌  x>780,150<y<480
            back_player_cards.append(rec_res[dt_boxes.index(i)])
        elif float(i[1]) > 0.75757:    #当前玩家手牌 y>750
            my_left_cards.append((rec_res[dt_boxes.index(i)],i))
        elif float(i[1]) > 0.50505 and float(i[1]) < 0.75757: #当前玩家出牌 500<y<750
            if float(i[0]) > 0.27778 and rec_res[dt_boxes.index(i)] == 'PASS':
                act_flag = True
            else:
                my_cards.append(rec_res[dt_boxes.index(i)])
    return forward_player_cards,back_player_cards,my_cards,my_left_cards,act_flag

def get_player(player_mark):
    if player_mark == []:
        forward_player,my_player,back_player = 'forward_player','my_player','back_player'
    else:
        if player_mark == 'forward_player':
            forward_player,my_player,back_player = players[0],players[1],players[2]
        elif player_mark == 'my_player':
            forward_player,my_player,back_player = players[2],players[0],players[1]
        elif player_mark == 'back_player':
            forward_player,my_player,back_player = players[1],players[2],players[0]
    return forward_player,my_player,back_player

def get_record(player_mark,record,forward_player_cards,back_player_cards,my_cards):
    def game_over():
        game_over = False
        left_num1,left_num2,left_num3=0,0,0
        if record != []:
            records =[x for x in record if x[1]!=['PASS']]
            for i in records:
                if i[0] == players[0]:
                    left_num1 += len(i[1])
                elif i[0] == players[1]:
                    left_num2 += len(i[1])
                elif i[0] == players[2]:
                    left_num3 += len(i[1])
            if left_num1 == 20 or left_num2 == 17 or left_num3 == 17:
                game_over = True
        else:
            left_num1,left_num2,left_num3=0,0,0
        return game_over
    def write_record(record,player_mark):
        with open('./jj_record.txt','a',encoding="utf-8") as f:
            f.write(str(record)+','+'\n')
        record = []
        player_mark = []
        is_over = False
        return record,player_mark,is_over

    forward_player,my_player,back_player = get_player(player_mark)
    if forward_player_cards != [] and back_player_cards == [] and my_cards == []: 
        if len(record) == 0:    #上家首先出牌
            player_mark = 'forward_player'
            record.append((players[0],forward_player_cards))
        else:
            if record[-1] == (my_player,['PASS']):
                record.append((back_player,['PASS']))
                record.append((forward_player,forward_player_cards))
            elif record[-1] == (back_player,['PASS']):
                record.append((forward_player,forward_player_cards))
            elif record[-1][0] == forward_player and record[-1][1] != forward_player_cards:
                record.append((my_player,['PASS']))
                record.append((back_player,['PASS']))
                record.append((forward_player,forward_player_cards))
    elif forward_player_cards == [] and back_player_cards != [] and my_cards == []: 
        if len(record) == 0:    #下家首先出牌
            player_mark = 'back_player'
            record.append((players[0],back_player_cards))
        else:
            if record[-1] == (forward_player,['PASS']):
                record.append((my_player,['PASS']))
                record.append((back_player,back_player_cards))
            elif record[-1] == (my_player,['PASS']):
                record.append((back_player,back_player_cards))
    elif forward_player_cards == [] and back_player_cards == [] and my_cards != []: 
        if len(record) == 0:    #当前玩家首先出牌
            player_mark = 'my_player'
            record.append((players[0],my_cards))
        else:
            if record[-1] == (back_player,['PASS']):
                record.append((forward_player,['PASS']))
                record.append((my_player,my_cards))
            elif record[-1] == (forward_player,['PASS']):
                record.append((my_player,my_cards))
    elif forward_player_cards != [] and back_player_cards != [] and my_cards == []: # 当前玩家出牌
        if record == []:
            pass
        elif record[-1] == (back_player,back_player_cards):
            record.append((forward_player,forward_player_cards))
        elif record[-1][0] == back_player and record[-1][1] != back_player_cards:
            record.pop()
            record.append((back_player,back_player_cards))
            record.append((forward_player,forward_player_cards))
        elif record[-1] == (forward_player,forward_player_cards) and record[-2] != (back_player,back_player_cards):
            record.append((my_player,['PASS']))
            record.append((back_player,back_player_cards))
        elif record[-1][0] == my_player:
            record.append((back_player,back_player_cards))
            record.append((forward_player,forward_player_cards))
    elif forward_player_cards != [] and back_player_cards == [] and my_cards != []: # 下家出牌
        if record == []:
            pass
        else:
            if record[-1] == (forward_player,forward_player_cards):
                record.append((my_player,my_cards))
            elif record[-1][0] == forward_player and record[-1][1] != forward_player_cards:
                record.pop()
                record.append((forward_player,forward_player_cards))
                record.append((my_player,my_cards))
            elif record[-1][0] == my_player and record[-1][1] != my_cards:
                record.pop()
                record.append((my_player,my_cards))
            elif record[-1] == (my_player,my_cards) and record[-2] != (forward_player,forward_player_cards):
                record.append((back_player,['PASS']))
                record.append((forward_player,forward_player_cards))
            elif record[-1][0] == back_player:
                record.append((forward_player,forward_player_cards))
                record.append((my_player,my_cards))
    elif forward_player_cards == [] and back_player_cards != [] and my_cards != []: # 上家出牌
        if record == []:
            pass
        elif record[-1] == (my_player,my_cards):
            record.append((back_player,back_player_cards))
        elif record[-1][0] == my_player and record[-1][1] != my_cards:
            record.pop()
            record.append((my_player,my_cards))
            record.append((back_player,back_player_cards))
        elif record[-1] == (back_player,back_player_cards) and record[-2] != (my_player,my_cards):
            record.append((forward_player,['PASS']))
            record.append((my_player,my_cards))
        elif record[-1][0] == forward_player:
            record.append((my_player,my_cards))
            record.append((back_player,back_player_cards))
    elif forward_player_cards != [] and back_player_cards != [] and my_cards != []:
        if my_cards == ['PASS']:
            if record[-1] == (back_player,back_player_cards):
                record.append((forward_player,forward_player_cards))
            elif record[-1][0] == back_player and record[-1][1] != back_player_cards:
                record.pop()
                record.append((back_player,back_player_cards))
                record.append((forward_player,forward_player_cards))
            elif record[-1] == (forward_player,forward_player_cards) and record[-2] != (back_player,back_player_cards):
                record.append((my_player,['PASS']))
                record.append((back_player,back_player_cards))
            elif record[-1] == (my_player,['PASS']):
                record.append((back_player,back_player_cards))
                record.append((forward_player,forward_player_cards))
    elif forward_player_cards == [] and back_player_cards == [] and my_cards == []:
        if record != []:
            if record[-1][0] == forward_player:
                record.append((my_player,['PASS']))
            elif record[-1][0] == my_player:
                record.append((back_player,['PASS']))
            elif record[-1][0] == back_player:
                record.append((forward_player,['PASS']))                
    if game_over():
        record,player_mark,is_over = write_record(record,player_mark)
    # print(record[-1])
    return record,player_mark

def socket_client(game_num):
    while True:
        ADDR =('10.21.8.9',9999)
        reg_sock = socket.socket()
        ADDR1 =('127.0.0.1',8888)
        strategy_sock = socket.socket()
        reg_sock.connect(ADDR)
        print('reg server connected success')
        strategy_sock.connect(ADDR1)
        print('strategy server connected success')
        record = []
        is_over = False
        i = 1
        while True:
            try:
                pic_path = './tmp/'
                record = get_img(i,record)
                if record == []:
                    player_mark = []
                if len(os.listdir(pic_path)) > 0:
                    filelist = sorted(os.listdir(pic_path),key=lambda x:int(x[:-4]))
                    filepath = pic_path + filelist[0]
                    if os.path.isfile(filepath):
                        fileinfo_size = struct.calcsize('64sl64s')
                        with open(filepath, 'rb') as fp:
                            data = fp.read()
                        img_md5 = hashlib.md5(data).hexdigest()
                        fhead = struct.pack('64sl64s', bytes(os.path.basename(filepath).encode('utf-8')),os.stat(filepath).st_size,img_md5.encode(encoding='utf-8'))
                        reg_sock.send(fhead)
                        reg_sock.sendall(data)
                        print ('{0} file send over...'.format(filepath))
                        res = reg_sock.recv(512).decode()
                        if res == 'file send over!':
                            res_size = reg_sock.recv(512).decode()
                            reg_sock.sendall('准备接受数据'.encode('utf-8'))
                            recv_size  = 0   
                            recv_data = b''  
                            while recv_size < int(res_size):  
                                res_data = reg_sock.recv(512)
                                recv_size += len(res_data)  
                                recv_data += res_data
                            os.remove(filepath)
                            recv_data = eval(recv_data)
                            dt_boxes,rec_res = recv_data[0],recv_data[1]
                            forward_player_cards,back_player_cards,my_cards,my_left_cards,act_flag = deal_data(dt_boxes,rec_res)
                            print('上家：{0},本家：{1},下家：{2}'.format(forward_player_cards,my_cards,back_player_cards))
                            record,player_mark = get_record(player_mark,record,forward_player_cards,back_player_cards,my_cards)
                            if record != [] and act_flag == True:
                                forward_player,my_player,back_player = get_player(player_mark)
                                if record[-1][0] == back_player:
                                    record.append((forward_player,['PASS']))
                                elif record[-1][0] == my_player:
                                    record.append((back_player,['PASS']))
                                    record.append((forward_player,['PASS']))
                            if act_flag == True:    
                                act_data = strategy_socket(my_left_cards,record,strategy_sock)
                                if act_data != '':
                                    act_data = eval(act_data)
                                    print(act_data)
                                    act_pokes(act_data,my_left_cards)
                                    if act_data != ['PASS']:
                                        if record != []:
                                            if record[-1][0] == back_player:
                                                record.append((forward_player,['PASS']))
                                                record.append((my_player,act_data[0]))
                                            elif record[-1][0] == my_player:
                                                record.append((back_player,['PASS']))
                                                record.append((forward_player,['PASS']))
                                                record.append((my_player,act_data[0]))
                                            elif record[-1][0] == forward_player:
                                                record.append((my_player,act_data[0]))  
                                        # else:
                                        #     forward_player,my_player,back_player = get_player(player_mark)
                                        #     record.append((players[0],act_data[0]))  
                                act_flag = False
                        elif res == 'file send wrong!':
                            continue
                i += 1
            except:
                reg_sock.close()
                strategy_sock.close()
                break

def strategy_socket(my_left_cards,record,strategy_sock):
    cards_data = []
    for i in my_left_cards:
        cards_data.append(i[0])
    send_data = str((record,cards_data)).encode('utf-8')
    strategy_sock.sendall(send_data)
    act_data = strategy_sock.recv(512).decode()
    return act_data

def baoming():
    if pg.pixelMatchesColor(1050, 660, (84, 185, 17), tolerance=10):
        pg.moveTo(1100, 660,duration=0.6)
        pg.click()
        time.sleep(5)
        return 1
    else:
        pg.moveTo(1250, 350,duration=0.6)
        pg.click()
        time.sleep(2)
        return 0

def in_newplayer():
    pg.moveTo(400, 240,duration=0.6)
    pg.click()
    time.sleep(2)
    res = baoming()
    return res

def in_2000player():
    pg.moveTo(1060, 240,duration=0.6)
    pg.click()
    time.sleep(2)
    res = baoming()
    return res

def set_forward():
    hwnd_title = {}
    def get_all_hwnd(hwnd, mouse):
        if (win32gui.IsWindow(hwnd) and
            win32gui.IsWindowEnabled(hwnd) and
            win32gui.IsWindowVisible(hwnd)):
            hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

    win32gui.EnumWindows(get_all_hwnd, 0)
    for h, t in hwnd_title.items():
        if t :
            if '斗地主-新手场' in t:
                h = win32gui.FindWindow(None,t)
                if not win32gui.GetWindowLong(h, win32con.GWL_EXSTYLE):
                    pg.press('enter')
                    win32gui.SetForegroundWindow(h)
                    time.sleep(2)
                break

def click_but():
    epoch = 0
    win_count = 0
    while True:
        img_name = len(os.listdir('./imgs'))
        try:
            if pg.pixelMatchesColor(1400, 670, (219, 80, 21), tolerance=10):   #有不叫按钮
                pg.moveTo(600, 670,duration=0.6)
                pg.click()
                time.sleep(1)
                pg.click(1350, 670,duration=0.5)
            elif pg.pixelMatchesColor(1050, 670, (211, 129, 27), tolerance=10) and not pg.pixelMatchesColor(1300, 670, (210, 128, 26), tolerance=10):         #有要不起按钮
                pg.click(960, 670,duration=0.6)
            elif pg.pixelMatchesColor(1300, 965, (49, 175, 91), tolerance=10):         #有再来一局按钮
                time.sleep(3)
                res_img = pg.screenshot('./imgs/{}.png'.format(img_name),region=(500,100, 900, 900))
                if not (pg.pixelMatchesColor(920, 380, (255, 255, 221), tolerance=10) and pg.pixelMatchesColor(900, 490, (255, 228, 78), tolerance=10)):
                    win_count += 1
                pg.moveTo(1250, 940,duration=1)
                pg.click()
                time.sleep(5)
                epoch += 1
            elif pg.pixelMatchesColor(1300, 880, (48, 166, 90), tolerance=10):         #有再来一局按钮
                time.sleep(3)
                res_img = pg.screenshot('./imgs/{}.png'.format(img_name),region=(500,100, 900, 900))
                if not (pg.pixelMatchesColor(920, 380, (255, 255, 221), tolerance=10) and pg.pixelMatchesColor(900, 490, (255, 228, 78), tolerance=10)):
                    win_count += 1
                pg.moveTo(1250, 860,duration=1)
                pg.click()
                time.sleep(5)
                epoch += 1
            elif pg.pixelMatchesColor(850, 920, (30, 155, 213), tolerance=10):         #有取消托管按钮
                pg.moveTo(950, 920,duration=0.5)
                pg.click()
            elif pg.pixelMatchesColor(410, 700, (255, 205, 64), tolerance=10) and pg.pixelMatchesColor(450, 140, (255, 204, 60), tolerance=10) and pg.pixelMatchesColor(1430, 140, (255, 203, 60), tolerance=10):
                pg.moveTo(1895,14,duration=0.6)
                pg.click()
                pg.moveTo(1300,860,duration=0.6)
                pg.click()
            elif pg.pixelMatchesColor(370, 230, (246, 223, 156), tolerance=10):
                res = in_newplayer()
                if res == 0:
                    res = in_2000player()
            else:
                set_forward()
        except:
            continue

def count_client():
    while True:
        ADDR =('10.21.8.67',5555)
        reg_sock = socket.socket()
        reg_sock.connect(ADDR)
        print('reg server connected success')
        while True:
            try:
                pic_path = './imgs/'
                if len(os.listdir(pic_path)) > 0:
                    filelist = sorted(os.listdir(pic_path),key=lambda x:int(x[:-4]))
                    filepath = pic_path + filelist[0]
                    if os.path.isfile(filepath):
                        fileinfo_size = struct.calcsize('64sl64s')
                        with open(filepath, 'rb') as fp:
                            data = fp.read()
                        img_md5 = hashlib.md5(data).hexdigest()
                        fhead = struct.pack('64sl64s', bytes(os.path.basename(filepath).encode('utf-8')),os.stat(filepath).st_size,img_md5.encode(encoding='utf-8'))
                        reg_sock.send(fhead)
                        reg_sock.sendall(data)
                        res = reg_sock.recv(512).decode()
                        print(res)
                        if res != 'file send over!':
                            continue
                        elif res == 'file send over!':
                            os.remove(filepath)
                time.sleep(20)
            except:
                reg_sock.close()
                break



t1 = threading.Thread(target=click_but, args=())
t2 = threading.Thread(target=socket_client, args=(game_num,))
# t3 = threading.Thread(target=count_client, args=())
t1.start()
t2.start()
# t3.start()







