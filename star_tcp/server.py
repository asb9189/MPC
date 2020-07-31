from node import Node
import argparse
import time
import json
import select
import collections
import threading
import sys
import socket

# import constants
from constants import FORMAT

parser = argparse.ArgumentParser(description=None);
parser.add_argument("-H", "--hosts", action="store", required=True, type=int, help="number of parties");
parser.add_argument("-P", "--ports", action="store", required=True, type=int, help="number of open ports");
args = parser.parse_args();

NUM_ROUNDS = 1
NUM_PARTIES = args.hosts
NUM_PORTS = args.ports

class CentralServer(Node):
    def __init__(self, host, port):
        super().__init__(True, host, port)

        #num connections
        self.connections = 0

        # node id counter to keep track of node id's
        self.id_counter = 0

        # message dictionary to package all messages together for a node.
        self.message_collector = {}

        # dictionary mapping id numbers to addresses.
        self.id_table = {}

        # dictionary that maps addresses to id numbers.
        self.addr_table = {}

        # create extra sockets to listen for connections.
        # use range 1,10 to get 9 new sockets to listen on
        for i in range(1,NUM_PORTS):
            new_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            new_listener.bind((host, port + i))
            new_listener.listen(5)
            new_listener.setblocking(0)
            self.inbound_connections.append(new_listener)

        event_loop = threading.Thread(target = self.server_loop)
        event_loop.daemon = True
        event_loop.start()

    def server_loop(self):
        bufs = collections.defaultdict(str)
        start = None
        time_started = False
        time_collected = False
        while True:
            reader, writer, errors = select.select(self.inbound_connections,
                                                   self.inbound_connections,
                                                   self.inbound_connections, 60)
            # wait for all nodes to connect
            if self.connections != NUM_PARTIES: #Aleksei: removed 2s timer
                for sock in reader:
                    if sock in self.inbound_connections[:NUM_PORTS]:
                        conn, addr = sock.accept()
                        if not time_started:
                            start = time.time()
                            time_started = True
                        conn.setblocking(0)
                        self.inbound_connections.append(conn)
                        self.connections += 1 #I added this

            # all nodes are connected so start reading data.
            else:
                if not time_collected:
                    print(f"It took {time.time() - start} seconds to connect all nodes to the server")
                    time_collected = True
                for sock in reader:
                    # the first 10 sockets in the list are the listeners
                    if sock not in self.inbound_connections[:NUM_PORTS]:
                        data = sock.recv(65507)
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

    def receive(self, msg, sock):
        if msg['round'] == 0:

            # get index specified by the party member
            index = msg['message']
            # this should always be here inside of receive.
            # set up the dictionary that will package the messages for the nodes.
            # send the node its id number as well as how many parties are connected to the server.
            self.message_collector[index] = {'round' : 0, 'message': index, 'num_parties' : NUM_PARTIES}
            self.id_table[index] = sock.getpeername()
            self.addr_table[sock.getpeername()] = index
            #self.id_counter += 1
            self.recv_count += 1
            if self.recv_count == NUM_PARTIES:
                for i in self.inbound_connections[NUM_PORTS:]:
                    self.send_message(self.message_collector[self.addr_table[i.getpeername()]], conn = i)
                    # self.send_count += 1

        # server is only responsible for packaging and sending messages to the proper parties.
        # add rounds assciated with the messages being sent back.
        elif msg['round'] > 0:
            for key in self.message_collector:
                # make sure we do not receive a share from ourselves.
                if key != self.addr_table[sock.getpeername()]:
                    self.message_collector[key]['message'] += str(msg['message'][key]) + '\n'
            self.recv_count += 1
            if self.recv_count == NUM_PARTIES:
                for i in self.inbound_connections[NUM_PORTS:]:
                    self.send_message(self.message_collector[self.addr_table[i.getpeername()]], conn = i)
                    # only increment the counter when we send all the messages intended for the node.
                    # self.send_count += 1

        if self.recv_count == len(self.inbound_connections) - NUM_PORTS and self.send_count == len(self.inbound_connections) - NUM_PORTS:
            if self.round_num == NUM_ROUNDS:
                self.is_done = True
            else:
                self.round_num += 1
                for key in self.message_collector:
                    self.message_collector[key]['round'] += 1
                    self.message_collector[key]['message'] = ''
                    if self.round_num == 1:
                        del self.message_collector[key]['num_parties']
                self.recv_count = 0
                self.send_count = 0

start2 = time.time()
server = CentralServer(host = '0.0.0.0', port = 8765)
try:
    while True:
        #time.sleep(1)
        #print(len(server.inbound_connections) - 10)
        if server.is_done == True:
            print(f'Overall it took {time.time() - start2} seconds')
            sys.exit()
except Exception:
    print(f'There was an eror after {time.time() - start2} seconds')
