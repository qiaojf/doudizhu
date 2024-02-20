
from poke import Game_env
from RL_brain1 import PolicyGradient,DQNPrioritizedReplay

import numpy as np
import random
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

gamma = 0.99  # Discount factor for past rewards
max_steps_per_episode = 20000
eps = np.finfo(np.float32).eps.item()  # Smallest number such that 1.0 + eps != 1.0
game = Game_env()

num_inputs = 59
num_actions = len(game.action_space)
num_hidden1 = 128
num_hidden2 = 256
num_hidden3 = 512

inputs = layers.Input(shape=(num_inputs,))
common1 = layers.Dense(num_hidden1, activation="relu")(inputs)
common2 = layers.Dense(num_hidden2, activation="relu")(common1)
common3 = layers.Dense(num_hidden3, activation="relu")(common2)
action = layers.Dense(num_actions, activation="softmax")(common3)
critic = layers.Dense(1)(common3)

model = keras.Model(inputs=inputs, outputs=[action, critic])

optimizer = keras.optimizers.Adam(learning_rate=0.0005)
huber_loss = keras.losses.Huber()
action_probs_history = []
critic_value_history = []
rewards_history = []
running_reward = 0
episode_count = 0

players = ['player1','player2','player3']

# RL_1 = DQNPrioritizedReplay(
#         game.n_actions, 
#         game.n_features,
#     )

# RL_2 = PolicyGradient(
#     game.n_actions, 
#     game.n_features,
#     )
# model.load_weights("my_model/actor_critic_0.34970261592715407_19000.h5")
step = 1
win_count = 0
for i_episode in range(1,20001):
    game = Game_env()
    state = np.zeros(59)
    episode_reward = 0
    game_over = False
    act_mark = ('player1',None)
    record = []
    round = 1
    bomb_count = 0
    with tf.GradientTape() as tape:
        while True:
            player,player_pokes,player_real_pokes= game.get_playerinfo(round)
            actions = game.get_actions(act_mark,player,player_pokes)
            if actions == []:
                act_cards = 'pass'
                record.append((player,act_cards))
            else:
                state = tf.convert_to_tensor(state)
                state = tf.expand_dims(state, 0)
                action_probs, critic_value = model(state)
                critic_value_history.append(critic_value[0, 0])
                if player == players[0]:
                    act_cards = np.random.choice(num_actions, p=np.squeeze(action_probs))
                    action_probs_history.append(tf.math.log(action_probs[0, act_cards]))
                elif player == players[1]:
                    act_cards = random.choice(actions)
                elif player == players[2]:
                    act_cards = random.choice(actions)
                if act_cards not in actions:
                    act_cards = random.choice(actions)
                actions.clear()
                if act_cards == 'pass':
                    record.append((player,act_cards))
                else:
                    action,player_real_pokes,player_pokes = game.get_real_action(act_cards,player_real_pokes,player_pokes)
                    act_mark = (player,action)
                    record.append((player,act_cards))
                    state_ = game.get_observation(record)
            if len(player_real_pokes) == 0:         #游戏结束
                game_over = True
                winner = record[-1][0]
                for i in record:
                    if i[0] == players[2]:
                        reward = game.get_reward(i[1])
                        if players[0] == winner:
                            reward = reward*2
                        else:
                            reward = -0.5*reward
                        rewards_history.append(reward)
                        episode_reward += reward
                if winner == players[0]:
                    win_count += 1
                win_rate = win_count/i_episode
                print('本局游戏结束，{}首先出完手牌'.format(player))
                print('i_episode:',i_episode,'win_rate:','%6f'%(win_rate))
                if game_over:
                    break
            round += 1
            state = state_
            step += 1

        # Update running reward to check condition for solving
        running_reward = 0.05 * episode_reward + (1 - 0.05) * running_reward

        returns = []
        discounted_sum = 0
        for r in rewards_history[::-1]:
            discounted_sum = r + gamma * discounted_sum
            returns.insert(0, discounted_sum)

        # Normalize
        returns = np.array(returns)
        returns = (returns - np.mean(returns)) / (np.std(returns) + eps)
        returns = returns.tolist()

        # Calculating loss values to update our network
        history = zip(action_probs_history, critic_value_history, returns)
        actor_losses = []
        critic_losses = []
        for log_prob, value, ret in history:

            diff = ret - value
            actor_losses.append(-log_prob * diff)  # actor loss

            critic_losses.append(
                huber_loss(tf.expand_dims(value, 0), tf.expand_dims(ret, 0))
            )

        # Backpropagation
        loss_value = sum(actor_losses) + sum(critic_losses)
        grads = tape.gradient(loss_value, model.trainable_variables)
        optimizer.apply_gradients(zip(grads, model.trainable_variables))

        action_probs_history.clear()
        critic_value_history.clear()
        rewards_history.clear()

    i_episode += 1
    if i_episode % 1000 == 0:
        model.save_weights("my_model/actor_critic_{:.6f}_{}.h5".format(win_rate,i_episode))
        template = "running reward: {:.2f} at episode {}"
        print(template.format(running_reward, i_episode))




















































