from __init__ import *


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = msg.encode("utf-8")
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    raw_msglen = raw_msglen.encode("utf-8")
    msglen = struct.unpack('>I', raw_msglen)[0]
    return recvall(sock, msglen)

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data.decode('utf-8')