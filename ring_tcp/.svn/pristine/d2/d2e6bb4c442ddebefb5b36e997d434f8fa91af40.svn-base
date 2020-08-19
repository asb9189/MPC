import socket
import sys
from abc import ABCMeta, abstractmethod
import uuid
import json
import select
import threading
import time
import collections

# import the neccessary variables from the constants file
from imports.constants import HEADERSIZE, FORMAT

class Node():

    def __init__(self, host = None, port = None):

        # if this flag is set to true then shutdown this node.
        self.end_flag = False

        # generate id number for the node.
        self.node_id = uuid.uuid1()

        # host of the node.
        if host is not None:
            self.host = host
        else:
            self.host = socket.gethostbyname(socket.gethostname())

        # list of outbound sockets.
        self.outbound_connections = []

        # list of inbound sockets.
        self.inbound_connections = []

        # default value set to false and will be set to true once all nodes are connected.
        self.connections_done = False

        # keeps track of messages sent per round.
        self.message_count = 0

        # create sockets for listening and sending data
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if port is not None:
            self.listen_sock.bind((self.host, port))
            self.listen_port = port
        else:
            self.listen_sock.bind((self.host, 0))
            # remember the port we are listening on.
            self.listen_port = self.listen_sock.getsockname()[1]

        self.listen_sock.setblocking(0)
        self.listen_sock.listen(5)

        self.inbound_connections.append(self.listen_sock)

        loop_process = threading.Thread(target = self.node_loop)
        loop_process.daemon = True
        loop_process.start()

    # this loop will handle all of the incoming connections and read data from them
    # as well as calling the receive method on incoming data.
    def node_loop(self):
        bufs = collections.defaultdict(str)

        while True:
            reader, writer, errors = select.select(self.inbound_connections,
                                                   self.outbound_connections,
                                                   self.inbound_connections, 60)
            for sock in reader:
                if sock is self.listen_sock:
                    conn, addr = sock.accept()
                    conn.setblocking(0)
                    self.inbound_connections.append(conn)
                else:
                    data = sock.recv(1024)
                    bufs[sock] += data.decode(FORMAT)

            for sock in errors:
                self.inbound_connections.remove(sock)
                if sock in self.outbound_connections:
                    self.outbound_connections.remove(sock)
                sock.close()

            for sock, buf in bufs.items():
                lines = buf.split('\n')
                bufs[sock] = lines[-1]
                for l in lines[:-1]:
                    self.receive(json.loads(l), sock)


    # connect to a node listening for your connection.
    def connect_to_node(self, addr_list = []):

        for i in addr_list:

            if i == (self.host, self.listen_port):
                # print('Cannot connect to ourselves.')
                return

            new_conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_conn_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            new_conn_sock.setblocking(0)

            connected = False
            while not connected:
                try:
                    new_conn_sock.connect(i)
                    self.outbound_connections.append(new_conn_sock)
                    break
                except Exception:
                    new_conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    new_conn_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # print('Connections sucessful!')
        self.connections_done = True

    # purely virtual method so the child class receive method can be called.
    @abstractmethod
    def receive(self, msg, conn = None, addr_list = None):
        raise NotImplementedError("You need to override the receive method.")

    # returns true once all outgoing messages have been sent
    # sends a message to a node that we are already connected to and is listening for us.
    def send_message(self, msg, addr_list = None, conn = None):

        msg = json.dumps(msg)+'\n'
        message = msg.encode(FORMAT)

        # make sure we are connected first.
        if conn is None:
            for i in addr_list:
                if i == (self.host, self.listen_port):
                    print('ERROR: we cannot send a message to ourselves.')
                else:
                    for j in self.outbound_connections:

                        try:
                            if j.getpeername() == i:
                                j.send(message)
                                #print(f'sending message {msg}')
                        except OSError:
                            print("Turning off thread")
                            sys.exit()
                        
        else:
            conn.send(message)

        return True

    # print all inbound and outbound connections
    def print_connections(self):

        print('----- Outbound Connections ------')
        if self.outbound_connections:
            for i in self.outbound_connections:
                print(i)
        else:
            print('None.')

        print('----- Inbound Connections  ------')
        if self.inbound_connections:
            for i in self.inbound_connections:
                print(i)
        else:
            print('None.')

    # reset the message count after each round
    def reset_message_count(self):
        self.message_count = 0

    # to string method used for printing out the information associated with a node.
    def __str__(self):
        return f'Node ID: {self.node_id}, Host: {self.host}, Listening Port: {self.listen_port}'

