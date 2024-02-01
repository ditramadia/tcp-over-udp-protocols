import struct

# Constants 
SYN_FLAG = 0b00000010
ACK_FLAG = 0b00010000
FIN_FLAG = 0b00000001

class SegmentFlag:
    def __init__(self, flag : bytes):
        self.syn = False
        self.ack = False
        self.fin = False

        if flag & SYN_FLAG:
            self.syn = True
        if flag & ACK_FLAG:
            self.ack = True
        if flag & FIN_FLAG:
            self.fin = True

    def get_flag_bytes(self) -> bytes:
        flag = 0b00000000
        if self.syn:
            flag |= SYN_FLAG
        if self.ack:
            flag |= ACK_FLAG
        if self.fin:
            flag |= FIN_FLAG

        return flag

class Segment:
    # -- Internal Function --
    def __init__(self):
        # header
        self.header = {}
        self.header["flag"] = SegmentFlag(0b00000000)
        self.header["seq_num"] = 0
        self.header["ack_num"] = 0
        self.header["checksum"] = 0

        # data
        self.data = {}
        self.data["payload"] = b''

    def __str__(self):
        output = ""
        output += f"{'Sequence number':24} | {self.header['seq_num']}\n"
        output += f"{'Acknowledgement number':24} | {self.header['ack_num']}\n"
        output += f"{'Flag':24} | {self.header['flag']}\n"
        output += f"{'Checksum':24} | {self.header['checksum']}\n"
        output += f"{'Payload':24} | {self.data['payload']}\n"

        return output

    def calculate_checksum(self) -> int:
        # checksum using 8 bits one complement
        data_bytes = self.get_bytes_no_checksum()

        # convert data_bytes into binary string, wih array of 16 bits
        data_binary = []
        for byte in data_bytes:
            data_binary.append(bin(byte)[2:].zfill(8))
        
        # calculate checksum
        sum = 0
        for i in range(0, len(data_binary), 2):
            if i == len(data_binary) - 1:
                sum += int(data_binary[i], 2)
            else:
                sum += int(data_binary[i] + data_binary[i+1], 2)

        return sum % 65536
        
    def update_checksum(self):
        self.header['checksum'] = self.calculate_checksum()


    # -- Setter --
    def set_header(self, header : dict):
        self.header = header
        self.update_checksum()

    def set_seq_num(self, seq_number : int):
        # Set sequence number
        self.header['seq_num'] = seq_number
        self.update_checksum()

    def set_ack_num(self, ack_number : int):
        # Set acknowledgement number
        self.header['ack_num'] = ack_number
        self.update_checksum()

    def set_payload(self, payload : bytes):
        self.data['payload'] = payload
        self.update_checksum()

    def set_flag(self, flag_list : list):
        initial_flag = 0b00000000
        for flag in flag_list:
            if flag == 'syn':
                initial_flag |= SYN_FLAG
            elif flag == 'ack':
                initial_flag |= ACK_FLAG
            elif flag == 'fin':
                initial_flag |= FIN_FLAG
        self.header['flag'] = SegmentFlag(initial_flag)
        self.update_checksum()


    # -- Getter --
    def get_flag(self) -> SegmentFlag:
        return self.header['flag']

    def get_header(self) -> dict:
        return self.header
    
    def get_ack_num(self) -> int:
        return self.header['ack_num']

    def get_payload(self) -> bytes:
        return self.data['payload']


    # -- Marshalling --
    def set_from_bytes(self, src : bytes):
        # From pure bytes, unpack() and set into python variable
        header_bytes = src[:12]
        header_values = struct.unpack('iibbh', header_bytes)
        header = {
            'seq_num': header_values[0],
            'ack_num': header_values[1],
            'flag': SegmentFlag(header_values[2]),
            'checksum': header_values[4]
        }
        self.header = header
        self.data['payload'] = src[12:]
        self.update_checksum()

    def get_bytes_no_checksum(self) -> bytes:
        # Convert this object to pure bytes
        header_bytes = struct.pack('iibb', self.header['seq_num'], self.header['ack_num'], self.header['flag'].get_flag_bytes(), 0b00000000)
        return header_bytes + self.data['payload']

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        header_bytes = struct.pack('iibbH', self.header['seq_num'], self.header['ack_num'], self.header['flag'].get_flag_bytes(), 0b00000000, self.header['checksum'])
        return header_bytes + self.data['payload']

    # -- Checksum --
    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object 
        return self.calculate_checksum() == self.header['checksum']
    