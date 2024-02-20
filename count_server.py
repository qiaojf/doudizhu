
from socketserver import BaseRequestHandler,ThreadingTCPServer
import struct
import os
import shutil
import hashlib

class CountServer(BaseRequestHandler):
    def handle(self):
        dirpath = './imgs/'.encode('utf-8')
        address,pid = self.client_address
        print('%s connected!'%address)
        dirpath = ('./imgs/%s/' %address).encode('utf-8')
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        # else:
        #     shutil.rmtree(dirpath)
        #     os.mkdir(dirpath)
        while True:
            # try:
                fileinfo_size = struct.calcsize('64sl64s')
                buf = self.request.recv(fileinfo_size)
                if buf:
                    filename, filesize, img_md5 = struct.unpack('64sl64s', buf)
                    fn = filename.strip(str.encode('\00'))
                    img_md5 = img_md5.strip(str.encode('\00')).decode()
                    new_filename = os.path.join(dirpath, str.encode('new_') + fn)
                    with open(new_filename, 'wb') as fp:
                        recvd_size = 0
                        recv_data = b''
                        while recvd_size < int(filesize):
                                data = self.request.recv(512)
                                recvd_size += len(data)
                                recv_data += data
                        pic_md5 = hashlib.md5(recv_data).hexdigest()
                        if img_md5 == pic_md5:
                            fp.write(recv_data)
                            print('%s send over'% new_filename)
                            self.request.sendall('file send over!'.encode('utf-8'))
                        else:
                            print('%s send wrong!'% new_filename)
                            self.request.sendall('file send wrong!'.encode('utf-8'))
            # except:
            #     continue

if __name__ == "__main__":
    ADDR = ('10.21.8.67',5555)
    server = ThreadingTCPServer(ADDR,CountServer)  #参数为监听地址和已建立连接的处理类
    print('listening')
    server.serve_forever() 




