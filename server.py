import sys
import multiprocessing
import time
import threading
from typing import Dict, List, Tuple

from lib.connection import Connection
from lib.segment import Segment
from lib.segment import SegmentFlag

from lib.utils.logger import Logger

WINDOW_SIZE = 4

class Server:
    def __init__(self, parallel):
        # Initialize server
        self.ip = "localhost"
        self.port = None
        self.file_path = None
        self.file_buffer = None
        self.connection = None
        self.clients = []
        self.clients_parallel: Dict[Tuple[str, int], List[Segment]] = {}
        self.parallel = parallel
        self.sleep = 1

        # Utility
        self.logger = Logger()

    def start_server(self, port, file_path):
        # Initialize server
        self.port = port
        self.file_path = file_path
        self.file_buffer = open(self.file_path, "rb").read()
        self.connection = Connection(self.ip, self.port)
        self.logger.log_info(1, f"Server running on port {self.port}")
        
        # Starting server
        try:
            if self.parallel:
                self.logger.log_info(1, "Starting server in parallel mode...")
                self.listen_for_clients_parallel()
            else:
                self.logger.log_info(1, "Starting server in normal mode...")
                self.listen_for_clients()
                self.start_file_transfer(self.clients)

            
        except Exception as e:
            # self.logger.log_err(0, e)
            print(e)
            sys.exit(1)


    def listen_for_clients(self):
        # Listening for client
        while True:
            try:
                self.logger.log_info(1, f"Listening for clients...")
                req, addr = self.connection.listen_single_segment()

                # Receive request from client
                self.logger.log_info(1, f"Request received from, {addr[0]}:{addr[1]}")
                if req.data['payload'] == b"Pen connect bang":
                    self.clients.append(addr)
                    self.logger.log_info(0, "Client connected")
                    
                # Listen more option
                command = None
                command_valid = False
                while not command_valid:
                    self.logger.log_ask(1, "Listen more? (y/n)")
                    command = input()
                    if command == "y" or command == "n" or command == "Y" or command == "N":
                        command_valid = True
                if command == "n" or command == "N":
                    break
            
            except Exception as e:
                # self.logger.log_err(0, e)
                print(e)
                break

        # Sending ACK to clients
        for client in self.clients:
            ack = Segment()
            ack.set_flag(["ack"])
            self.logger.log_info(0, "Sending ACK ...")
            self.connection.send(ack, client)
            self.logger.log_info(0, "ACK sent ...")
        
        # Print client list
        self.logger.log_info(1, "Client list:")
        i = 1
        for client in self.clients:
            self.logger.log_info(0, f"{i}. {client[0]}:{client[1]}")
            i += 1


    def listen_for_clients_parallel(self):
        # Listening for client
        while True:
            self.connection.set_timeout(15)
            try:
                client, client_address = self.connection.listen_single_segment()
                ip, port = client_address
                if (client_address not in self.clients_parallel):
                    self.logger.log_info(1, f"Request received from, {ip}:{port}")
                    self.clients_parallel[client_address] = []
                    new_transfer = threading.Thread(target=self.start_file_transfer, kwargs={"client_addr": client_address})
                    new_transfer.start()
                else:
                    # Receive request from client
                    self.clients_parallel[client_address].append(client)
            except Exception as e:
                print(e)
                    

    def start_file_transfer(self, client_addr : ("ip", "port")):
        # Handshake & file transfer for all client
        if self.parallel:
            self.logger.log_info(1, f"Starting file transfer for client {client_addr[0]}:{client_addr[1]}")
            self.three_way_handshake(client_addr)
            self.file_transfer(client_addr)
        else:
            for client in self.clients:
                self.logger.log_info(1, f"Starting file transfer for client {client[0]}:{client[1]}")
                self.three_way_handshake(client)
                self.file_transfer(client)

    def file_transfer(self, client_addr : ("ip", "port")):
        # File transfer, server-side, Send file to 1 client
        # Initialize file transfer
        limit = 2**15 - 12
        array_of_data = []
        data = self.file_buffer
        time.sleep(self.sleep)
        self.sleep += 1
        # Segment file buffer
        while len(data) > 0:
            if len(data) > limit:
                array_of_data.append(data[:limit])
                data = data[limit:]
            else:
                array_of_data.append(data)
                data = b''

        # Sending segmented file data to client
        self.logger.log_info(1, f"Sending file to client {client_addr[0]}:{client_addr[1]}")
        sn = 0
        sb = 0
        sc = len(array_of_data)
        sm = WINDOW_SIZE - 1
        while True:
            # print ("sn = " + str(sn))
            # print ("sb = " + str(sb))
            # print ("sc = " + str(sc))
            # print ("sm = " + str(sm))
            while sb <= sn <= sm and sn < sc:
                # Initialize segment
                segment = Segment()
                segment.set_seq_num(sn)
                segment.set_payload(array_of_data[sn])
                
                # Send segment
                self.logger.log_info(0, f"Sending segment {sn} to client {client_addr[0]}:{client_addr[1]}")
                self.connection.send(segment, client_addr)
                self.logger.log_info(0, f"Segment {sn} sent")
                sn += 1
                if sb + 4 == sn:
                    self.logger.log_info(0, "Waiting for ACK")
                    break        

            # Listening for ACK
            self.connection.set_timeout(1)
            try:
                if self.parallel:
                    ack, addr = self.listen_single_segment_parallel(client_addr)
                else:
                    ack, addr = self.connection.listen_single_segment()
                self.logger.log_info(0, "Listening for ACK")
                if ack.get_flag().ack and addr == client_addr:
                    self.logger.log_info(0, "ACK " + str(ack.get_ack_num()) + " received")
                    sb = ack.get_ack_num()
                    sm = sb + (WINDOW_SIZE - 1)
                    if sb + 1 == sc:
                        break
                elif ack.get_ack_num() > sb:
                    sm = (sm - sb) + ack.get_ack_num()
                    sb = ack.get_ack_num()
                else:
                    self.logger.log_err(0, "ACK not received")
                    sn = sb
            except Exception as e:
                self.logger.log_err(0, e)
                sn = sb      
            
            if sb == sc:
                break
        
        # Sending FIN
        while True:
            fin = Segment()
            fin.set_flag(["fin"])
            self.logger.log_info(0, "Sending FIN")
            self.connection.send(fin, client_addr)
            self.logger.log_info(0, "FIN sent")
            try:
                ack, addr = self.connection.listen_single_segment()
                if ack.get_flag().ack and ack.get_flag().fin:
                    ack = Segment()
                    ack.set_flag(["ack"])
                    self.logger.log_info(0, "Sending ACK")
                    self.connection.send(ack, client_addr)
                    self.logger.log_info(0, "ACK sent")
                    time.sleep(5)
                    break
                else:
                    self.logger.log_err(0, "ACK not received")
            except Exception as e:
                self.logger.log_err(0, e)

        
    def three_way_handshake(self, client_addr: ("ip", "port")) -> bool:
        # Three way handshake, server-side, 1 client
        # Send SYN
        while True:
            self.logger.log_info(1, f"Handshaking with client {client_addr[0]}:{client_addr[1]}")
            syn = Segment()
            syn.set_flag(["syn"])
            print (client_addr)
            self.logger.log_info(0, "Sending SYN")
            self.connection.send(syn, client_addr)
            self.logger.log_info(0, "SYN sent")
            # Listening SYN-ACK
            self.connection.set_timeout(1)
            try:
                self.logger.log_info(0, "Listening SYN-ACK")
                syn_ack, addr = self.connection.listen_single_segment()
                self.logger.log_info(0, "SYN-ACK received")
                syn_ack_flags = syn_ack.get_flag()
                if syn_ack_flags.syn and syn_ack_flags.ack and addr == client_addr and not syn_ack_flags.fin:
                    self.logger.log_info(0, "SYN-ACK valid")
                    # Send ACK
                    ack = Segment()
                    ack.set_flag(["ack"])
                    self.logger.log_info(0, "Sending ACK")
                    self.connection.send(ack, client_addr)
                    self.logger.log_info(0, "ACK sent")
                    self.logger.log_info(0, f"Handshake with {client_addr[0]}:{client_addr[1]} successful")
                    return True
                else:
                    self.logger.log_err(0, f"Handshake with {client_addr[0]}:{client_addr[1]} failed")
            except Exception as e:
                # self.logger.log_err(0, e)
                self.logger.log_err(0, f"Handshake with {client_addr[0]}:{client_addr[1]} failed")


    def listen_single_segment_parallel(self, client_addr: ("ip", "port")) -> Tuple[Segment, Tuple[str, int]]:
        # Listen for single segment, 1 client
        time_timeout = time.time() + 1
        while (time.time() < time_timeout):
            if len(self.clients_parallel[client_addr]) > 0:
                return (self.clients_parallel[client_addr].pop(0), client_addr)
                
    
if __name__ == '__main__':
    # Argument validation
    if len(sys.argv) != 3:
        print("Usage: python server.py <port> <file path>")
        sys.exit(1)
    port = int(sys.argv[1])
    file_path = sys.argv[2]

    # Server main
    print ("Enable parallel mode? (y/n)")
    command = input()
    if command == "y" or command == "Y":
        parallel = True
    else:
        parallel = False
    server = Server(parallel)
    server.start_server(port, file_path)

    sys.exit(0)
