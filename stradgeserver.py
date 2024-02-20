
import json
import random
import socket
import threading
import time
import numpy as np
import tensorflow as tf
from doudizhu.engine import Doudizhu,sort_cards
from doudizhu import Card, engine
from poke import Game_env
from RL_brain1 import DQNPrioritizedReplay, PolicyGradient, PolicysGradient
from socketserver import BaseRequestHandler,ThreadingTCPServer

tf.compat.v1.disable_eager_execution()
players = ['player1','player2','player3']
card_type = Doudizhu.CARD_TYPE
STR_RANKS = '3-4-5-6-7-8-9-10-J-Q-K-A-2-BJ-CJ'.split('-')
INT_RANKS = range(1,16)
CHAR_RANK_TO_INT_RANK = dict(zip(STR_RANKS, INT_RANKS))
game = Game_env()
model_name1 = r'Model_last/player1_0.5_1000.ckpt'
RL_1 = PolicyGradient(
            game.n_actions, 
            game.n_features,
        )
RL_1.load_model(model_name1)
model_name2 = r'Model_last/player2_0.5_1000.ckpt'
RL_2 = PolicysGradient(
    game.n_actions, 
    game.n_features,
    )
RL_2.load_model(model_name2)
model_name3 = r'Model_last/player3_0.5_1000.ckpt'
RL_3 = DQNPrioritizedReplay(
    game.n_actions, 
    game.n_features,
    )
RL_3.load_model(model_name3)

