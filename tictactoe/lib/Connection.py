import socket
from lib.Segment import Segment

class Connection:
    def __init__(self, ip : str, port : int):
        # Initialize UDP socket
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))

    def send(self, msg : Segment, dest : ("ip", "port")):
        # Send single segment into destination
        self.socket.sendto(msg.get_bytes(), dest)

    def listen_single_segment(self) -> Segment:
        # Listen single UDP datagram within timeout and convert into segment
        msg, address = self.socket.recvfrom(32768)
        segment = Segment()
        segment.set_from_bytes(msg)
        if not segment.valid_checksum():
            raise Exception("Invalid checksum")
        return segment, address

    def close_socket(self):
        # Release UDP socket
        self.socket.close()

    def set_timeout(self, timeout : float):
        # Set timeout for UDP socket
        self.socket.settimeout(timeout)
