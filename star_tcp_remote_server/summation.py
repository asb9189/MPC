
#Author: Aleksei Bingham

'''
summation.py is the client side script used per party member.
First the party member creates a node object, generates a random int value and
encrypts this value for all other party members. This node then sends the shares
to the centeral server and waits until it completes n rounds.
'''

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

#decrpyt the given data using our private key and the 'senders' public key
def decrypt(data):

    num = literal_eval(data)
    secret_message = base64.b64decode(num[0].encode('utf-8'))
    box = Box(private_key, keys[num[1]])
    msg = box.decrypt(secret_message)
    input = int.from_bytes(msg, "big")
    return input

#read from command line and config.ini file to gather all information needed
#prior to executing the protocol.
def get_args():

    parser = argparse.ArgumentParser(description=None);
    parser.add_argument("-p", "--port", action="store", required=True, type=int, help="my port");
    parser.add_argument("-n", "--ports", action="store", default=10, type=int, help="num server ports");
    config = configparser.ConfigParser()
    args = parser.parse_args();

    my_ip = "192.168.1.223"
    my_port = args.port

    parties = []
    keys = {}
    indexes = {}

    private_key = None
    num_ports = args.ports

    config.read_file(open("configs/config.ini"))

    # parse out the config.ini file
    index = 0
    for section in config.sections():
        temp_port = None
        for (key, val) in config.items(section):

            if key == "port":
                temp_port = int(val)
                parties.append(temp_port)
                indexes[temp_port] = index
                index += 1

            elif key == "public" and temp_port != my_port:

                keys[temp_port] = PublicKey(val.encode(), encoder=nacl.encoding.Base64Encoder)

            elif key == "private" and temp_port == my_port:

                private_key = PrivateKey(val.encode(), encoder=nacl.encoding.Base64Encoder)

    return my_ip, my_port, parties, keys, private_key, indexes, num_ports

#create an array of length parties such that each index is an encrypted version
#of our randomly generated input. Each index corresponds to the party ID. For example
#index 0 is the party who holds ID 0. Knowing this, we MUST encrypt value at index 0 with
#the party member's public key who also holds ID 0.
def build_message():

    msg = [-1 for i in range(len(parties))]

    for p in parties:

        if p == my_port:
            continue

        #PyNaCl assymetric encryption
        #box = Box(private_key, keys[p[0]])
        box = Box(private_key, keys[p]) #REMOVE AFTER
        #get index by party ID
        index = indexes[p]

        #encrypt value for party i
        message = box.encrypt(bytes([value]))
        msg[index] = (base64.b64encode(message).decode('utf-8'), my_port)

    return msg

my_ip, my_port, parties, keys, private_key, indexes, num_ports = get_args()
#print(f"My IP: {my_ip}")
#print(f"My Port: {my_port}")
#print(f"Parties: {parties}")
#print(f"Keys: {keys}")
#print(f"Private Key: {private_key}")
#print(f"Indexes: {indexes}")
#print(f"Number of ports: {num_ports}")

server_ip = '192.168.1.100'
server_port = 8765 + (my_port % num_ports)
server = (server_ip, server_port)
client = ClientNode(my_ip, my_port)

value = random.randint(1, 10)
#value = 1
#my_message = [1 for i in range(len(parties))] # this is only for testing

#add our own value prior to receiving others to get a true total sum.
client.r1_sum += value * NUM_ROUNDS
my_message = build_message()
#print(f"msg: {my_message}")
#print(f"My Value: {value}")

start = time.time()
try:

    #Connect to server
    client.connect_to_node(server)

    # round 0 getting id numbers
    client.send_message({'round' : 0, 'message' : indexes[my_port]}, addr = server)

    # Wait until everyone is done
    while client.round_num < NUM_ROUNDS + 1:
        #time.sleep(1)
        continue

    print(f'{my_port} sum : {client.r1_sum}')
    print(f'it took {time.time() - start} seconds for {len(parties)} parties.')
    sys.exit()

except Exception:
    print(f'There was an error after {time.time() - start} seconds.')
    raise Exception
