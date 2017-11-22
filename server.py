import json
from json import JSONDecodeError
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Lock, Thread, Barrier
from uuid import uuid4
from guardian.camera import Camera as Cam

HOST = '127.0.0.1'
PORT = 2550


class Server:

    def __init__(self, host=HOST, port=PORT):
        self.server_tcp = socket(family=AF_INET, type=SOCK_STREAM)
        self.server_udp = socket(family=AF_INET, type=SOCK_DGRAM)
        self.link = (host, port)
        self.server_tcp.bind(self.link)
        self.server_udp.bind(self.link)
        self.server_tcp.listen(10)
        self.server_udp.listen(10)
        self.clients = dict()
        self.exit = False
        self.manage = Thread(target=self.connection_manager,
                             daemon=False, name="manager", args=())
        self.manage.start()
        pass

    def connection_manager(self):

        print("Server is running...")

        while not self.exit:
            new_sock, address = self.server_tcp.accept()
            new_client = Client(new_sock, False)
            listening_client = Thread(target=self.client_listener, args=(new_client,), daemon=True,
                                      name="{}:{}".format(*address))
            print("Listening client at adress: {}".format(
                listening_client.getName()))
            try:
                listening_client.start()
            except ConnectionResetError:
                print("Conection lost...")

    def client_listener(self, client):

        while not client.exit:
            rules_len = int.from_bytes(client.recv(4), byteorder="big")
            try:
                rules = json.loads(client.tcp.recv(rules_len).decode('utf-8'))
            except JSONDecodeError:
                self.reset_protocol(client)
                continue
            with client.lock:
                pass

    def reset_protocol(self, client):
        with client.lock:
            instructions = json.dumps(
                {"rule": "reset"}).encode(encoding="utf-8")
            rules_len = len(instructions).to_bytes(4, byteorder="big")
            client.tcp.send(rules_len)
            client.tcp.send(instructions)
            pass


class Client:

    def __init__(self, link1, link2):
        self.tcp = link1
        #self.udp = link2
        self.lock = Lock()
        self.barrier = Barrier()
        self.exit = False
