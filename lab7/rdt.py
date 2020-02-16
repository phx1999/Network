from udp import UDPsocket
from socket import *
import struct
import time
import threading



# 数字转换
def ascii_to_num(message):
    key = 0
    re = 0
    num = len(message)
    while key < num:
        re = re + 256 ** (num - 1 - key) * int(message[key])
        key = key + 1
    return re

# 将信息封装为一个packet
class packet():
    def __init__(self, syn=0, fin=0, ack=0, seq=0, seq_ack=0, payload=''):
        self.syn = syn
        self.fin = fin
        self.ack = ack
        self.seq = seq
        self.seq_ack = seq_ack
        self.payload = payload
        self.len = len(payload)
        self.packet_list = [syn, fin, ack]
        self.packt_list_add_byte(self.seq, 8)
        self.packt_list_add_byte(self.seq_ack, 8)
        self.packt_list_add_byte(self.len, 8)
        self.packt_list_add_byte(0, 4)
        key = 0
        while key < len(payload):
            self.packet_list.append(ord(payload[key]))
            key = key + 1
        self.checksum = calc_checksum(self.packet_list)
        str = hex(self.checksum)
        length = str.__len__()
        str = '0' * (4 - (length - 2)) + str[2:]
        self.packet_list[15] = int(str[0:2], 16)
        self.packet_list[16] = int(str[2:4], 16)

    # 转化为 byte
    def encode(self):
        re = b''
        ooo = 0
        for message in self.packet_list:
            re += struct.pack('B', message)
            ooo += 1
        return re

    # 十进制数字转化为特定长度的十六进制
    def packt_list_add_byte(self, num, len):
        str = hex(num)
        length = str.__len__()
        str = '0' * (len - (length - 2)) + str[2:]
        key = 0
        while key < str.__len__():
            self.packet_list.append(int(str[key:key + 2], 16))
            key += 2



# 解析收到的packet
class packet_resolver():
    def __init__(self, message):
        self.checksum_list = []
        self.syn = message[0]
        self.fin = message[1]
        self.ack = message[2]
        self.seq = ascii_to_num(message[3:7])
        self.seq_ack = ascii_to_num(message[7:11])
        self.len = ascii_to_num(message[11:15])
        self.checksum = ascii_to_num(message[15:17])
        self.payload = message[17:]
        if calc_checksum(message) == 0:
            self.check = True
        else:
            self.check = False


class Socket(UDPsocket):
    def __init__(self, window_size=3, base=0, next_sequence=1, recent_seq=0, syn=0):
        super().__init__()
        self.send_socket = socket(AF_INET, SOCK_DGRAM)
        self.seq = {}
        self.seq_ack = {}
        self.message = None
        self.window_size = window_size
        self.packets = []
        self.base = base
        self.next_sequence = next_sequence
        self.recent_seq = recent_seq
        self.sender = threading.Thread(target=self.sender)
        self.receiver = threading.Thread(target=self.receiver)
        self.sender_check = False
        self.receiver_check = False
        self.syn = syn

    def connect(self):
        # send syn; receive syn, ack; send ack
        # your code here
        pass

    def accept(self):
        # receive syn; send syn, ack; receive ack
        # your code here
        pass

    def close(self):
        # send fin; receive ack; receive fin; send ack
        # your code here
        pass

    def recv(self):
        return self.recvfrom()[0]

    def recvfrom(self):
        # your code here
        while True:
            UDPsocket.setblocking(self, 1)
            reply = UDPsocket.recvfrom(self, bufsize=4096)
            if reply is None:
                continue
            else:
                try:
                    data = packet_resolver(reply[0])
                except:
                    continue
                address = reply[1]
                if data.payload is None:
                    continue
                if data.check:
                    if address not in self.seq.keys():
                        self.seq[address] = 0
                        self.seq_ack[address] = 0
                    if data.seq == self.seq_ack[address]:
                        self.seq_ack[address] = data.seq + data.len
                        re = packet(seq_ack=self.seq_ack[address]).encode()
                        UDPsocket.sendto(self, re, address)
                        print(data.payload)
                        return data.payload, address
                    else:
                        # print("not match")
                        re = packet(seq_ack=self.seq_ack[address]).encode()
                        UDPsocket.sendto(self, re, address)
                        continue
                else:
                    if address not in self.seq.keys():
                        self.seq[address] = 0
                        self.seq_ack[address] = 0
                    re = packet(seq_ack=self.seq_ack[address]).encode()
                    UDPsocket.sendto(self, re, address)
                    continue
        return


    def send(self, data):
        message = data[0]
        address = data[1]
        bytes = message.encode()
        UDPsocket.sendto(self, bytes, address)

    def sendto(self, data, address):
        if address not in self.seq.keys():
            self.seq[address] = 0
            self.seq_ack[address] = 0
        load = packet(payload=data, seq=self.recent_seq, seq_ack=self.seq_ack[address])
        self.packets.append([load, address])
        self.recent_seq += load.len

    def sender(self):
        while True:
            if self.packets.__len__() > 0:
                if self.packets.__len__() > self.window_size:
                    max = self.window_size
                else:
                    max = len(self.packets)
                for key in range(self.base, max):
                    data = self.packets[key]
                    self.send(data)
            time.sleep(2)

    def start_sender(self):
        self.sender.setDaemon(True)
        self.sender.start()

    def start_receiver(self):
        self.receiver.setDaemon(True)
        self.receiver.start()

    def receiver(self):
        while True:
            UDPsocket.setblocking(self, 0)
            try:
                response = UDPsocket.recvfrom(self, bufsize=4096)
                if response is not None:
                    message = packet_resolver(response[0])
                    if not message.check:
                        continue
                else:
                    continue
            except:
                time.sleep(0.5)
                continue
            try:
                pack = self.packets[0]
                address = response[1]
            except IndexError:
                continue
            if address not in self.seq.keys():
                self.seq[address] = 0
                self.seq_ack[address] = 0
            if message.seq_ack >= self.seq[address] + pack[0].len:
                print('\"' + str(pack[0].payload))
                self.seq[address] += pack[0].len
                self.packets.remove(pack)
                continue
            elif message.seq == self.seq_ack[address] and message.syn is 1:
                print('\"' + str(message.payload))
                self.seq_ack[address] += message.len
                continue
            else:
                time.sleep(0.5)
                continue


def calc_checksum(payload):
    sum = 0
    for byte in payload:
        sum += byte
    sum = -(sum % 256)
    return sum & 0xFF
