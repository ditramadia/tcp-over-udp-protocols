import sys
import json

from lib.Connection import Connection
import lib.Segment as segment
from lib.Segment import Segment
from lib.Display import Display

class Client:
    # Construct client
    def __init__(self):
        self.ip = "localhost"
        self.port = None
        self.server_addr = None
        self.name = ''
        self.connection = None
    
    # Connect client to server
    def connect_to_server(self, client_port, server_port, username):
        # Initialize client
        self.port = client_port
        self.server_addr = ("localhost", server_port)
        self.connection = Connection(self.ip, self.port)

        # Connect to server
        try:

            # Initialize request
            req = Segment()
            req.set_flag(['syn'])
            sign = 'Requesting connection'
            data = {
                "sign": sign,
                "username": username
            }
            req.data['payload'] = json.dumps(data).encode('utf-8')
            req.update_checksum()

            # Send request
            self.connection.send(req, self.server_addr)

            # Listen for ACK
            ack, addr = self.connection.listen_single_segment()
            ack_flag = ack.get_flag()
            ack_flag = ack_flag.get_flag_bytes()
            if ack_flag != segment.ACK_FLAG:
                raise Exception
        
        except Exception as e:
            print(".", end="")
        
    def perform_three_way_handshake(self):
        while True:
            self.connection.set_timeout(1)
            try:
                # Listening SYN
                syn, addr = self.connection.listen_single_segment()
                syn_flag = syn.get_flag()
                syn_flag = syn_flag.get_flag_bytes()

                # Send SYN-ACK
                if syn_flag == segment.SYN_FLAG:
                    syn_ack = Segment()
                    syn_ack.set_flag(["syn", "ack"])
                    self.connection.send(syn_ack, self.server_addr)
                else:
                    raise Exception
                
                # Listening ACK
                ack, addr = self.connection.listen_single_segment()
                if ack.get_flag().get_flag_bytes() != segment.ACK_FLAG:
                    raise Exception
                else:
                    break
                
            except Exception as e:
                print(".", end="")
    
    # Listening request
    def listen_state(self):
        while True:
            self.connection.set_timeout(1)
            try:
                # Listen for request
                req, addr = self.connection.listen_single_segment()

                # Receive request from server
                if req.data['payload']:
                    received_data = req.data['payload']
                    parsed_data = json.loads(received_data.decode('utf-8'))
                    
                    # Send ACK
                    if parsed_data['sign'] == 'Requesting state' or parsed_data['sign'] == 'Requesting result':
                        ack = Segment()
                        ack.set_flag(['ack'])
                        self.connection.send(ack, addr)

                        return parsed_data
                    
                    else:
                        raise Exception

            except Exception as e:
                print(".", end="") # Do nothing
    
    def request_move_update(self, cell):
        while True:
            self.connection.set_timeout(1)
            try:
                # Initialize request
                req = Segment()
                sign = 'Requesting move update'
                data = {
                    "sign": sign,
                    "cell": cell
                }
                req.data['payload'] = json.dumps(data).encode('utf-8')
                req.update_checksum()
                # Send request
                self.connection.send(req, self.server_addr)
        

                # Listen ACK
                ack, addr = self.connection.listen_single_segment()
                if ack.get_flag().get_flag_bytes() != segment.ACK_FLAG:
                    raise Exception
                else :
                    break

            except Exception as e:
                print(".", end="")