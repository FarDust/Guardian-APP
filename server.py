import json
from json import JSONDecodeError
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Lock, Thread, Barrier
from uuid import uuid4
from guardian import Camera as Cam

__all__ = ['Server']

HOST = '127.0.0.1'
PORT = 2550


class Server:

    def __init__(self, host=HOST, port=PORT, camera=Cam()):
        self.camera = camera
        self.server_tcp = socket(family=AF_INET, type=SOCK_STREAM)
        self.server_udp = socket(family=AF_INET, type=SOCK_DGRAM)
        self.link = (host, port)
        self.server_tcp.bind(self.link)
        self.server_udp.bind(self.link)
        self.server_tcp.listen(10)
        self.clients = dict()
        self.exit = False
        self.manage = Thread(target=self.connection_manager,
                             daemon=False, name="manager", args=())

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
                if "rule" in rules:
                    if rules["rules"] == "getFrame":
                        frame_to_send = self.camera.video_frame
                        request_uuid = uuid4()
                        response = json.loads(
                            {"rule": "init", "type": "image", "content_len": len(frame_to_send), "uuid": request_uuid}).encode('utf8')
                        client.tcp.send(
                            len(response).to_bytes(4, byteorder='big'))
                        client.tcp.send(response)
                        minion = Thread(target=self.send_frame, args=(
                            client, frame_to_send), daemon=true)
                        minion.start()

    @staticmethod
    def send_frame(client, to_send):
        with client.exclusive_lock:
            total_to_send = len(to_send)
            index = 0
            buffer_size = 2048
            while index < total_to_send:
                with client.lock:
                    bytes_to_send = to_send[index:min(
                        total_to_send - index + 1, index + 2048)]
                    sent = len(bytes_to_send)
                    index += sent
                    response = {"rule": "download",
                                "type": "image", "sent": sent}
                    encoded_response = json.dumps(response).endode('utf-8')
                    response_len = len(response).to_bytes(4, byteorder="big")
                    client.tcp.send(response_len + response + bytes_to_send)

    @staticmethod
    def reset_protocol(client):
        with client.lock:
            instructions = json.dumps(
                {"rule": "reset"}).encode(encoding="utf-8")
            rules_len = len(instructions).to_bytes(4, byteorder="big")
            client.tcp.send(rules_len)
            client.tcp.send(instructions)

    def __enter__(self):
        print("starting Theread...")
        self.manage.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server_udp.detach()
        self.server_tcp.detach()
        self.exit = True
        print("exit secuence complete")


class Client:

    def __init__(self, link1, link2):
        self.tcp = link1
        self.udp = link2
        self.lock = Lock()
        self.exclusive_lock = Lock()
        self.barrier = Barrier()
        self.exit = False


if __name__ == "__main__":
    with Cam() as render:
        server = Server(camera=render)
        with server:
            last = ""
            while True:
                current = server.camera.current
                if last != current:
                    print(current)
                last = current
