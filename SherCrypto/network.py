import sys
import socket

class Client:
    def __init__(self):
        # This creates an INET (IPv4), STREAMing (TCP) socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.AF_INET is the address family, and socket.SOCK_STREAM is the

    def connect(self, host, port):
        # This connects a socket to a host
        self.s.connect((host, port))   # We can now use this socket to connect to python.org on port 80.

    def mysend(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.s.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myreceive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.s.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunk)

    def close(self):
        self.s.close()

class Server:
    def __init__(self):
        # This creates an INET (IPv4), STREAMing (TCP) socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to a public host (host will be: "tim" in this case), and a well-known port (just using 80 for now)
        self.serverSocket.bind((socket.gethostname()), 80)
        # Become a server socket
        self.serversocket.listen(1)

def createServer():
    Server serversocket
    # accept a connection from outside
    (clientsocket, address) = serversocket.accept()
    # now we want to do something with the client server
