import json
import socket
from threading import Thread
from SocketServer import ThreadingMixIn

#config
TCP_IP = 'localhost'
TCP_PORT = 9001
BUFFER_SIZE = 1024
UPLOAD_FOLDER: "uploads"
ALLOWED_AUDIO_EXTENSIONS = set(['wav', 'ogg', 'mp3', ])

class ClientThread(Thread):

    def __init__(self,ip,port,sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        print(" New thread started for "+ip+":"+str(port))

    def run(self):
        filename='mytext.txt'
        f = open(filename,'rb')
        while True:
            l = f.read(BUFFER_SIZE)
            while (l):
                self.sock.send(l)
                #print('Sent ',repr(l))
                l = f.read(BUFFER_SIZE)
            if not l:
                f.close()
                self.sock.close()
                break


def is_audio_file_ext(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

def main():
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind((TCP_IP, TCP_PORT))
    threads = []

    while True:
        tcpsock.listen(5)
        print("Waiting for incoming connections...")
        (conn, (ip,port)) = tcpsock.accept()
        print('Got connection from ', (ip,port))
        newthread = ClientThread(ip,port,conn)
        newthread.start()
        threads.append(newthread)

    for t in threads:
        t.join()

"""
if file and audio_file(file.filename):
    file.save(os.path.join(config['UPLOAD_FOLDER'], filename))
"""
if __name__ == "__main__":
    main()