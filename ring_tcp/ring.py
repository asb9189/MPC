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

def ping_all():

    # Ping forward and backward nodes
    for i in range(0,num_nodes):
        node = net.hosts[i]

        fwdNode, bwNode = None, None

        output('%s -> '%node.name)
        
        bwNode = net.hosts[i-1]
        bwIP = bwNode.IP('%s-eth1'%bwNode.name)
        result = node.cmd('ping -c1 %s'%bwIP)
        sent, received = net._parsePing(result)

        output(('%s '%bwNode.name) if received else 'X ')

        try:
            fwdNode = net.hosts[i+1]
        except IndexError:
            fwdNode = net.hosts[0]

        fwdIP = fwdNode.IP('%s-eth0'%fwdNode.name)
        result = node.cmd('ping -c1 %s'%fwdIP)
        sent, received = net._parsePing(result)

        output(('%s '%fwdNode.name) if received else 'X ')

        output('\n')

def start_protocol():

    agg_ip = "None"
    command = "python3 summation.py -I{} -H {} -C config{}.ini -A " + str(agg_ip)

    start = time.time()

    index = 0;
    group_index = 0;
    for p in net.hosts:

        if index == len(net.hosts) - 1:
            p.sendCmd(command.format(index, p.name, group_index));

            print("Started all parties")
            for m in (net.hosts)[::-1]:
                print(m.waitOutput());

        else:
            p.sendCmd(command.format(index, p.name, group_index));
        
        index += 1;

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=None);
    parser.add_argument("-p", "--parties", action="store", required=True, type=int, help="number of parties");
    args = parser.parse_args();
    num_nodes = args.parties;

    if num_nodes <= 1:
        print("Error: Illegal Number of Parties {}".format(num_nodes))
        sys.exit()
    print("Running generate.py -p{} -g{}".format(num_nodes, num_nodes))
    subprocess.Popen(["sudo", "python3", "generate.py", "-p{}".format(num_nodes), "-g{}".format(num_nodes)]).wait()
    print("Finished generating config files")
    net = Mininet()
    print("Starting Simulation")
    
    start = time.time()

    ip_one = ipaddress.ip_address("10.0.1.1")
    ip_two = ipaddress.ip_address("10.0.1.2")

    #after each iteration add '256' to rollover to next IP
    #print(str(ip_one + 256))
    #print(str(ip_two + 256))

    # Create the nodes without an ip
    for i in range(1,num_nodes+1): 
        net.addHost('h%d'%i,ip=None)

    # from 1 to num_nodes-1 because the index starts from zero
    for i in range(1,num_nodes): 

        h1 = net.hosts[i-1]
        h2 = net.hosts[i]

        net.addLink(h2, h1, intfName1 = '%s-eth0'%h2.name, intfName2 = '%s-eth1'%h1.name)
        h2.intf('%s-eth0'%h2.name).setIP(str(ip_one), 24) 
        h1.intf('%s-eth1'%h1.name).setIP(str(ip_two), 24)

        #print("{} eth1 {}".format(h1.name, ip_two))
        #print("{} eth0 {}".format(h2.name, ip_one))
        #print("\n")

        #if h2 is the last node wrap back to front
        if (i == num_nodes-1):
            h1 = net.hosts[0]
            ip_one += 256
            ip_two += 256
            net.addLink(h2, h1, intfName1 = '%s-eth1'%h2.name, intfName2 = '%s-eth0'%h1.name)
            h2.intf('%s-eth1'%h2.name).setIP(str(ip_one), 24) 
            h1.intf('%s-eth0'%h1.name).setIP(str(ip_two), 24)

            #print("{} eth0 {}".format(h1.name, ip_two))
            #print("{} eth1 {}".format(h2.name, ip_one))
            #print("\n")

        ip_one += 256
        ip_two += 256

    print("Created {} nodes in {} seconds".format(num_nodes, time.time() - start))

    net.start()

    start = time.time()

    start_protocol()

    end = time.time()

    print("Total Time: {} seconds".format(end - start))

    net.stop()
