
import random
import os
from keras.models import load_model
import numpy as np

from doudizhu import Card
from doudizhu.engine import Doudizhu, cards2str
from poke import Game_env

from RL_brain import PolicyGradient
#玩家列表
players = ['player1','player2','player3']

card_type = Doudizhu.CARD_TYPE
game = Game_env()

model1 = load_model('./Model_last/player1.h5')
model2 = load_model('./Model_last/player2.h5')
model3 = load_model('./Model_last/player3.h5')

# RLPG = PolicyGradient(n_actions=9914,n_features=66)
models = [model1,model2,model3]
def cardstype(cards):
    if cards == None or cards == ['PASS']:
        return None
    else:
        ok,act_type = Doudizhu.check_card_type(cards)
        return act_type[0][0] 

def store_transition(record):
    winner = record[-1][0]
    transition1,transition2,transition3 = [],[],[]
    for i in record:
        if i[0] == players[0]:
            if i[1] not in game.action_space:
                break
            else:
                reward = game.get_reward(i[1])
                observation = game.get_observation(record[:record.index(i)])
                # observation_ = game.get_observation(record[:record.index(i)+1])
                if players[0] == winner:
                    transition1.append((observation,game.action_space.index(i[1]),reward*2))
                else:
                    transition1.append((observation,game.action_space.index(i[1]),-0.5*reward))
        elif i[0] == players[1]:
            if i[1] not in game.action_space:
                break
            else:
                reward = game.get_reward(i[1])
                observation = game.get_observation(record[:record.index(i)])
                # observation_ = game.get_observation(record[:record.index(i)+1])
                if players[1] == winner:
                    transition2.append((observation,game.action_space.index(i[1]),reward*2))
                elif players[2] == winner:
                    transition2.append((observation,game.action_space.index(i[1]),reward))
                elif players[0] == winner:
                    transition2.append((observation,game.action_space.index(i[1]),-0.5*reward))
        elif i[0] == players[2]:
            if i[1] not in game.action_space:
                break
            else:
                reward = game.get_reward(i[1])
                observation = game.get_observation(record[:record.index(i)])
                observation_ = game.get_observation(record[:record.index(i)+1])
                if players[2] == winner:
                    transition3.append((observation,game.action_space.index(i[1]),reward*2,observation_))
                elif players[1] == winner:
                    transition3.append((observation,game.action_space.index(i[1]),reward,observation_))
                elif players[0] == winner:
                    transition3.append((observation,game.action_space.index(i[1]),-0.5*reward,observation_))
    # with open("./records/player1_record.txt","a",encoding="utf-8") as f1:
    #     transition1 = str(transition1).replace('array([','[',len(transition1))
    #     transition1 = transition1.replace('])',']',len(transition1))
    #     f1.write(transition1+',')
    #     # f1.write('\r\n')
    # with open("./records/player2_record.txt","a",encoding="utf-8") as f2:
    #     transition2 = str(transition2).replace('array([','[',len(transition2))
    #     transition2 = transition2.replace('])',']',len(transition2))
    #     f2.write(transition2+',')
    #     # f2.write('\r\n')
    # with open("./records/player3_record.txt","a",encoding="utf-8") as f3:
    #     transition3 = str(transition3).replace('array([','[',2*len(transition3))
    #     transition3 = transition3.replace('])',']',2*len(transition3))
    #     f3.write(transition3+',')
    #     # f3.write('\r\n')

def get_act(act):
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

def load_train():
    with open("./records/player1_record.txt","r",encoding="utf-8") as f1:
        f1 = eval(f1.read())
        for trainsitions in f1:
            for trainsition in trainsitions:
                RL_1.store_transition(np.array(trainsition[0]),trainsition[1],trainsition[2])
            RL_1.learn(1)
        RL_1.save_model('player1',str(0.5),1000)
    with open("./records/player2_record.txt","r",encoding="utf-8") as f2:
        f2 = eval(f2.read())
        for trainsitions in f2:
            for trainsition in trainsitions:
                RL_2.store_transition(np.array(trainsition[0]),trainsition[1],trainsition[2])
            RL_2.learn(1)
        RL_2.save_model('player2',str(0.5),1000)
    with open("./records/player3_record.txt","r",encoding="utf-8") as f3:
        f3 = eval(f3.read())
        for trainsitions in f3:
            for trainsition in trainsitions:
                RL_p.store_transition(np.array(trainsition[0]),trainsition[1],trainsition[2],np.array(trainsition[3]))
            RL_p.learn()
            if (f3.index(trainsitions)+1)%50==0:
                RL_p.learn()
        RL_p.save_model('player3',str(0.5),1000)

def list_candidate(type_list,cards_str):  #候选牌列表
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

