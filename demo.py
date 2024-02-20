
import time
import socket,sys
import os
import struct
import hashlib


def count_client():
    while True:
        ADDR =('10.21.8.67',5555)
        reg_sock = socket.socket()
        reg_sock.connect(ADDR)
        print('reg server connected success')
        while True:
            # try:
                pic_path = './tmp/'
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
            # except:
            #     reg_sock.close()
            #     break

if __name__ == '__main__':
    count_client()
