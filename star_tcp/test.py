from node import Node
import json
import time
import sys

NUM_PARTIES = 50
NUM_ROUNDS = 10

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
            # end of round 0 so send the next round.
            if self.recv_count == 1 and self.send_count == 1:
                self.round_num += 1
                self.send_message({'round' : self.round_num, 'message' : [i for i in range(self.num_parties)]}, addr = ('127.0.0.1', 8765 + (self.port % 10)))
                self.recv_count = 0
                self.send_count = 0
        else:
            vals = msg['message'].split('\n')
            for num in vals[:-1]:
                self.r1_sum += int(num)
            if self.recv_count == 1:
                self.round_num += 1
                if self.round_num != NUM_ROUNDS + 1:
                    self.send_message({'round' : self.round_num, 'message' : [i for i in range(self.num_parties)]}, addr = ('127.0.0.1', 8765 + (self.port % 10)))
                    self.recv_count = 0
                    self.send_count = 0

party_list = [ClientNode('127.0.0.1', 8888 + i) for i in range(NUM_PARTIES)]

start = time.time()
try:
    # connect to the server
    start = time.time()
    for p in party_list:
        # since the server is listening on 10 ports each client needs to connect to one of the 10
        # this is why we use mod 10 plus the default port number for the server
        p.connect_to_node(('127.0.0.1', 8765 + (p.port % 10)))

    # round 0 getting id numbers
    for p in party_list:
        p.send_message({'round' : 0}, addr = ('127.0.0.1', 8765 + (p.port % 10)))

# Wait until everyone is done
    while True:
        time.sleep(1)
        done = True
        num_done = 0
        for p in party_list:
            if p.round_num < NUM_ROUNDS + 1:
                done = False
            else:
                num_done += 1
                print(f'r1 sum : {p.r1_sum}, r2 sum : {p.r2_sum}, r3 sum : {p.r3_sum}')
        print('parties finished:', num_done)
        if done:
            print(f'it took {time.time() - start} seconds for {NUM_PARTIES} parties and {NUM_ROUNDS} rounds.')
            sys.exit()
except Exception:
    print(f'There was an error after {time.time() - start} seconds.')
    raise Exception
