import socketserver
import struct
import threading

from messages import Message

client_map = {}

class ThreadedTCPHandler(socketserver.BaseRequestHandler):
    daemon_threads = True
    allow_reuse_address = True

    def setup(self):
        self.handlers = {
            Message.MOVE: self.move_handler,
        }

    def move_handler(self, data):
        global client_map
        request = self.request
        _, x, y = struct.unpack('<bHH', data)
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
            except IndexError as e:
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
