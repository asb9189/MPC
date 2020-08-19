from node import Node
import random
import socket
import argparse
import configparser
import time
import sys
import os

#networking libary
import netifaces as ni

#crypto libary
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import Base64Encoder

#Author Aleksei Bingham

'''
This program exchanges integers with 2 other nodes following
the my_framework topology. While the IP's are hard coded this would be
swapped out with command line arguments and a given config.ini file
containing a list of each parties IP:PORT.

Keep in mind the IP:PORT in party_list are real machines on my local network
that do have connection to one another. Of course this means self.next is different
for each node and is represented as such in each summation.py on each machine along with self.members
'''

def get_ip(hostname):

    ni.ifaddresses(hostname + '-eth0')
    return ni.ifaddresses(hostname + '-eth0')[ni.AF_INET][0]['addr']

class SummationNode(Node):

    def __init__(self, host, port):

        self.public_key = None
        self.private_key = None

        self.received = 0

        #my value that will be changed rapidly
        self.mysum = 0

        #the original value of mysum to be sent
        #to all nodes in self.members
        self.value = 0

        #list of all members in network excluding myself
        self.members = []
        self.done = False
        self.done_messages = 0
        self.sent_done = False
        self.start = False

        self.num_keys = 0
        self.num_done_keys = 0
        self.sent_done_keys = False
        self.keys = {}

        self.sent_message = False
        self.sent_start = False

        self.index = None

        #tuple of (ip, port)
        #representing my successor node
        self.next = None
        super().__init__(host, port)

    def receive(self, message, conn=None, addr_list=None):

        #debug statement
        #print("message: " + str(message))

        #check the type of the message
        if message["type"] == "data":

            #check if destination is for us
            #and if so prevent it from moving forward
            if message["destination"] == self.host:

                #print("Caught my own message")
                return

            else:

                #decrypt the messages
                secret_message = message[self.host].encode("ISO-8859-1")
                box = Box(self.private_key, self.keys[message["destination"]])
                msg = box.decrypt(secret_message)
                input = int.from_bytes(msg, "big")

                self.mysum = self.mysum + input
                self.received = self.received + 1
                self.send_message(message, [self.next])


        elif message["type"] == "done":

            # only party leader collects done messages
            if self.index == 0:
                self.done_messages = self.done_messages + 1
            else:
                self.send_message(message, [self.next])

        elif message["type"] == "shutdown":

            #prevent sending message to an already shutdown node
            #(party leader will be first to shutdown always)
            if self.next[0] != message["destination"]:
                self.send_message(message, [self.next])
            self.done = True

        else:

            print("I don't recognize this type of data\n\t{}".format(message))

        #only the party leader should send the shutdown message
        if self.index == 0:

            if self.received == len(self.members) and self.done_messages == len(self.members) and not self.done:
                msg = {"destination": self.host, "type": "shutdown"}
                self.send_message(msg, [self.next])
                self.done = True

        #everyone else checks if they can send their done message
        #to the party leader
        else:

            if self.received == len(self.members) and not self.sent_done:
                msg = {"type": "done"}
                self.send_message(msg, [self.next])
                self.sent_done = True


    # kick off protocol
    def start_protocol(self, msg):
        self.send_message(msg, [self.next])
        self.sent_message = True

def get_args():

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-I", "--index", action="store", required=True, type=int, default=0, help="group size")
    parser.add_argument("-A", "--agg", action="store", required=True, help="agg ip")
    parser.add_argument("-H", "--hostname", action="store", required=True, help="hostname")
    parser.add_argument("-C", "--config", action="store", required=True,
                        help="config.ini file with addr:port for each member")
    args = parser.parse_args()
    file = args.config
    config = configparser.ConfigParser()
    path = sys.path[0] + "/configs/" + file
    config.read_file(open(path))

    my_ip = get_ip(args.hostname)
    my_port = 8700  # default
    parties = []

    keys = {}
    private_key = None

    # parse out the config.ini file
    for section in config.sections():
        temp_host = None
        for (key, val) in config.items(section):
            if key == "host":
                temp_host = val
            elif key == "port":
                # not our ip
                if not temp_host == my_ip:
                    parties.append((temp_host, int(val)))
                # our ip
                else:
                    parties.append((temp_host, int(val)))
                    my_port = int(val)

            elif key == "public" and temp_host != my_ip:

                keys[temp_host] = PublicKey(val.encode(), encoder=nacl.encoding.Base64Encoder)

            elif key == "private" and temp_host == my_ip:

                private_key = PrivateKey(val.encode(), encoder=nacl.encoding.Base64Encoder)


    # get our next_node
    next_node = None
    for i in range(len(parties)):
        p = parties[i]
        if p[0] == my_ip:
            try:
                next_node = parties[i + 1]
            except Exception:
                next_node = parties[0]

    # remove our self from the parties list
    parties.remove((my_ip, my_port))

    return my_ip, my_port, args.index, next_node, parties, keys, private_key

def main():

    my_ip, my_port, index, next_node, parties, keys, private_key = get_args()

    print("Running on {}".format(my_ip))
    print("next node {}".format(next_node))

    #print(f"Private Key {private_key}")
    #print(f"Keys {keys}")

    node = SummationNode(my_ip, my_port)
    node.value = random.randint(1, 10)
    node.mysum = node.value
    node.index = index
    node.private_key = private_key
    node.keys = keys

    print("My value {}".format(node.value))

    node.connect_to_node([next_node])
    node.next = next_node

    node.members = parties

    #without this sleep the program
    #will not run properly
    time.sleep(10) #this sleep should be changed to allow for large no. parties

    start_time = time.time()

    # message for exchanging shares
    msg = {"destination": my_ip, "type": "data"}
    for p in parties:

        box = Box(private_key, node.keys[p[0]])
        message = box.encrypt(bytes([node.value]))
        msg[p[0]] = message.decode('ISO-8859-1')

    node.start_protocol(msg)

    # Wait until everyone is done
    while True:

        #kill switch
        #if (time.time() - start_time > 60):
            #print("Error: at least one machine stalled")
            #sys.exit()

        if node.done:
            print("\nTotal sum: " + str(node.mysum))
            print("Total Time: {}".format(time.time() - start_time))

            sys.exit()


if __name__ == "__main__":
    main()
