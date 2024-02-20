import os
import tensorflow as tf
import numpy as np
from tensorflow import keras
from keras.models import load_model

class PolicyGradient:
    def __init__(
        self,
        n_actions,
        n_features,
        learning_rate=0.01,
        reward_decay=0.95
    ):
        self.n_actions = n_actions
        self.n_features = n_features
        self.lr = learning_rate
        self.gamma = reward_decay
        
        #PG的memory不是利用一个数组存放的数据。而是利用了三个列表分别存储observation， action， reward
        self.ep_obs, self.ep_as, self.ep_rs =[],[],[]
        # self.pg_net = load_model('./Model_last/%s.h5'%winner)
        # self._build_net()  #这里相当于是把pg_net也定义了,也定义了all_acts
        
    # def make_model(self):
    #     #建立网络
    #     tf_obs = tf.keras.layers.Input(shape=(self.n_features,), name='observation')
    #     x = tf.keras.layers.Dense(128, activation='tanh', name='fc1')(tf_obs)
    #     x = tf.keras.layers.Dense(256, activation='tanh', name='fc2')(x)
    #     all_acts = tf.keras.layers.Dense(self.n_actions, name='fc3')(x)  #输出中间结果
    #     all_acts_prob = tf.keras.layers.Softmax()(all_acts)
    #     pg_net = tf.keras.Model(inputs=tf_obs, outputs=[all_acts_prob, all_acts]) #PG_net返回两个值，一个是最终，一个是上一层
        
    #     return pg_net
        
    # def _build_net(self):
    #     '''建立策略网络，不是值网络了！'''
    #     self.pg_net = self.make_model()
        #优化器
        # self.optimizer = tf.keras.optimizers.Adam(learning_rate=self.lr)
        # self.pg_net.compile(loss='categorical_crossentropy',
        #     optimizer=self.optimizer,
        #     metrics=['accuracy'])
 
    def choose_action(self, observation):
        '''根据observation来选择动作'''
        # 输入一个状态到网络，得到这个状态下，几个动作对应的被选中的概率。[1, n_actions]
        #由于返回两个值，第二个用占位符
        prob_weights, _ = self.pg_net(np.expand_dims(observation, axis=0))  #输入需要给observation添加一个维度,s输出转成np
        prob_weights = prob_weights.numpy()

        action = np.random.choice(range(prob_weights.shape[1]), p=prob_weights.ravel())  #展开这个概率数组，按照概率对动作进行选择，选出一个动作！
                #比如有10个动作，那么这个是0,1,2...9  #没有输入选几个默认选一个  #概率也有10个
        return action
    
    def store_transition(self, game,record):
        player_cards = []
        '''存储三个列表'''
        winner = record[-1][0]
        records = [i for i in record if i[0]==winner and i[1] not in [['PASS'],['yaobuqi']]]
        for i in records:
            for j in i[1]:
                player_cards.append(j)
        record = [i for i in record if i[1] !=['yaobuqi']]
        for i in record:
            if i[0] == winner:
                if i[1] not in game.action_space:
                    break
                else:
                    reward = game.get_reward(i[1])
                    observation = game.get_observation(record[:record.index(i)],player_cards)
                    self.ep_obs.append(observation)  #s列表
                    self.ep_as.append(game.action_space.index(i[1]))   #a列表
                    self.ep_rs.append(float(reward))   #r列表
        
    def learn(self,model,winner):
        '''学习'''
        optimizer = tf.keras.optimizers.Adam(learning_rate=self.lr)
        x_train = np.array(self.ep_obs)
        y_train = keras.utils.to_categorical(self.ep_as,num_classes=self.n_actions)
        model.fit(x_train,y_train,epochs=3)
        discounted_ep_rs_norm = self._discount_and_norm_rewards()  #返回了折扣之后的r数组
        
        # 训练,在这里应该直接输入实体变量
        with tf.GradientTape() as tape:
            _, all_act = model(np.vstack(self.ep_obs))
            #损失函数之前写错了。tf.nn.sparse_softmax_cross_entropy_with_logits并不是keras.losses里的Sparse损失！
            neg_log_prob = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=all_act, labels=np.array(self.ep_as)) 
            #计算损失
            self.loss = tf.reduce_mean(neg_log_prob * discounted_ep_rs_norm)  #reward guided loss
        
        #计算梯度
        gradients = tape.gradient(self.loss, model.trainable_variables)
        #优化器优化梯度
        optimizer.apply_gradients(zip(gradients, model.trainable_variables))
        
        self.ep_obs, self.ep_as, self.ep_rs = [],[],[]    #重置 episode data
        model.save('./Model_last/%s.h5'%winner)
        return discounted_ep_rs_norm   #返回一下reward的值
              
        
    def _discount_and_norm_rewards(self):
        '''折扣rewards,并且归一化rewards'''
        #折扣rewards
        discounted_ep_rs = np.zeros_like(self.ep_rs)
        running_add = 0
        for t in reversed(range(0, len(self.ep_rs))):
            running_add = running_add * self.gamma + self.ep_rs[t]
            discounted_ep_rs[t] = running_add
        
        #归一化rewards
        discounted_ep_rs -= np.mean(discounted_ep_rs)
        discounted_ep_rs /= np.std(discounted_ep_rs)
        return discounted_ep_rs









