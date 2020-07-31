import warnings
warnings.filterwarnings("ignore")

from mininet.net import Mininet
from mininet.log import output
from mininet.cli import CLI
import subprocess
import argparse
import ipaddress
import time
import sys


# Try to ping:
# node -> server
# server -> node
def ping_all():

    server = net.hosts[len(net.hosts) - 1]

    #Keep track of server interface
    server_index = 0
    for i in range(0,num_nodes):

        # ping node -> server
        node = net.hosts[i]
        server_ip = server.IP('s0-eth{}'.format(server_index))

        print("Node {} -> {}".format(node.name, server_ip))
        result = node.cmd('ping -c1 {}'.format(server_ip))
        sent, received = net._parsePing(result)

        if not received:
            print("ERROR!")
            sys.exit()

        output(('%s '%server.name) if received else 'X ')
        output('\n')

        # ping server -> node
        print("Server -> {}".format(node.IP('{}-eth0'.format(node.name))))
        result = server.cmd('ping -c1 {}'.format(node.IP('{}-eth0'.format(node.name))))
        sent, received = net._parsePing(result)

        if not received:
            print("ERROR!")
            sys.exit()

        output(('%s '%node.name) if received else 'X ')

        output('\n')
        server_index += 1

def start_protocol():

    print("Starting Server")
    net.hosts[len(net.hosts)-1].sendCmd("sudo python3 server.py -H{} -P{}".format(len(net.hosts)-1, num_ports))
    time.sleep(5)
    print("Server Started")

    command = "python3 summation.py -H{} -P{}"

    start = time.time()
    num_parties = len(net.hosts) - 1
    index = 0;
    group_index = 0;
    for p in net.hosts:

        #exclude server
        if p.name == 's0':
            continue

        if index == len(net.hosts) - 2:
            p.sendCmd(command.format(p.name, num_ports))

            print("Started all parties\n")
            for m in (net.hosts):
                print(m.waitOutput());

        else:
            p.sendCmd(command.format(p.name, num_ports))

        index += 1;

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=None)
    parser.add_argument("-p", "--parties", action="store", required=True, type=int, help="number of parties")
    parser.add_argument("-n", "--ports", action="store", default=10, type=int, help="number of ports")
    args = parser.parse_args()
    num_nodes = args.parties
    num_ports = args.ports

    if num_nodes <= 1:
        print("Illegal Number of Parties: {}".format(num_nodes))
        sys.exit()
    if num_ports < 1:
        print("Illegal Number of Ports: {}".format(num_ports))
        sys.exit()

    print("Running generate.py -p{}".format(num_nodes))
    subprocess.Popen(["sudo", "python3", "generate.py", "-p{}".format(num_nodes)]).wait()
    print("Finished generating config files")

    net = Mininet()
    print("Starting Simulation")

    start = time.time()

    start_ip = ipaddress.ip_address("10.0.1.1")
    server_start_ip = ipaddress.ip_address("10.0.1.2")

    # Create the nodes without an ip
    for i in range(1,num_nodes+1):
        net.addHost('h%d'%i,ip=None)

    # Create static server
    net.addHost('s0', ip=None)
    server = net.hosts[len(net.hosts) - 1]

    # connect all nodes to server
    index = 0
    for i in range(0 ,num_nodes):

        host = net.hosts[i]

        net.addLink(host, server, intfName1 = '%s-eth0'%host.name, intfName2 = 's0-eth{}'.format(str(index)))

        host.intf('%s-eth0'%host.name).setIP(str(start_ip), 24)
        server.intf('s0-eth{}'.format(str(index))).setIP(str(server_start_ip), 24)
        #print(f"Created host {host.name} with IP {str(start_ip)}")
        #print(f"Created server {server.name} with IP {str(server_start_ip)}\n")

        start_ip += 256
        server_start_ip += 256
        index += 1

    print("Created {} nodes in {} seconds".format(num_nodes, time.time() - start))

    net.start()
    start = time.time()

    #CLI(net)
    #ping_all()
    start_protocol()

    end = time.time()

    print("Total Time: {} seconds".format(end - start))

    net.stop()
