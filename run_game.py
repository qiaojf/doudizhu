
# from logging import exception
from keras.models import load_model
import numpy as np
# from tensorflow.python.keras.backend import print_tensor

from doudizhu import Card
from doudizhu.engine import Doudizhu,sort_cards
from poke import Game_env

#玩家列表
players = ['player1','player2','player3']

card_type = Doudizhu.CARD_TYPE
STR_RANKS = '3-4-5-6-7-8-9-10-J-Q-K-A-2-BJ-CJ'.split('-')
INT_RANKS = range(1,16)
CHAR_RANK_TO_INT_RANK = dict(zip(STR_RANKS, INT_RANKS))
game = Game_env()

model1 = load_model('./Model_last/player1.h5')
model2 = load_model('./Model_last/player2.h5')
model3 = load_model('./Model_last/player3.h5')

class GameProcess:

    def cardstype(self,cards):
        if cards == None or cards in [['PASS'],['yaobuqi']]:
            return None
        else:
            ok,act_type = Doudizhu.check_card_type(cards)
            return act_type[0][0] 

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
            single_list,pairs_list,trio_list,trio_2_list,trio_3_list,bomb_list = [],[],[],[],[],[]
            cards_list1 = cards_list
            cards_list2 = cards_list.copy()
            # print(cards_list1,cards_list2)
            for i in cards_list:
                if self.cardstype(i) == 'solo' and i not in [['BJ'],['CJ']]:
                    single_list.append(i)
                elif self.cardstype(i) == 'pair' and i not in [['2','2'],['A','A']]:
                    pairs_list.append(i)
                elif self.cardstype(i) == 'trio':
                    trio_list.append(i)
                elif self.cardstype(i) == 'trio_chain_2':
                    trio_2_list.append(i)
                elif self.cardstype(i) == 'trio_chain_3':
                    trio_3_list.append(i)
                elif self.cardstype(i) == 'bomb':
                    bomb_list.append(i)
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
                    single_list = single_list[len(trio_list):] 
            if len(single_list) >= 2:
                if bomb_list != []:
                    cards_list1.remove(single_list[0])
                    cards_list1.remove(single_list[1])
                    cards_list1[cards_list1.index(bomb_list[0])] = sort_cards(bomb_list[0]+single_list[0]+single_list[1])
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
                    pairs_list = pairs_list[len(trio_list):]
            if len(pairs_list) >= 2:
                if bomb_list != []:
                    cards_list2.remove(pairs_list[0])
                    cards_list2.remove(pairs_list[1])
                    cards_list2[cards_list2.index(bomb_list[0])] = sort_cards(bomb_list[0]+pairs_list[0]+pairs_list[1])
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
            if act_type not in ['trio_solo','trio_pair','four_two_solo','trio_solo_chain_2','trio_solo_chain_3','trio_solo_chain_4','trio_solo_chain_5','four_two_pair','trio_pair_chain_2','trio_pair_chain_3','trio_pair_chain_4','trio_chain_4','trio_chain_5','trio_chain_6']:
                act_type_list.append(act_type)
            else:
                acts_rm.append(i)
        for x in acts_rm:
            acts.remove(x)
        act_type_list = list(set(act_type_list))
        acts = [x for x in acts if len(x)>=4]
        candy_list = []
        if acts==[]:        #没有大于4的动作
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
                act_count = len(candy_list)-trio_num-2*trio_chain_2_num-3*trio_chain_3_num
                act_count = act_count-2 if bomb_num > 0 else act_count
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

    # def rule_stradge(self,action,actions,actions_candy):
    #     def chai_pai(i,a_candy):
    #         if i == ['2'] and ['CJ'] not in a_candy and ['BJ'] not in a_candy:  #没王拆2
    #             if ['2','2'] in a_candy:
    #                 return i
    #             else:
    #                 for j in a_candy:
    #                     if j.count('2') >= 3:
    #                         return i
    #         elif i == ['2','2']:            #拆成对2
    #             for j in a_candy:
    #                 if j.count('2') >= 3:
    #                     return i
    #         elif i in [['BJ'],['CJ']] and ['BJ','CJ'] in a_candy:       #拆双王
    #             return i
    #         action = ['PASS']
    #         return action

    #     for i in actions:
    #         if type(actions_candy) is tuple:
    #             if i in actions_candy[1]:
    #                 return i
    #         elif type(actions_candy) is list:
    #             for x in actions_candy:
    #                 if i in x[1]:
    #                     return i                
    #     action = ['PASS']
    #     if action == ['PASS']:
    #         for i in actions:
    #             if type(actions_candy) is tuple:
    #                 if i not in actions_candy[1] and i in [['BJ'],['CJ'],['2'],['2','2']]:
    #                     action = chai_pai(i,actions_candy[1])
    #                     return action
    #             elif type(actions_candy) is list:
    #                 for x in actions_candy:
    #                     if i not in x[1] and i in [['BJ'],['CJ'],['2'],['2','2']]:
    #                         action = chai_pai(i,x[1])
    #                         return action   
    #     return action

    def get_action(self,new_cards,actions,actions_candy_len):
        cards = new_cards.copy()
        action_list =[]
        action = ['PASS']
        for i in actions:
            if i not in [['PASS'],['yaobuqi']]:
                for j in i:
                    cards.remove(j)
                new_candy = self.get_actions_candy(cards)
                new_candy_len = new_candy[0] if type(new_candy) is tuple else new_candy[0][0]
                if new_candy_len <= actions_candy_len:
                    action_list.append((new_candy_len,i))
                cards = new_cards.copy()
        if action_list != []:
            mark = action_list[0][0]
            action = action_list[0][1]
            for i in action_list:
                if i[0] < mark:
                    mark = i[0]
                    action = i[1]
        return action

    def get_action_list(self,actions_candy):
        new_actions = []
        if type(actions_candy) is tuple:
            new_actions = actions_candy[1] 
        else:
            for i in actions_candy:
                for j in i[1]:
                    if j not in new_actions:
                        new_actions.append(j)
        return new_actions

    def game_process(self):
        win_count = 0
        #游戏循环
        for i_episode in range(1,501):
            game_over = False
            act_mark = ('player1',None)
            game = Game_env()
            record = []
            print('游戏开始！')
            round = 1
            while True:
                player,player_pokes,player_real_pokes = game.get_playerinfo(round)
                player_cards = [Card.rank_int_to_str(i) for i in player_pokes]
                state = game.get_observation(player,record,player_cards)
                acted = act_mark[1]
                if acted != None:
                    acted = [Card.rank_int_to_str(Card.new(i)) for i in acted]
                actions_candy = self.get_actions_candy(player_cards)
                new_cards = player_cards.copy()
                # print(new_cards)
                actions_candy_len = actions_candy[0] if type(actions_candy) is tuple else actions_candy[0][0]
                actions = game.get_actions(act_mark,player,player_pokes,actions_candy)
                # print(actions)
                #=================================让队友出牌============================================
                if act_mark[0] in ['player2','player3'] and player in ['player2','player3'] and act_mark[0] != player and (acted in [['CJ'],['BJ'],['2'],['A'],['A','A'],['2','2']] or self.cardstype(acted) not in ['solo','pair']):
                    if actions_candy_len > 3:
                        action = ['PASS']
                    else:
                        action = self.get_action(new_cards,actions,actions_candy_len)
                        if self.cardstype(action) in ['bomb','rocket']:
                            action = ['PASS']
                else:
                #=================================AI给出出牌============================================
                    observation = np.reshape(state,(-1,384))
                    # print(observation[0,369:])
                    if player == 'player1':
                        action = np.argmax(model1.predict(observation), axis=-1)
                    elif player == 'player2':
                        action = np.argmax(model2.predict(observation), axis=-1)
                    elif player == 'player3':
                        action = np.argmax(model3.predict(observation), axis=-1)
                    action = game.action_space[action[0][0]]
                    candy = actions_candy[1] if type(actions_candy) is tuple else actions_candy[0][1]
                    candy = sorted(candy,key = lambda i:len(i),reverse=True)
                    # print(candy)
                    act_solo = [i for i in candy if self.cardstype(i)=='solo']
                    act_pair = [i for i in candy if self.cardstype(i)=='pair']
                    act_bomb = [i for i in candy if self.cardstype(i) in ['bomb','rocket']]
                    act_list = [i for i in candy if self.cardstype(i) not in ['solo','bomb','rocket']]
                    # if len(act_solo)>0:
                    #     print(observation[0,(369+CHAR_RANK_TO_INT_RANK[act_solo[-1][0]]):])
                    #     print(all(observation[0,(369+CHAR_RANK_TO_INT_RANK[act_solo[-1][0]]):] == 0) ==1)
                    # if len(act_pair)>0:
                    #     print(observation[0,(369+CHAR_RANK_TO_INT_RANK[act_pair[-1][0]]):])
                    #     print(all((observation[0,(369+CHAR_RANK_TO_INT_RANK[act_pair[-1][0]]):]) < 2) == 1)
                    #=================================被动出牌============================================
                    if act_mark[0] != player:   
                        new_actions = self.get_action_list(actions_candy)
                        if action not in new_actions or action not in actions:
                            action = self.get_action(new_cards,actions,actions_candy_len)
                        if act_mark[0] in ['player2','player3'] and player != players[0] and (self.cardstype(action) in ['bomb','rocket'] or action in [['CJ'],['BJ'],['A','A'],['2','2']]):     #让队友先出
                            if actions_candy_len > 3:   #大于三手让队友
                                action = ['PASS']
                        elif act_mark[0] == 'player1' and acted not in [['BJ'],['2'],['K', 'K'],['A', 'A']] and player == 'player2' and action in [['CJ'],['2', '2']]:        #让队友出牌
                            if actions_candy_len > 3:
                                action = ['PASS']
                        if self.cardstype(action) in ['bomb','rocket']:        #炸弹选择时机
                            if actions_candy_len > 4:
                                action = ['PASS']
                            if act_mark[0] in ['player2','player3'] and player in ['player2','player3']:   #大于三手让队友
                                action = ['PASS']
                            elif player == 'player1' and actions_candy_len > 3:    
                                action = ['PASS']
                            if act_mark[0] == 'player1' and len(act_solo) < 2 and int(observation[0,0]) == 1: #地主一张出炸 
                                if len(act_bomb)>0:
                                    action = act_bomb[0] if len(act_bomb)>0 else action
                        if int(observation[0,160]) == 1 and player == 'player2':  #队友一张出炸
                            action = act_bomb[0] if len(act_bomb)>0 else action
                        elif (int(observation[0,160]) == 1 or int(observation[0,80]) == 1) and player == 'player1' and self.cardstype(acted) == 'solo':
                            if len(act_solo) > 0:
                                action = act_solo[-1] if act_solo[-1] in actions else action
                    else:           
                    #=================================主动出牌============================================
                        for x in range(3):
                            for i in range(len(candy)):
                                if (candy[i].count('2') >= 2  or self.cardstype(candy[i]) in ['bomb','rocket']) and len(candy) > 2:
                                    candy.append(candy[i])
                                    candy.remove(candy[i])
                                    break
                        action = candy[0]
                        if len(act_solo) >= 2 and ['CJ'] in act_solo:
                            action = act_solo[0]
                        elif len(act_pair) >= 2 and ['2', '2'] in act_pair:
                            action = act_pair[0]
                        if int(observation[0,160]) == 1 and player == 'player2':   #队友一张，给队友顺牌
                            action = self.list_candidate(['solo'],player_cards)[0]
                        elif (int(observation[0,160]) == 1 or int(observation[0,80]) == 1) and player == 'player1':
                            if len(act_list) > 0: 
                                action = act_list[0] 
                            else:
                                if len(act_solo) > 0:
                                    act_solo[-1]
                        if len(candy) == 2 and act_solo != []:
                            action = act_solo[-1] if all(observation[0,(369+CHAR_RANK_TO_INT_RANK[act_solo[-1][0]]):] == 0) == 1 else action
                        if len(candy) == 2 and act_pair != []:
                            action = act_pair[-1] if all(observation[0,(369+CHAR_RANK_TO_INT_RANK[act_pair[-1][0]]):] < 2) == 1 else action
                    #==================================地主只有一张，地主上家出大牌====================================
                    if int(observation[0,0]) == 1 and player == 'player3':
                        if act_mark[0] == player:
                            if len(act_list) > 0: 
                                action = act_list[0] 
                            else:
                                if len(act_solo) > 0:
                                    act_solo[-1]
                        else:
                            if self.cardstype(acted) == 'solo' and len(act_solo) > 0:
                                action = act_solo[-1] if act_solo[-1] in actions else action
                    #======================================得到最终出牌================================================
                if actions[0] == ['yaobuqi']:
                    action = ['yaobuqi']
                actions.clear()
                # print(player,action)
                if action in [['PASS'],['yaobuqi']]:
                    record.append((player,action))
                else:
                    real_action,player_real_pokes,player_pokes = game.get_real_action(action,player_real_pokes,player_pokes)
                    act_mark = (player,real_action)
                    record.append((player,action))
                if len(player_real_pokes) == 0:         #游戏结束
                    game_over = True
                    winner = record[-1][0]
                    if winner in ['player2','player3']:
                        win_count += 1
                    win_rate = win_count/i_episode 
                    print('本局游戏结束，{}首先出完手牌'.format(player))
                    with open('./records/%s.txt'%player,'a',encoding="utf-8") as f:
                        f.write(str(record)+'\n')
                    print('i_episode:',i_episode,'win_rate:','%6f'%(win_rate))
                    if game_over:
                        break
                round += 1
        return win_rate,i_episode

if __name__ == "__main__":
    a = GameProcess()
    win_rate = 0.5
    while 0.25 < win_rate < 0.75:
        # try:
            win_rate,i_episode = a.game_process()
        # except Exception as e:
        #     with open('./records/error.txt','a',encoding="utf-8") as f:
        #         f.write(str(e)+'\n')

















