
from keras.layers import Embedding
from keras.layers import LSTM
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
print(len(x))
# x_test = np.array(x[int(len(x)*0.8):])
# x_test = scaler.fit_transform(x_test)
# y_test = keras.utils.to_categorical(y[int(len(x)*0.8):],num_classes=CLASSES)

new_x_pr = []
x_pr = x[:int(len(x)*0.25)]
x_pr = scaler.fit_transform(x_pr)
midd = []
for i in range(0,len(x_pr)):
    midd.append(x_pr[i])
    new_x_pr.append(midd)
    midd = []
new_x_pr = np.array(new_x_pr)
y_pr = keras.utils.to_categorical(y[:int(len(y)*0.25)],num_classes=CLASSES)


new_x_train = []
x_train = x[int(len(x)*0.25):]
x_train = scaler.fit_transform(x_train)
mid = []
for i in range(0,len(x_train)):
    mid.append(x_train[i])
    new_x_train.append(mid)
    mid = []
new_x_train = np.array(new_x_train)
y_train = keras.utils.to_categorical(y[int(len(y)*0.25):],num_classes=CLASSES)

def lstm_model():
    data_dim = len(x[0])
    # print(data_dim)
    timesteps = 1
    num_classes = 6801

    # 期望输入数据尺寸: (batch_size, timesteps, data_dim)
    model = Sequential()
    model.add(LSTM(64, return_sequences=True,
                   input_shape=(timesteps, data_dim)))  
    model.add(LSTM(128, return_sequences=True,dropout=0.2))  
    model.add(LSTM(192,dropout=0.2)) 
    model.add(Dense(num_classes, activation='softmax'))

    model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])
    return model

# model = lstm_model()
model = load_model('./Model_last/%s_lstm.h5'%player)

model.fit(new_x_train, y_train,
          batch_size=128, epochs=200,
          validation_data=(new_x_pr, y_pr))

# score = model.evaluate(new_x_pr, y_pr, batch_size=128)

model.save('./Model_last/%s_lstm.h5'%player) 

