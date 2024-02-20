import keras
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from keras.models import load_model
from keras.layers import Activation, Dense, Dropout
from keras.models import Sequential
from keras import regularizers
import reco_to_obsv

FEATHER = 67
CLASSES = 6801
scaler = MinMaxScaler()
players = ['player1','player2','player3']
player = players[0]
file = '%s.txt'%player
x,y = reco_to_obsv.read_file(file,player)
# print(x[0])
x_test = np.array(x[int(len(x)*0.8):])
x_test = scaler.fit_transform(x_test)
y_test = keras.utils.to_categorical(y[int(len(x)*0.8):],num_classes=CLASSES)

# x_pr = np.array(x[int(len(x)*0.95):])
# y_pr = keras.utils.to_categorical(y[int(len(x)*0.95):],num_classes=CLASSES)

x_train = np.array(x[:int(len(x)*0.8)])
x_train = scaler.fit_transform(x_train)
y_train = keras.utils.to_categorical(y[:int(len(x)*0.8)],num_classes=CLASSES)

def Mlp():
    # model = Sequential()
    # model.add(Dense(128, activation='relu', input_dim=FEATHER,))
    # model.add(Dropout(0.25))
    # model.add(Dense(256, activation='relu'))
    # model.add(Dropout(0.35))
    # model.add(Dense(512, activation='relu'))
    # model.add(Dropout(0.35))
    # model.add(Dense(1024, activation='relu'))
    # model.add(Dropout(0.25))
    # model.add(Dense(CLASSES, activation='softmax'))
    # return model

# def make_model(self):
    #建立网络
    obs = tf.keras.layers.Input(shape=(FEATHER,), name='observation')
    x = tf.keras.layers.Dense(256, activation='relu', name='fc1')(obs)
    x = tf.keras.layers.Dropout(0.4)(x)
    x = tf.keras.layers.Dense(384, activation='relu', name='fc2')(x)
    x = tf.keras.layers.Dropout(0.4)(x)
    x = tf.keras.layers.Dense(512, activation='relu', name='fc3')(x)
    x = tf.keras.layers.Dropout(0.4)(x)
    x = tf.keras.layers.Dense(768, activation='relu', name='fc4')(x)
    x = tf.keras.layers.Dropout(0.4)(x)
    all_acts = tf.keras.layers.Dense(CLASSES, name='fc5')(x)  #输出中间结果
    all_acts_prob = tf.keras.layers.Softmax()(all_acts)
    mlp_net = tf.keras.Model(inputs=obs, outputs=[all_acts_prob, all_acts]) #mlp_net返回两个值，一个是最终，一个是上一层

    return mlp_net


# model = Mlp()
# model.compile(loss='categorical_crossentropy',
#         optimizer='adam',
#         metrics=['accuracy'])
# # model = load_model('./Model_last/%s.h5'%player)
# model.fit(x_train, y_train,
#         epochs=500,
#         batch_size=128)
# score = model.evaluate(x_test, y_test, batch_size=128)
# # print(np.argmax(model.predict(x_pr), axis=-1))

# model.save('./Model_last/%s.h5'%player)  