class StradgeServer(BaseRequestHandler):
    def cardstype(self,cards):
        if cards == None or cards == ['PASS']:
            return None
        else:
            ok,act_type = Doudizhu.check_card_type(cards)
            return act_type[0][0] 

    def get_player(self,mark):
        if mark == players[0]:
            player = players[1]
        elif mark == players[1]:
            player = players[2]
        elif mark == players[2]:
            player = players[0]
        return player

    def get_act(self,act):
        acts = list(set(act))
        if 'BJ' in acts:
            acts.remove('BJ')
        if 'CJ' in acts:    
            acts.remove('CJ')
        for k in acts:
            idx = [i for i,x in enumerate(act) if x==k]
            if len(idx) == 1:
                act[idx[0]] = k+'c'
            elif len(idx) == 2:
                act[idx[0]] = k+'c'
                act[idx[1]] = k+'d'
            elif len(idx) == 3:
                act[idx[0]] = k+'c'
                act[idx[1]] = k+'d'
                act[idx[2]] = k+'h'
            elif len(idx) == 4:
                act[idx[0]] = k+'c'
                act[idx[1]] = k+'d'
                act[idx[2]] = k+'h'
                act[idx[3]] = k+'s'
        return act

    def get_cards(self,cards):
        card = list(set(cards))
        if 'BJ' in card:
            card.remove('BJ')
        if 'CJ' in card:
            card.remove('CJ')
        for k in card:
            idx = [i for i,x in enumerate(cards) if x==k]
            if len(idx) == 1:
                cards[idx[0]] = k+'s'
            elif len(idx) == 2:
                cards[idx[0]] = k+'s'
                cards[idx[1]] = k+'h'
            elif len(idx) == 3:
                cards[idx[0]] = k+'s'
                cards[idx[1]] = k+'h'
                cards[idx[2]] = k+'d'
            elif len(idx) == 4:
                cards[idx[0]] = k+'s'
                cards[idx[1]] = k+'h'
                cards[idx[2]] = k+'d'
                cards[idx[3]] = k+'c'
        return cards

    def get_mark(self,record):
        if record == []:
            act_mark = ('player1',None)
        else:
            records =[x for x in record if x[1]!=['PASS']]
            act = records[-1][1]
            acts = self.get_act(act)
            act_mark = (records[-1][0],acts)
        return act_mark

    def change_data(self,data):
        data = eval(data)
        player_cards = data[1]
        record = data[0]
        return player_cards,record

    def list_candidate(self,type_list,cards_str):  #候选牌列表
        cards_candidate = []
        for i in range(len(card_type)):
            for x in type_list:
                if card_type[i]['name'] == x:
                    actions_list = card_type[i]['func']() #actions_list=[('BJ-CJ', 0)]
                    for j in actions_list:    #j=('BJ-CJ', 0)
                        action = [a for a in j[0].split('-')]  #action=['BJ', 'CJ']
                        flag = True
                        for k in action:
                            if  cards_str.count(k) < action.count(k):
                                flag = False
                                break
                        if flag == True:
                            cards_candidate.append(action)
        actions =cards_candidate
        cards_candidate = []
        return actions

    def update_actions_candy(self,actions_candy):
        def change_actions_candy(cards_list):
            single_list,pairs_list,trio_list,trio_2_list,trio_3_list = [],[],[],[],[]
            cards_list1 = cards_list
            cards_list2 = cards_list.copy()
            # print(cards_list1,cards_list2)
            for i in cards_list:
                if self.cardstype(i) == 'solo':
                    single_list.append(i)
                elif self.cardstype(i) == 'pair':
                    pairs_list.append(i)
                elif self.cardstype(i) == 'trio':
                    trio_list.append(i)
                elif self.cardstype(i) == 'trio_chain_2':
                    trio_2_list.append(i)
                elif self.cardstype(i) == 'trio_chain_3':
                    trio_3_list.append(i)
            if len(single_list) >= 3*len(trio_3_list):  #三连三带三
                if trio_3_list != []:
                    cards_list1.remove(single_list[0])
                    cards_list1.remove(single_list[1])
                    cards_list1.remove(single_list[2])
                    cards_list1[cards_list1.index(trio_3_list[0])] = sort_cards(trio_3_list[0]+single_list[0]+single_list[1]+single_list[2])
                    single_list = single_list[3:]
            if len(single_list) >= 2*len(trio_2_list): #三连二带二
                if trio_2_list != []:
                    cards_list1.remove(single_list[0])
                    cards_list1.remove(single_list[1])
                    cards_list1[cards_list1.index(trio_2_list[0])] = sort_cards(trio_2_list[0]+single_list[0]+single_list[1])
                    single_list = single_list[2:]
            if len(single_list) >= len(trio_list):  #三带一
                if trio_list != []:
                    for i in range(len(trio_list)):
                        cards_list1.remove(single_list[i])
                        cards_list1[cards_list1.index(trio_list[i])] = sort_cards(trio_list[i]+single_list[i])  
            if len(pairs_list) >= 3*len(trio_3_list):   #三连三带三队
                if trio_3_list != []:
                    cards_list2.remove(pairs_list[0])
                    cards_list2.remove(pairs_list[1])
                    cards_list2.remove(pairs_list[2])
                    cards_list2[cards_list2.index(trio_3_list[0])] = sort_cards(trio_3_list[0]+pairs_list[0]+pairs_list[1]+pairs_list[2])
                    pairs_list = pairs_list[3:]
            if len(pairs_list) >= 2*len(trio_2_list):   #三连二带二队
                if trio_2_list != []:
                    cards_list2.remove(pairs_list[0])
                    cards_list2.remove(pairs_list[1])
                    cards_list2[cards_list2.index(trio_2_list[0])] = sort_cards(trio_2_list[0]+pairs_list[0]+pairs_list[1])
                    pairs_list = pairs_list[2:]
            if len(pairs_list) >= len(trio_list):   #三带二
                if trio_list != []:
                    for i in range(len(trio_list)):
                        cards_list2.remove(pairs_list[i])
                        cards_list2[cards_list2.index(trio_list[i])] = sort_cards(trio_list[i]+pairs_list[i])
            return cards_list1,cards_list2

        if type(actions_candy) is tuple:
            trio_flag = [x for x in actions_candy[1] if self.cardstype(x) in ['trio','trio_chain_2','trio_chain_3']]
            if trio_flag != []:
                actions_candy_new = []
                cards_list1,cards_list2 = change_actions_candy(actions_candy[1])
                actions_candy_new.append((len(cards_list1),cards_list1))
                actions_candy_new.append((len(cards_list2),cards_list2))
        elif type(actions_candy) is list:
            actions_candy_new = []
            for x in actions_candy:
                trio_flag = [i for i in x[1] if self.cardstype(i) in ['trio','trio_chain_2','trio_chain_3']]
                if trio_flag != []:
                    cards_list1,cards_list2 = change_actions_candy(x[1])
                    actions_candy_new.append((len(cards_list1),cards_list1))
                    actions_candy_new.append((len(cards_list2),cards_list2))
        if trio_flag != []:
            return actions_candy_new
        else:
            return actions_candy

    def get_actions_candy(self,cards):
        def append_act():
            while player_cards!=[]:
                act = self.list_candidate(act_type_list,player_cards)
                mark = len(max(act, key=len, default=''))
                for y in act:
                    if len(y)==mark:
                        candy_list.append(y)
                        for j in y:
                            player_cards.remove(j)
                        break
                act.clear()
        player_cards = cards.copy()
        acts = game.list_candidate(player_cards)
        # act_types = set([self.cardstype(i) for i in acts])
        acts_rm = []
        act_type_list = []
        for i in acts:
            act_type = self.cardstype(i)
            if act_type not in ['trio_solo_chain_2','trio_solo_chain_3','trio_solo_chain_4','trio_solo_chain_5','four_two_solo','four_two_pair','trio_pair_chain_2','trio_pair_chain_3','trio_pair_chain_4',]:
                act_type_list.append(act_type)
            else:
                acts_rm.append(i)
        for x in acts_rm:
            acts.remove(x)
        act_type_list = list(set(act_type_list))
        acts = [x for x in acts if len(x)>=4]
        candy_list = []
        if acts==[]:        #没有大于4的动作，最多三不带
            append_act()
            trio_num = len([i for i in candy_list if self.cardstype(i)=='trio'])
            actions_candy = (len(candy_list)-trio_num,candy_list)
        else:               
            len_mark = len(player_cards)
            actions_candy = []
            for i in acts:
                candy_list.append(i)
                for z in i:
                    try:
                        player_cards.remove(z)
                    except:
                        continue
                append_act()
                trio_num = len([i for i in candy_list if self.cardstype(i)=='trio'])
                trio_chain_2_num = len([i for i in candy_list if self.cardstype(i)=='trio_chain_2'])
                trio_chain_3_num = len([i for i in candy_list if self.cardstype(i)=='trio_chain_3'])
                bomb_num = len([i for i in candy_list if self.cardstype(i)=='bomb'])
                act_count = len(candy_list)-trio_num-2*trio_chain_2_num-3*trio_chain_3_num-2*bomb_num
                if act_count < len_mark:
                    len_mark = act_count
                    actions_candy.clear()
                    actions_candy.append((len_mark,candy_list))
                elif act_count == len_mark:
                    actions_candy.append((len_mark,candy_list))
                candy_list = []        
                player_cards = cards.copy()
        # print(actions_candy)
        actions_candy = self.update_actions_candy(actions_candy)
        if type(actions_candy) is not tuple:
            act_len = [i[0] for i in actions_candy]
            if len(set(act_len)) > 1:
                act_len = min(set(act_len))
                actions_candy = [i for i in actions_candy if i[0]==act_len]
        # print(actions_candy)
        return actions_candy

    def rule_stradge(self,action,actions,actions_candy):
        def chai_pai(i,a_candy):
            if i == ['2'] and ['CJ'] not in a_candy and ['BJ'] not in a_candy:  #没王拆2
                if ['2','2'] in a_candy:
                    return i
                else:
                    for j in a_candy:
                        if j.count('2') >= 3:
                            return i
            elif i == ['2','2']:            #拆成对2
                for j in a_candy:
                    if j.count('2') >= 3:
                        return i
            elif i in [['BJ'],['CJ']] and ['BJ','CJ'] in a_candy:       #拆双王
                return i
            action = ['PASS']
            return action
        for i in actions:
            if type(actions_candy) is tuple:
                if i in actions_candy[1]:
                    return i
            elif type(actions_candy) is list:
                for x in actions_candy:
                    if i in x[1]:
                        return i                
        action = ['PASS']
        if action == ['PASS']:
            for i in actions:
                if type(actions_candy) is tuple:
                    if i not in actions_candy[1] and i in [['BJ'],['CJ'],['2'],['2','2']]:
                        action = chai_pai(i,actions_candy[1])
                        return action
                elif type(actions_candy) is list:
                    for x in actions_candy:
                        if i not in x[1] and i in [['BJ'],['CJ'],['2'],['2','2']]:
                            action = chai_pai(i,x[1])
                            return action   
        return action

    def deal_recv(self,client_data,actions_candy):
        player_cards,record = self.change_data(client_data)
        actions_candy = self.get_actions_candy(player_cards)
        state = game.get_observation(record)
        real_player_cards = self.get_cards(player_cards)
        real_player_cards = [Card.new(x) for x in real_player_cards]
        player = self.get_player(record[-1][0]) if record != [] else players[0]
        act_mark = self.get_mark(record)
        acted = act_mark[1]
        if acted != None:
            acted = [Card.rank_int_to_str(Card.new(i)) for i in acted]
        print(act_mark[0],acted,player)
        actions = game.get_actions(act_mark,player,real_player_cards,actions_candy)
        if act_mark[0] == players[1] and player == players[2] and (acted in [['CJ'],['BJ'],['2'],['A'],['A','A'],['2','2']] or self.cardstype(acted) not in ['solo','pair']):
            if (type(actions_candy) is tuple and len(actions_candy[1]) > 3) or (type(actions_candy) is list and len(actions_candy[0][1]) > 3):
                action = ['PASS']
            else:
                action = self.rule_stradge(actions[0],actions,actions_candy)
        elif act_mark[0] == players[2] and player == players[1] and (acted in [['CJ'],['BJ'],['2'],['A'],['A','A'],['2','2']] or self.cardstype(acted) not in ['solo','pair']):
            if (type(actions_candy) is tuple and len(actions_candy[1]) > 3) or (type(actions_candy) is list and len(actions_candy[0][1]) > 3):
                action = ['PASS']
            else:
                action = self.rule_stradge(actions[0],actions,actions_candy)
        else:
            if record == []:
                action = RL_1.choose_action(state,actions,game.action_space)
            elif record[-1][0] == players[0]: #地主下家出牌
                action = RL_2.choose_action(state,actions,game.action_space)
            elif record[-1][0] == players[1]: #地主上家出牌
                action = RL_3.choose_action(state,actions,game.action_space)
            elif record[-1][0] == players[2]:   #地主出牌
                action = RL_1.choose_action(state,actions,game.action_space)
            # print(action,actions)
            action = self.rule_stradge(action,actions,actions_candy)
            if act_mark[0] == player:           #主动出牌
                if type(actions_candy) is tuple:
                    action = actions_candy[1][0]
                    if (action.count('2') >= 2 and len(actions_candy[1]) > 2) or self.cardstype(action) in ['bomb','rocket'] or (len(actions_candy[1]) == 3 and actions_candy[1][2] in [['CJ'],['BJ'],['2']] and self.cardstype(actions_candy[1][1]) == 'solo'):
                        action = actions_candy[1][1]
                elif type(actions_candy) is list:
                    action = actions_candy[0][1][0]
                    if (action.count('2') >= 2 and len(actions_candy[0][1]) > 2) or self.cardstype(action) in ['bomb','rocket']:
                        action = actions_candy[0][1][1]
            elif act_mark[0] in ['player2','player3'] and act_mark[0] != player and player != players[0] and (self.cardstype(action) in ['bomb','rocket'] or action in [['CJ'],['BJ'],['A','A'],['2','2']]):     #让队友先出
                if type(actions_candy) is tuple and len(actions_candy[1]) > 3:
                    action = ['PASS']
                elif type(actions_candy) is list and len(actions_candy[0][1]) > 3:
                    action = ['PASS']
            elif act_mark[0] == 'player1' and acted not in [['BJ'],['2'],['K', 'K'],['A', 'A']] and player == 'player2' and action in [['CJ'],['2', '2']]:        #让队友出牌
                if type(actions_candy) is tuple and len(actions_candy[1]) > 3:
                    action = ['PASS']
                elif type(actions_candy) is list and len(actions_candy[0][1]) > 3:
                    action = ['PASS']
            elif act_mark[0] != player and self.cardstype(action) in ['bomb','rocket']:        #炸弹选择时机
                if type(actions_candy) is tuple and len(actions_candy[1]) > 4:
                    action = ['PASS']
                elif type(actions_candy) is list and len(actions_candy[0][1]) > 4:
                    action = ['PASS']
            actions.clear()
        return action,actions_candy

    def handle(self):
        address,pid = self.client_address
        print('%s connected!'%address)
        # last_cards = []
        actions_candy = []
        while True:     # 利用一个死循环，保持和客户端的通信状态
            client_data = self.request.recv(80960).decode()
            start_time = time.time()
            action,actions_candy = self.deal_recv(client_data,actions_candy)
            print(action)
            if action == ['PASS']:
                self.request.sendall(str(action).encode())
            else:
                card_type = self.cardstype(action)
                self.request.sendall(str((action,card_type)).encode())
            end_time = time.time()
            print(end_time-start_time)

if __name__ == "__main__":
    ADDR = ('127.0.0.1',8888)
    server = ThreadingTCPServer(ADDR,StradgeServer)  #参数为监听地址和已建立连接的处理类
    print('listening')
    server.serve_forever()  #监听，建立好TCP连接后，为该连接创建新的socket和线程，并由处理类中的handle方法处理






















 