def get_actions_candy(cards):
    def append_act():
        while player_cards!=[]:
            act = list_candidate(act_type_list,player_cards)
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
    acts_rm = []
    act_type_list = []
    for i in acts:
        act_type = cardstype(i)
        if act_type not in ['trio_solo_chain_3','trio_solo_chain_4','trio_solo_chain_5','four_two_solo','four_two_pair','trio_pair_chain_3','trio_pair_chain_4',]:
            act_type_list.append(act_type)
        else:
            acts_rm.append(i)
    for x in acts_rm:
        acts.remove(x)
    act_type_list = list(set(act_type_list))
    acts = [x for x in acts if len(x)>=4]
    candy_list = []
    if acts==[]:
        append_act()
        actions_candy = (len(candy_list),candy_list)
        return actions_candy
    else:
        len_mark = 17
        actions_candy = []
        for i in acts:
            candy_list.append(i)
            for z in i:
                player_cards.remove(z)
            append_act()
            act_count = len(candy_list)
            if act_count < len_mark:
                len_mark = act_count
                actions_candy.clear()
                actions_candy.append((len_mark,candy_list))
            elif act_count == len_mark:
                actions_candy.append((len_mark,candy_list))
            candy_list = []        
            player_cards = cards.copy()
    return actions_candy

def rule_stradge(action,actions,actions_candy):
    def update_action(a_candy,action,actions):
        for i in actions:
            if action == i:
                if action in a_candy:
                    return action
            else:
                if i in a_candy:
                    action = i
                    return action
                elif i == ['2'] and ['CJ'] not in a_candy and ['BJ'] not in a_candy:
                    if ['2','2'] in a_candy:
                        action = i
                    else:
                        for j in a_candy:
                            if j.count('2') == 3:
                                action = i
                    return action
                elif i == ['2','2']:
                    for j in a_candy:
                            if j.count('2') == 3:
                                action = i
                                return action
        return ['PASS']
    if type(actions_candy) is tuple:
        action = update_action(actions_candy[1],action,actions)
    elif type(actions_candy) is list:
        for x in actions_candy:
            action = update_action(x[1],action,actions)
            if action != ['PASS']:
                break
    # print(action,actions_candy)
    return action

def game_process():
    win_count = 0
    step = 1 
    #游戏循环
    for i_episode in range(1,501):
        game_over = False
        act_mark = ('player1',None)
        game = Game_env()
        record = []
        print('游戏开始！')
        state = np.zeros(16*3+2+16)
        round = 1
        while True:
            a = []
            player,player_pokes,player_real_pokes = game.get_playerinfo(round)
            player_cards = [Card.rank_int_to_str(i) for i in player_pokes]
            state = game.get_observation(record,player_cards)
            a.append(state)
            acted = act_mark[1]
            if acted != None:
                acted = [Card.rank_int_to_str(Card.new(i)) for i in acted]
            # ok,act_type = Doudizhu.check_card_type(acted)
            actions_candy = get_actions_candy(player_cards)
            actions = game.get_actions(act_mark,player,player_pokes,actions_candy)
            # print(actions)
            observation = np.array(a)
            if player == 'player1':
                action = np.argmax(model1.predict(observation), axis=-1)
                # print(action)
            elif player == 'player2':
                action = np.argmax(model2.predict(observation), axis=-1)
                # print(action)
            elif player == 'player3':
                action = np.argmax(model3.predict(observation), axis=-1)
                # print(action)
            action = game.action_space[action[0][0]]
            if action not in actions:
                action = rule_stradge(action,actions,actions_candy)
            if actions[0] == ['PASS']:
                action = ['yaobuqi']
            actions.clear()
            # print('real:%s'%action)
            if action == ['PASS'] or action == ['yaobuqi']:
                pass
            else:
                real_action,player_real_pokes,player_pokes = game.get_real_action(action,player_real_pokes,player_pokes)
                act_mark = (player,real_action)
            record.append((player,action))
            if len(player_real_pokes) == 0:         #游戏结束
                game_over = True
                winner = record[-1][0]
                # store_transition(record)
                if winner in ['player2','player3']:
                    win_count += 1
                win_rate = win_count/i_episode 
                print('本局游戏结束，{}首先出完手牌'.format(player))
                with open('./records/%s.txt'%player,'a',encoding="utf-8") as f:
                    f.write(str(record)+'\n')
                print('i_episode:',i_episode,'win_rate:','%6f'%(win_rate))
                if game_over:
                    # RLPG.store_transition(game,record)
                    # player_model = models[players.index(record[-1][0])]
                    # RLPG.learn(player_model,record[-1][0])
                    break
            round += 1
            step += 1
            # if step % 500 == 0:
            #     load_train()
            #     for j in os.listdir('./records'):
            #         os.remove('./records/%s' %j)
    return win_rate,i_episode

if __name__ == "__main__":
    win_rate = 0.5
    while 0.25 < win_rate < 0.75:
        try:
            win_rate,i_episode = game_process()
        except:
            print('wrong!')

















