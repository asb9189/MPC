import socket
import sys
from abc import ABCMeta, abstractmethod
import json
import select
import threading
import time
import collections

class Node():

    def __init__(self, server, host = None, port = None):

        # lets us know if we are a server node
        self.is_server = server

        # flag to let us know if the node is finished with the protocol.
        self.is_done = False

        # keep track of the current round.
        self.round_num = 0

        # counter to keep track of the number of messages sent and received
        self.send_count = 0
        self.recv_count = 0

        # keep track of the number of parties in the protocol
        self.num_parties = 0

        # store the id number associated with the node, this will be assigned by the server.
        self.node_id = 0

        # host of the node.
        if host is not None:
            self.host = host
        else:
            self.host = socket.gethostbyname(socket.gethostname())

        # list of outbound sockets.
        self.outbound_connections = []

        # list of inbound sockets.
        self.inbound_connections = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if port is not None:
            self.sock.bind((self.host, port))
            self.port = port
        else:
            self.sock.bind((self.host, 0))
            # remember the port we are listening on.
            self.port = self.sock.getsockname()[1]

        # since we are the server we need to listen for connections.
        if self.is_server == True:
            self.sock.listen(5)
            self.sock.setblocking(0)

        # for select to work we need to have a 'connection' to ourselves
        self.inbound_connections.append(self.sock)

    # this loop will handle all of the incoming connections and read data from them
    # as well as calling the receive method on incoming data.
    def node_loop(self):
        bufs = collections.defaultdict(str)
        while True:

            reader, writer, errors = select.select(self.inbound_connections,
                                                   self.outbound_connections,
                                                   self.inbound_connections, 60)
            for sock in reader:
                data = sock.recv(65507)
                self.recv_count += 1
                bufs[sock] += data.decode('utf-8')

            for sock in errors:
                self.inbound_connections.remove(sock)
                if sock in self.outbound_connections:
                    self.outbound_connections.remove(sock)
                sock.close()

            for sock, buf in bufs.items():
                lines = buf.split('\n')
                bufs[sock] = lines[-1]
                for l in lines[:-1]:
                    self.receive(json.loads(l))

    # connect to a node listening for your connection.
    def connect_to_node(self, addr):
        start = time.time()
        if addr == (self.host, self.port):
            print('Cannot connect to ourselves.')
            return

        else:

            while True:
                try:
                    self.sock.connect(addr)
                    total = time.time() - start
                except Exception as e:
                    #time.sleep(1)
                    continue
                break

            self.outbound_connections.append(self.sock)
            loop_thread = threading.Thread(target = self.node_loop)
            loop_thread.daemon = True
            loop_thread.start()

    # purely virtual method so the child class receive method can be called.
    @abstractmethod
    def receive(self, msg, conn = None, addr_list = None):
        raise NotImplementedError("You need to override the receive method.")

    # returns true once all outgoing messages have been sent
    # sends a message to a node that we are already connected to and is listening for us.
    def send_message(self, msg, addr = None, conn = None):

        msg = json.dumps(msg)+'\n'
        message = msg.encode('utf-8')

        # if we are the client just send the message
        if self.is_server == False:
            self.sock.send(message)
            self.send_count += 1

        # if not we must be the server sending the message back
        elif self.is_server == True:
            if conn is None:
                if addr == (self.host, self.port):
                    print('ERROR: we cannot send a message to ourselves.')
                else:
                    for j in self.inbound_connections:
                        if j.getpeername() == addr:
                            j.send(message)
                            self.send_count += 1
            else:
                conn.send(message)
                self.send_count += 1

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

    # to string method used for printing out the information associated with a node.
    def __str__(self):
        return f'Host: {self.host}, Port: {self.port}'
