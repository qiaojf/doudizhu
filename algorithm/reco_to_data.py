
import os
import time

files = os.listdir('./trained_qqgame')
print(files)

def write_data(player,data):
    with open('./records/%s.txt'%player,'a',encoding='utf-8') as f:
        f.write(data+'\n')

for file in files:
    with open('./trained_qqgame/%s'%file,'r',encoding='utf-8') as f:
        while 1:
            record = f.readline().strip()
            if not record:
                break
            record = eval(record.strip(','))
            write_data(record[-1][0],str(record))




