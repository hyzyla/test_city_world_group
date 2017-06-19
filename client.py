from __init__ import *
from common import send_msg, recv_msg


class Client(QObject):

    connectionChanged = pyqtSignal()
    connectionFailed = pyqtSignal()
    connectionRefused = pyqtSignal()

    def __init__(self, port, host=None):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host if not host else socket.gethostname()                        
        self.port = port
        try:
            self.sock.connect((self.host, self.port))
            self.connected = True
        except:
            self.connected = False
            self.connectionFailed.emit()
            self.sock.close()
        self.listen()

    def sendRequest(self, request):
        send_msg(self.sock, request)
        response = recv_msg(self.sock)
        return response

    def listen(self):
        threading.Thread(target=self.listenServer).start()

    def listenServer(self):
        while True:
            try:
                time.sleep(3)
                send_msg(self.sock, "ping *")
                recv_msg(self.sock)
            except:
                if self.sock._closed:
                    return None
                self.changeStatus(connected=False)
                self.connectionRefused.emit()
                return None

    def changeStatus(self, connected):
        if self.connected == connected:
            return
        if connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                self.connected = True
                self.listen()
                self.connectionChanged.emit()
            except:
                self.connected = False
                self.connectionFailed.emit()
                return
        else:
            self.sock.close()
            self.connected = False
            self.connectionChanged.emit()
            

    def __bool__(self):
        return self.connected    

    def __repr__(self):
        return "Client({} {})".format(self.host, self.port)  

    def __str__(self):
        return self.__repr__()
