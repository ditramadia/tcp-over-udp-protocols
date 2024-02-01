import sys
import json

from lib.Connection import Connection
import lib.Segment as segment
from lib.Segment import Segment
from lib.Display import Display

class Server:
    # Construct server
    def __init__(self):
        self.ip = "localhost"
        self.port = None
        self.connection = None
        self.clients = [] # (ip, port, username)

    # Starting server connection
    def request_state(self, ip, port, id, username, board, status):
        while True:
            self.connection.set_timeout(1)
            try:
                # Initialize request
                req = Segment()
                sign = 'Requesting state'
                data = {
                    "sign": sign,
                    "id": id,
                    "username": username,
                    "board": board,
                    "game_status": status,
                    }
                req.data['payload'] = json.dumps(data).encode('utf-8')
                req.update_checksum()

                # Send request
                client_addr = (ip, port)
                self.connection.send(req, client_addr)

                # Listen ACK
                ack, addr = self.connection.listen_single_segment()
                if ack.get_flag().get_flag_bytes() != segment.ACK_FLAG:
                    raise Exception
                else:
                    break
            
            except Exception as e:
                print(e)
    def start_server(self, port):
        try:
            self.port = port
            self.connection = Connection(self.ip, self.port)
        except Exception as e:
            print(".", end="")
        
    # Listen for connection request
    def listen_connection_request(self):
        try:
            # Listen for request
            req, addr = self.connection.listen_single_segment()

            # Receive connection request
            if req.data['payload']:
                received_data = req.data['payload']
                parsed_data = json.loads(received_data.decode('utf-8'))
                if (parsed_data['sign']) == 'Requesting connection':
                    self.clients.append({
                        'ip': addr[0],
                        'port': addr[1],
                        'username': parsed_data['username']
                    })

            # Send ACK
            ack = Segment()                 
            ack.set_flag(["ack"])
            self.connection.send(ack, addr)
            
        except Exception as e:
            print(".", end = "") # Do nothing
    
    def perform_three_way_handshake(self, ip, port):
        while True:
            self.connection.set_timeout(1)
            try:
                client_addr = (ip, port)

                # Send SYN
                syn = Segment()
                syn.set_flag(['syn'])
                self.connection.send(syn, client_addr)

                # Listening for SYN-ACK
                syn_ack, addr = self.connection.listen_single_segment()
                syn_ack_flags = syn_ack.get_flag()

                # Send ACK
                if syn_ack_flags.syn and syn_ack_flags.ack and not syn_ack_flags.fin:
                    ack = Segment()
                    ack.set_flag(['ack'])
                    self.connection.send(ack, client_addr)
                    break
                
                else:
                    raise Exception
                
            except Exception as e:
                print(".", end="")

        

    def listen_move_update(self):
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
                    if parsed_data['sign'] == 'Requesting move update':
                        ack = Segment()
                        ack.set_flag(['ack'])
                        self.connection.send(ack, addr)
                        return parsed_data['cell']
                    break

            except Exception as e:
               print(".", end="")
        
    def request_result(self, id, board):
        while True:
            self.connection.set_timeout(1)
            try:
                # Initialize request
                req = Segment()
                sign = 'Requesting result'
                data = {
                    "sign": sign,
                    "id": id,
                    "board": board,
                    }
                req.data['payload'] = json.dumps(data).encode('utf-8')
                req.update_checksum()

                for client in self.clients:
                    # Send request
                    client_addr = (client['ip'], client['port'])
                    self.connection.send(req, client_addr)

                    # Listen ACK
                    ack, addr = self.connection.listen_single_segment()
                    if ack.get_flag().get_flag_bytes() != segment.ACK_FLAG:
                        sys.exit(1)
                break

            except Exception as e:
                print(".", end="")