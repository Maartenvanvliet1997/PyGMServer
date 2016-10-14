import socketserver
import struct

from messages import Message
import data_handler

client_map = {}
buffer_u16 = "H"
buffer_u8 = "b"


class ThreadedTCPHandler(socketserver.BaseRequestHandler):
    daemon_threads = True
    allow_reuse_address = True

    def setup(self):
        self.handlers = {
            Message.CONNECT: self.connect_handler,
            Message.DISCONNECT: self.disconnect_handler,
            Message.BULLET: self.bullet_handler,
            Message.MOVE: self.move_handler
        }

    def connect_handler(self, data):
        print("Client Connected")

    def disconnect_handler(self, data):
        print("Client Disconnected")
        self.data_handler.send(
            [Message.DISCONNECT, self.socket_id],
            [buffer_u8, buffer_u16],
            client_map)

    def bullet_handler(self, data):
        self.__base_rebroadcast(data, Message.BULLET, 4)

    def move_handler(self, data):
        print(data, "MOVE")
        self.__base_rebroadcast(data, Message.MOVE, 2)

    def handle(self):
        global client_map
        _, self.socket_id = self.request.getpeername()
        self.data_handler = data_handler.DataHandler(self.socket_id)
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

    def __base_rebroadcast(self, data, message, size=1):
        data_bundle = self.data_handler.receive(
            data, [buffer_u8, buffer_u16 * size])
        self.data_handler.send(
            [message, self.socket_id, *data_bundle],
            [buffer_u8, buffer_u16 * (size + 1)],
            client_map)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    print("Starting Server on port {}".format(PORT))
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPHandler)
    server.serve_forever()
