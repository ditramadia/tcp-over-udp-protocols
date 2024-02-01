import sys
import time

import lib.connection
import lib.segment as segment
from lib.segment import Segment

from lib.utils.logger import Logger

WINDOW_SIZE = 4

class Client:
    def __init__(self):
        # Initialize client
        self.ip = "localhost"
        self.port = None
        self.server_addr = None
        self.connection = None
        self.file_path = None
        self.file_buffer = []

        # Utility
        self.logger = Logger()

    def connect_to_server(self, client_port, server_port, file_path):
        # Initialize client
        self.port = client_port
        self.server_addr = ("localhost", 12345)
        self.file_path = file_path
        self.connection = lib.connection.Connection(self.ip, self.port)
        
        # Connect to server
        try:
            # Initialize segment
            req = Segment()
            req.header['seq_num'] = 1
            req.header['ack_num'] = 2
            req.set_flag(["syn"])
            req.data['payload'] = b"Pen connect bang"
            req.update_checksum()

            # Send segment
            self.logger.log_info(1, f"Sending request to server...")
            self.connection.send(req, self.server_addr)
            self.logger.log_info(0, "Request sent successfully")
        
        except Exception as e:
            # self.logger.log_err(0, e)
            sys.exit(1)

    def three_way_handshake(self):
        # Three Way Handshake, client-side
        while True:
            self.logger.log_info(1, "Handshaking with server...")

            # Listening SYN
            self.connection.set_timeout(999)
            try: 
                self.logger.log_info(0, "Listening SYN")
                syn, addr = self.connection.listen_single_segment()
                self.logger.log_info(0, "SYN received")
                syn_flag = syn.get_flag()
                syn_flag = syn_flag.get_flag_bytes()
                if syn_flag == segment.SYN_FLAG:
                    syn_ack = Segment()
                    syn_ack.set_flag(["syn", "ack"])
                    break
            except Exception as e:
                self.logger.log_err(0, e)
        while True:
            # Send SYN-ACK
            self.logger.log_info(0, "Sending SYN-ACK")
            self.connection.send(syn_ack, self.server_addr)
            self.logger.log_info(0, "SYN-ACK sent")
            
            # Listening ACK
            self.connection.set_timeout(1)
            try:
                self.logger.log_info(0, "Listening ACK")
                ack, addr = self.connection.listen_single_segment()
                self.logger.log_info(0, "ACK received")
                ack_flag = ack.get_flag()
                ack_flag = ack_flag.get_flag_bytes()
                if ack_flag == segment.ACK_FLAG:
                    self.logger.log_info(1, "Handshake successful")
                    return True
                else:
                    self.logger.log_err(0, "Handshake failed")
            except Exception as e:
                self.logger.log_err(0, e)

    def listen_file_transfer(self):
        # File transfer, client-side
        self.logger.log_info(1, "Listening for file transfer...")
        seq_num = 0
        current_seq_num = 0
        sm = WINDOW_SIZE - 1
        while True :
            self.connection.set_timeout(99999)
            try:
                # Listening segment
                self.logger.log_info(0, "Listening segment")
                segment, addr = self.connection.listen_single_segment()
                
                segment_flag = segment.get_flag()
                seq_num = segment.get_header()['seq_num']
                print ("current_seq_num", current_seq_num)
                print ("seq_num", seq_num)
                self.logger.log_info(0, "Segment" + str(seq_num) + " received")
                if segment_flag.fin:
                    self.logger.log_info(0, "File Received")
                    file = b''.join(self.file_buffer)
                    with open(self.file_path, 'wb') as f:
                        f.write(file)
                    timeout = time.time() + 4
                    ack_received = False
                    while time.time() < timeout:
                        ack = Segment()
                        ack.set_flag(["fin", "ack"])
                        self.connection.send(ack, self.server_addr)
                        self.logger.log_info(0, "FIN-ACK sent")
                        self.connection.set_timeout(1)
                        try:
                            ack, addr = self.connection.listen_single_segment()
                            ack_flag = ack.get_flag()
                            if ack_flag.ack:
                                self.logger.log_info(0, "ACK received")
                                self.logger.log_info(0, "Closing connection...")
                                self.connection.close_socket()
                                ack_received = True
                                break
                        except Exception as e:
                            self.logger.log_err(0, e)
                    if not ack_received:
                        self.logger.log_info(0, "ACK not received")
                        self.logger.log_info(0, "Closing connection...")
                    break
                if seq_num == current_seq_num:
                    self.file_buffer.append(segment.get_payload())
                    ack = Segment()
                    ack.set_flag(["ack"])
                    ack.set_ack_num(seq_num)
                    self.connection.send(ack, self.server_addr)
                    self.logger.log_info(0, "ACK" + str(current_seq_num) + " sent")
                    current_seq_num += 1
                else:
                    if (current_seq_num - seq_num >= sm):
                        ack = Segment()
                        ack.set_flag(["ack"])
                        ack.set_ack_num(seq_num)
                        self.connection.send(ack, self.server_addr)
                        self.logger.log_info(0, "Segment" + str(seq_num) + " is out of window")
                    else:
                        self.logger.log_info(0, "Segment" + str(seq_num) + " refused")
            except Exception as e:
                # self.logger.log_err(0, e)
                break

if __name__ == '__main__':
    # Argument validation
    if len(sys.argv) != 4:
        print("Usage: python client.py <client port> <server port> <file path>")
        sys.exit(1)
    client_port = int(sys.argv[1])
    server_port = int(sys.argv[2])
    file_path = sys.argv[3]

    # Client main
    client = Client()
    client.connect_to_server(client_port, server_port, file_path)
    connection = client.connection
    ack, addr = connection.listen_single_segment()
    client.three_way_handshake()
    client.listen_file_transfer()

    sys.exit(0)
