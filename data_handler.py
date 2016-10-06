
import struct

class DataHandler:

    def __init__(self, socket_id):
        self.socket_id = socket_id

    def __get_format(self, data_format):
        return "<" + "".join(data_format)

    def receive(self, info, data_format):
        return struct.unpack(self.__get_format(data_format), info)[1:]

    def send(self, info, data_format, client_map):
        message, *info_bundle = info
        data_bundle = struct.pack(
            self.__get_format(data_format),
            *[message.value, *info_bundle])
        for client_id, client in client_map.items():
            if client_id != self.socket_id:
                client.sendall(data_bundle)
