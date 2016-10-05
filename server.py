import socketserver
import struct

from messages import Message

client_map = {}

class ThreadedTCPHandler(socketserver.BaseRequestHandler):
    daemon_threads = True
    allow_reuse_address = True

    def setup(self):
        self.handlers = {
            Message.CONNECT: self.connect_handler,
            Message.BULLET: self.bullet_handler,
            Message.MOVE: self.move_handler,
            Message.DISCONNECT: self.disconnect_handler
        }

    def connect_handler(self, data):
        print("Client Connected")

    def disconnect_handler(self, data):
        print("Client Disconnected")
        send_data = struct.pack('<bH', *[101, self.socket_id])
        for client_id, client in client_map.items():
            if client_id != self.socket_id:
                client.sendall(send_data)

    def bullet_handler(self, data):
        print("SHOTS FIRED!!!")
        _, oX, oY, tX, tY = struct.unpack('<bHHHH', data)
        send_data = struct.pack('<bHHHHH', *[4, self.socket_id, oX, oY, tX, tY])
        for client_id, client in client_map.items():
            if client_id != self.socket_id:
                client.sendall(send_data)

    def move_handler(self, data):
        global client_map
        request = self.request
        _, x, y = struct.unpack('<bHH', data)
        print(self.socket_id, x, y)
        send_data = struct.pack('<bHHH', *[1, self.socket_id, x, y])
        for client_id, client in client_map.items():
            if client_id != self.socket_id:
                client.sendall(send_data)

    def handle(self):
        global client_map
        _, self.socket_id = self.request.getpeername()
        client_map[self.socket_id] = self.request
        while True:
            try:
                data = self.request.recv(255).strip()
                message = Message(bytearray(data)[0])
                if message:
                    self.handlers[message](data)
            except (ConnectionResetError, IndexError) as e:
                self.handlers[Message.DISCONNECT](data)
                break


    def finish(self):
        global client_map
        del client_map[self.socket_id]

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    print("Starting Server on port {}".format(PORT))
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPHandler)
    server.serve_forever()
