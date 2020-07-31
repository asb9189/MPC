import netifaces as ni
from node import Node
from ast import literal_eval
import configparser
import random
import ipaddress
import argparse
import json
import time
import sys
import base64

from socket import error as SocketError
import errno

#crypto libary
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import Base64Encoder

NUM_ROUNDS = 1

def get_ip(hostname):

    ni.ifaddresses(hostname + '-eth0')
    return ni.ifaddresses(hostname + '-eth0')[ni.AF_INET][0]['addr']

class ClientNode(Node):
    def __init__(self, host, port):
        super().__init__(False, host, port)
        self.r1_sum = 0
        self.r2_sum = 0
        self.r3_sum = 0

    def receive(self, msg):
        if msg['round'] == 0:
            self.node_id = msg['message']
            self.num_parties = msg['num_parties']
            #end of round 0 send the first real message
            if self.recv_count == 1 and self.send_count == 1:
                self.round_num += 1
                self.send_message({'round' : self.round_num, 'message' : my_message}, addr=server)
                self.recv_count = 0
                self.send_count = 0
        else:
            vals = msg['message'].split('\n')
            for num in vals[:-1]:
                #self.r1_sum += int(num) #THIS CHANGES WITH ENCRYPTION OR NOT
                self.r1_sum += decrypt(num)

            if self.recv_count == 1:
                self.round_num += 1
                if self.round_num != NUM_ROUNDS + 1:
                    self.send_message({'round' : self.round_num, 'message' : my_message}, addr = server)
                    self.recv_count = 0
                    self.send_count = 0

def decrypt(data):

    num = literal_eval(data)
    secret_message = base64.b64decode(num[0].encode('utf-8'))
    box = Box(private_key, keys[num[1]])
    msg = box.decrypt(secret_message)
    input = int.from_bytes(msg, "big")
    return input

def get_args():

    parser = argparse.ArgumentParser(description=None);
    parser.add_argument("-H", "--hostname", action="store", required=True, help="hostname");
    parser.add_argument("-P", "--ports", action="store", required=True, type=int, help="hostname");
    config = configparser.ConfigParser()
    args = parser.parse_args();

    my_ip = get_ip(args.hostname)
    my_port = 8888 #by default

    parties = []
    keys = {}
    indexes = {}

    private_key = None
    num_ports = args.ports

    config.read_file(open("configs/config.ini"))

    # parse out the config.ini file
    index = 0
    for section in config.sections():
        temp_host = None
        for (key, val) in config.items(section):
            if key == "host":
                temp_host = val
            elif key == "port":
                # not our ip
                if not temp_host == my_ip:
                    parties.append((temp_host, int(val)))
                    indexes[temp_host] = index
                    index += 1
                # our ip
                else:
                    parties.append((temp_host, int(val)))
                    my_port = int(val)
                    indexes[temp_host] = index
                    index += 1

            elif key == "public" and temp_host != my_ip:

                keys[temp_host] = PublicKey(val.encode(), encoder=nacl.encoding.Base64Encoder)

            elif key == "private" and temp_host == my_ip:

                private_key = PrivateKey(val.encode(), encoder=nacl.encoding.Base64Encoder)

    return my_ip, my_port, parties, keys, private_key, indexes, num_ports

def build_message():

    msg = [-1 for i in range(len(parties))]

    for p in parties:

        if p[0] == my_ip:
            continue

        #PyNaCl assymetric encryption
        #box = Box(private_key, keys[p[0]])
        box = Box(private_key, keys[p[0]]) #REMOVE AFTER
        #get index by party ID
        index = indexes[p[0]]

        #encrypt value for party i
        message = box.encrypt(bytes([value]))
        msg[index] = (base64.b64encode(message).decode('utf-8'), my_ip)

    return msg



my_ip, my_port, parties, keys, private_key, indexes, num_ports = get_args()
#print(f"my_ip: {my_ip}")
#print(f"my_port: {my_port}")
#print(f"parties: {parties}")
#print(f"keys: {keys}")
#print(f"private_key: {private_key}")
#print(f"indexes: {indexes}")

server_ip = str(ipaddress.ip_address(my_ip) + 1)
server_port = 8765 + (my_port % num_ports)
server = (server_ip, server_port)
client = ClientNode(my_ip, my_port)

value = random.randint(1, 10)
#shares = [1 for i in range(len(parties))] # this is only for testing
client.r1_sum += value
my_message = build_message()
print(f"My Value: {value}")

start = time.time()
try:

    #time.sleep(random.randint(0, 2)) an attempt to make connection to server faster

    #Connect to server
    #start_connecting = time.time()
    client.connect_to_node(server)
    #print(f"Connected to server in {time.time() - start_connecting} seconds")

    # round 0 getting id numbers
    s = time.time()
    client.send_message({'round' : 0, 'message' : indexes[my_ip]}, addr = server)
    print(f"I sent round 0 in {time.time() - s} seconds")

    # Wait until everyone is done
    while client.round_num < NUM_ROUNDS + 1:
        continue

    print(f'{my_ip} sum : {client.r1_sum}')
    print(f'it took {time.time() - start} seconds for {len(parties)} parties.')
    sys.exit()

except Exception:
    print(f'There was an error after {time.time() - start} seconds.')
    raise Exception
