
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


NUM_ROUNDS = 2

#use our hostnae to determine our IP on the network
def get_ip(hostname):
    """Returns the IPv4 address of host machine given it's desired interface hostname"""

    ni.ifaddresses(hostname + '-eth0')
    return ni.ifaddresses(hostname + '-eth0')[ni.AF_INET][0]['addr']

class ClientNode(Node):
    def __init__(self, host, port, parties, keys, private_key, indexes, message, server):
        super().__init__(False, host, port)
        self.r1_sum = 0
        self.r2_sum = 0
        self.r3_sum = 0

        self.parties = parties
        self.keys = keys
        self.private_key = private_key
        self.indexes = indexes
        self.message = message
        self.server = server

        self.time = None

    def receive(self, msg):
        """Handles incoming data from the server while sending new data out to the server
        :param msg: dictionary containing the current round and shares from other parties excluding round 0
        """
        if msg['round'] == 0:
            self.time = time.time()
            self.node_id = msg['message']
            self.num_parties = msg['num_parties']
            #end of round 0 send the first real message
            if self.recv_count == 1 and self.send_count == 1:
                self.round_num += 1
                self.send_message({'round' : self.round_num, 'message' : self.message}, addr=self.server)
                self.recv_count = 0
                self.send_count = 0
        else:
            got_data = False #Bandage fix for self.recv_count issue with large parties
            vals = msg['message'].split('\n')
            for num in vals[:-1]:
                #self.r1_sum += int(num) #THIS CHANGES WITH ENCRYPTION OR NOT
                self.r1_sum += decrypt(num, self.private_key, self.keys)
                got_data = True
            if self.recv_count == 1 or got_data:
                self.round_num += 1
                if self.round_num != NUM_ROUNDS + 1:
                    self.send_message({'round' : self.round_num, 'message' : self.message}, addr = self.server)
                    self.recv_count = 0
                    self.send_count = 0

#decrpyt the given data using our private key and the 'senders' public key
def decrypt(data, private_key, keys):
    """Decrpyts data encrypted using PyNaCl given a private key and hashtable of IPv4 -> public key
    :param data: encrypted data (share) from another party
    :param private_key: the recieving nodes private key used to unencrypt the my_message
    :param keys: dictionary of IPv4 -> Public key
    :return: unencrypted data
    """
    num = literal_eval(data)
    secret_message = base64.b64decode(num[0].encode('utf-8'))
    box = Box(private_key, keys[num[1]])
    msg = box.decrypt(secret_message)
    input = int.from_bytes(msg, "big")
    return input

#read from command line and config.ini file to gather all information needed
#prior to executing the protocol.
def get_args():
    """Returns information parsed from command line arguments and config.ini file
    :return: client IPv4 on the network
    :return: client port
    :return: list of all party members parsed out from config.ini file
    :return: hashtable called keys mapping IPv4 -> Public Key
    :return: private_key
    :return: hashtable of IPv4 -> Server Index (Used on server side)
    :return: number of open ports on the server
    """
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


def build_message(parties, my_ip, private_key, keys, indexes, value):

    """
    creates an array of length parties such that each index is an encrypted version
    of our randomly generated input. Each index corresponds to the party ID. For example
    index 0 is the party who holds ID 0. Knowing this, we MUST encrypt value at index 0 with
    the party member's public key who also holds ID 0.
    :param parties: List of all party members
    :param my_ip: Client side IP
    :param private_key: Client side private key
    :param keys: hashtable IPv4 -> Public Key
    :param indexes: Hashtable IPv4 -> Server Index
    :param value: Value (share) to be encrypted for all other party members
    :return: encrypted message contaning n number of encrypted shares for n party members on the network
    """

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

def main():

    my_ip, my_port, parties, keys, private_key, indexes, num_ports = get_args()

    server_ip = str(ipaddress.ip_address(my_ip) + 1)
    server_port = 8765 + (my_port % num_ports)
    server = (server_ip, server_port)

    #value = random.randint(1, 10)
    value = 1
    my_message = build_message(parties, my_ip, private_key, keys, indexes, value)
    client = ClientNode(my_ip, my_port, parties, keys, private_key, indexes, my_message, server)

    #value = 1
    #my_message = [1 for i in range(len(parties))] # this is only for testing

    #add our own value prior to receiving others to get a true total sum.
    client.r1_sum += value * NUM_ROUNDS
    print(f"My Value: {value}")

    try:

        #Connect to server
        client.connect_to_node(server)

        # round 0 getting id numbers
        client.send_message({'round' : 0, 'message' : indexes[my_ip]}, addr = server)

        # Wait until everyone is done
        while client.round_num < NUM_ROUNDS + 1:
            time.sleep(1)
            continue

        print(f'{my_ip} sum : {client.r1_sum}')
        print(f'it took {time.time() - client.time} seconds for {len(parties)} parties.')
        sys.exit()

    except Exception:
        print(f'There was an error after {time.time() - client.time} seconds.')
        raise Exception

if __name__ == '__main__':
    main()
