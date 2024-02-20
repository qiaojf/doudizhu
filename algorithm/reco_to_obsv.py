import os
from poke import Game_env
from doudizhu.engine import sort_cards,Doudizhu
import numpy as np
import time


card_type = Doudizhu.CARD_TYPE
game = Game_env()

def cardstype(cards):
    if cards == None or cards == ['PASS']:
        return None
    else:
        ok,act_type = Doudizhu.check_card_type(cards)
        return act_type[0][0] 

def get_info(record_slice,player,player_cards):
    player_cards_left = player_cards.copy()
    player_record = []
    cards = [i[1] for i in record_slice if i[0]==player and i[1]not in [['PASS'],['yaobuqi']]]
    for i in cards:
        for j in sort_cards(i):
            player_record.append(j)
    for i in player_record:
        player_cards_left.remove(i)
    return player_cards_left    

    
def read_file(filename,player):
    x_train,y_train=[],[]
    with open('./records/%s.txt'%player,'r',encoding='utf-8') as f:
        while 1:
            record = f.readline().strip()
            if not record:
                break
            record = eval(record)
            player_acts = [i for i in record if i[0]==player and i[1] not in [['PASS'],['yaobuqi']]]
            player_cards = []
            for x in player_acts:
                for j in x[1]:
                    player_cards.append(j)
            player_cards = sort_cards(player_cards)
            if player == 'player1':
                try:
                    observation = game.get_observation([],player_cards)
                    y_train.append(game.action_space.index(record[0][1]))
                    x_train.append(observation)
                except:
                    pass
            for i in range(1,len(record)-1):
                record_slice = record[:i+1]
                if len(record_slice) % 3 == 0 and player == 'player1' and record[i][1]!=['yaobuqi']:     #player1
                    try:
                        player_cards_left = get_info(record_slice,player,player_cards)
                        observation = game.get_observation(record_slice,player_cards_left)
                        if record[i+1][1] != ['yaobuqi']:
                            y_train.append(game.action_space.index(record[i+1][1]))
                            x_train.append(observation)
                    except:
                        continue
                elif len(record_slice) % 3 == 1 and player == 'player2' and record[i][1]!=['yaobuqi']:       #player2
                    try:
                        player_cards_left = get_info(record_slice,player,player_cards)
                        observation = game.get_observation(record_slice,player_cards_left)
                        if record[i+1][1] != ['yaobuqi']:
                            y_train.append(game.action_space.index(record[i+1][1]))
                            x_train.append(observation)
                    except:
                        continue
                elif len(record_slice) % 3 == 2 and player == 'player3' and record[i][1]!=['yaobuqi']:     #player3
                    try:
                        player_cards_left = get_info(record_slice,player,player_cards)
                        observation = game.get_observation(record_slice,player_cards_left)
                        if record[i+1][1] != ['yaobuqi']:
                            y_train.append(game.action_space.index(record[i+1][1]))
                            x_train.append(observation)
                    except:
                        continue
    return x_train,y_train



if __name__ == "__main__":
    players = ['player1','player2','player3']
    player = players[0]
    file = '%s.txt'%player
    x_train,y_train = read_file(file,player)
    print(len(x_train))

