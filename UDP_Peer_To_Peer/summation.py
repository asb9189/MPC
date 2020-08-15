from node import Node
import time
import sys
import threading
import random
import socket
import argparse
import configparser
import os
import base64
from ast import literal_eval

#networking libary
import netifaces as ni

#crypto libary
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import Base64Encoder


def get_args():

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-P", "--port", action="store", required=True, type=int, help="port")
    args = parser.parse_args()
    config = configparser.ConfigParser()
    path = sys.path[0] + "/configs/config.ini"
    config.read_file(open(path))

    my_port = args.port

    parties = []
    keys = {}
    private_key = None

    # parse out the config.ini file
    for section in config.sections():
        temp_port = None
        for (key, val) in config.items(section):

            if key == "port":
                temp_port = val
                parties.append( ('127.0.0.1', int(temp_port)) )

            elif key == "public" and temp_port != str(my_port):

                keys[temp_port] = PublicKey(val.encode(), encoder=nacl.encoding.Base64Encoder)

            elif key == "private" and temp_port == str(my_port):

                private_key = PrivateKey(val.encode(), encoder=nacl.encoding.Base64Encoder)

    return my_port, parties, keys, private_key

class SummationNode(Node):
    def __init__(self, host, port, pk, keys):
        super().__init__(False, host, port)
        self.r1_received = 0
        self.mysum1 = None
        self.done = False
        self.done_messages = 0
        self.leader = False

        self.pk = pk
        self.keys = keys

        self.sent_done = False

    def receive(self, message, conn = None, addr_list = None):

        #self.r1_received >= 0.9 * len(party_list)
        if message != None:

            # This is a round 1 message
            if message['round'] == 1:

                self.mysum1 = self.mysum1 + self.decrypt(message['val'])
                self.r1_received = self.r1_received + 1

    #decrpyt the given data using our private key and the 'senders' public key
    def decrypt(self, data):


        secret_message = base64.b64decode(data[0].encode('utf-8'))
        box = Box(private_key, keys[str(data[1])])
        msg = box.decrypt(secret_message)
        input = int.from_bytes(msg, "big")
        return input

    # kick off round 1
    def start(self):
        self.send_round1()

    def send_round1(self):
        count = 0
        for c in party_list:
            if c[1] == my_port:
                continue

            if count == 50:
                time.sleep(20)
                count = 0

            box = Box(private_key, keys[str(c[1])])
            val = box.encrypt(bytes([value]))
            val = (base64.b64encode(val).decode('utf-8'), my_port)
            msg = {'round': 1, 'val': val}
            #print(f"Size of msg: {sys.getsizeof(msg)} bytes")
            #sys.exit()

            self.send_message(msg, [c])
            count = count + 1
        self.sent_done = True

my_port, party_list, keys, private_key = get_args()
#value = random.randint(1, 10)
value = 1
#print("My Value: {}".format(value))
my_node = SummationNode("127.0.0.1", my_port, private_key, keys)
my_node.mysum1 = value
time.sleep(180)

# Give everyone the chance to construct themselfs
start = time.time()
my_node.start()

# Wait until everyone is done
debug = time.time()
while not my_node.r1_received == len(party_list) - 1 or not my_node.sent_done:
    if (time.time() - debug) > 80:
        print("I did not finish")
        print("My Recieved: {}".format(my_node.r1_received))
        print("My Sent: {}\n".format(my_node.sent_done))
        sys.exit()
    time.sleep(1)
    #my_node.receive(None)

#print("Sum " + str(my_node.mysum1))
print(f"Finished in {time.time() - start} seconds")

if my_node.mysum1 != len(party_list):
    print("ERROR: Not all nodes ended with the correct sum!")
