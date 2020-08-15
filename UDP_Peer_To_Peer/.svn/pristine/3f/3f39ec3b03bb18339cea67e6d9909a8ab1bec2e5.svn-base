import socket
import sys
from abc import ABCMeta, abstractmethod
import json
import select
import threading
import time
import collections

# import the neccessary variables from the constants file
from constants import HEADERSIZE, FORMAT

# unsure if this method will be useful.
# helper function to split the message into smaller chunks and send.
def split_message(message, sock, writer_poll, addr_list = []):

    mid = int(len(message) / 2)
    beginning = message[:mid]
    end = message[mid:]

    if len(beginning) < 1490 and len(end) < 1490:
        for i in addr_list:
            done_writing = False
            while not done_writing:
                poll_event = writer_poll.poll(10000)
                for socks, _ in poll_event:
                    sock.sendto(beginning, i)
                    sock.sendto(end, i)
                    done_writing = True
    else:
        split_message(beginning, sock, writer_poll, addr_list)
        split_message(end, sock, writer_poll, addr_list)

class Node():

    def __init__(self, server, host = None, port = None):

        # will let us know if the node we are running is the central server.
        self.is_server = server

        # flag to let us know if the node has finished the protocol.
        self.is_finished = False

        # will allow us to keep track of the current round
        self.round_num = 0

        # host of the node.
        if host is not None:
            self.host = host
        else:
            self.host = socket.gethostbyname(socket.gethostname())

        # list of inbound sockets.
        self.inbound_connections = []

        # create the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, port))
        self.port = port
        self.sock.setblocking(0)

        # if we are not the server then start the loop to receive data.
        if self.is_server == False:
            loop_process = threading.Thread(target = self.node_loop)
            loop_process.daemon = True
            loop_process.start()

    # this loop is responsible for calling receive on incoming data.
    def node_loop(self):
        bufs = collections.defaultdict(str)
        reader_poll = select.poll()
        reader_poll.register(self.sock, select.POLLIN)

        while True:
          poll_event = reader_poll.poll(10000)
          for sock, _ in poll_event:
              data, address = self.sock.recvfrom(65507)
              bufs[address] += data.decode(FORMAT)

          for address, buf in bufs.items():
              lines = buf.split('\n')
              bufs[address] = lines[-1]
              for l in lines[:-1]:
                  self.receive(json.loads(l))

    # purely virtual method so the child class receive method can be called.
    @abstractmethod
    def receive(self, msg, conn = None, addr_list = None):
        raise NotImplementedError("You need to override the receive method.")

    # returns true once all outgoing messages have been sent
    # sends a message to a node that we are already connected to and is listening for us.
    def send_message(self, msg, addr_list = None, conn = None):

        writer_poll = select.poll()
        writer_poll.register(self.sock, select.POLLOUT)
        msg = json.dumps(msg)+'\n'
        message = msg.encode(FORMAT)

        # the message is too long so break it up and send chunks
        if len(message) > 1490:
            split_message(message, self.sock, writer_poll, addr_list)
            # raise Exception('Message might be longer than 1500 bytes:', message)

        for i in addr_list:
            if i == (self.host, self.port):
                #print('ERROR: we cannot send a message to ourselves.')
                pass
            else:
                done_writing = False

                while not done_writing:
                    poll_event = writer_poll.poll(100000)
                    for sock, _ in poll_event:
                        self.sock.sendto(message, i)
                        done_writing = True

    # print all other nodes we know about. This is only useful as the server.
    def print_connections(self):
        print('----- Inbound Connections  ------')
        if self.inbound_connections:
            for i in self.inbound_connections:
                print(i)
        else:
            print('None.')

    # to string method used for printing out the information associated with a node.
    def __str__(self):
        return f'Node ID: {self.node_id}, Host: {self.host}, Port: {self.port}'
