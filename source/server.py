import socket
import threading
from common import send_msg, recv_msg
import time
import configparser
import sys

class Server:
    number_of_clients = 0

    def __init__(self, port=None):
        self.msg_size = 1024
        host, port, listens = self._get_from_settings(port)
        self.host = ""
        self.port = port
        self.listens = listens
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def _get_from_settings(self, port):
        config = configparser.ConfigParser()
        config.read('setting.ini')

        if "DEFAULT" in config.sections():
            raise AttributeError("Setting.ini doesnt have [DEFAULT] section")
        elif not "host" in config["DEFAULT"]:
            raise AttributeError("Setting.ini doesnt have host")
        elif port is None and not "port" in config["DEFAULT"]:
            raise AttributeError("Setting.ini doesnt have port")
        elif not "listens" in config["DEFAULT"]:
            raise AttributeError("Setting.ini doesnt have listens")

        if port is None:
            port = config["DEFAULT"]["port"]

        host = config["DEFAULT"]["host"]
        listens = config["DEFAULT"]["listens"]
        return host, int(port), int(listens)


    def accept_socket(self):
        Server.number_of_clients += 1
        return self.sock.accept()

    def close_client(self, client):
        Server.number_of_clients -= 1
        client.close()

    def listen(self):
        self.sock.listen(self.listens)

        while True:
            client, address = self.accept_socket()
            client.settimeout(60)

            ct = threading.Thread(target = self.listen_client, args = (client, address))
            ct.start()

    def listen_client(self, client, address):

        while True:
            request = self._get_request(client)

            if request:
                response = self._generate_responce(request)
                send_msg(client, response)

            else:
                self.close_client(client)
                return False

    def _generate_responce(self, request):
        command = request.split()[0]
        argument = " ".join(request.split()[1:])

        if command == "ping":
            return self._get_ping(argument)

        elif command == "status":
            return self._get_status()

        elif command == "lower":
            return self._get_lower(argument)

        return "bad request"


    def _get_request(self, client):
        return recv_msg(client)

    def _get_ping(self, argument):
        if argument == "*":
            return "+"
        return "bad request"

    def _get_status(self):
        unixtime = int(time.time())
        connections = Server.number_of_clients
        return "time: {t}, connections: {c}".format(t=unixtime, 
                                                    c=connections)
    def _get_lower(self, argument):
        return argument.lower()

if __name__ == "__main__":
    
    if len(sys.argv) == 2:
        port = sys.argv[1]
    else:
        port = None

    Server(port).listen()
