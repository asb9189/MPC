
#mininet package displays unneeded syntax errors
import warnings
warnings.filterwarnings("ignore");

from mininet.node import Controller
from mininet.cli import CLI
from mininet.net import Mininet
from imports.group import *
import argparse
import ipaddress
import time
import sys
import os

net = Mininet()
net.addController('c0');
switches = []

def setup():

    parser = argparse.ArgumentParser(description=None);
    parser.add_argument("-p", "--parties", action="store", required=True, type=int, default=0, help="number of parties");
    parser.add_argument("-g", "--group", action="store", required=True, type=int, default=0, help="group size");
    args = parser.parse_args();

    num_parties = args.parties;
    group_size = args.group;

    if num_parties == 0 or group_size == 0:
        print("Error: neither parties or group size can be 0");
        exit();

    if group_size > num_parties:

        print("Error: group size cannot be larger than number of parties");
        exit();

    if num_parties % group_size != 0:

        print("Error: {} parties cannot be broken into equal groups of size {}".format(num_parties, group_size));
        exit();
        
    main(num_parties, group_size, num_parties // group_size);

def createParties(num_parties, num_groups, group_size):

    hosts = [];
    ip_list = [];

    #create a switch for each group
    for i in range(num_groups):
        switches.append(net.addSwitch("s" + str(i)))

    switch_index = 0
    start_ip = ipaddress.ip_address("172.17.0.2")
    print("Creating Group 1: ")
    for i in range(num_parties):
        node_name = "d" + str(i + 1);
        node_ip = str(start_ip)
        print("node name: {} node ip: {}".format(node_name, node_ip));
        node = net.addHost(node_name, ip = node_ip)
        net.addLink(node, switches[switch_index])  
        hosts.append(node);
        ip_list.append(node_ip);

        if i % group_size == group_size - 1:
            switch_index += 1

            #don't print msg if we are already on last host of current group
            if i != num_parties - 1:
                print("Creating Group {}: ".format(switch_index + 1))

        start_ip += 1

    #add the aggregator as the next available ip address
    #node_name = "a";
    #agg_ip = str(start_ip)
    #print("node name: {} node ip: {}".format(node_name, node_ip));
    #agg_node = net.addHost(node_name, ip=node_ip)
    #net.addLink(agg_node, s1);

    #for switch in switches:
        #net.addLink(agg_node, switch)

    #Not using aggregator right now
    #return hosts, ip_list, agg_node, agg_ip;
    return hosts, ip_list

def createGroups(party_list, group_size, num_groups, ip_list):

    group_list = [];

    for i in range(num_groups):
        group_list.append(Group("group " + str(i + 1)));

    current_index = 0;
    current_group = group_list[current_index];
    count = 0;
    ip_index = 0;
    for party in party_list:

        if count == group_size:
            current_index += 1;
            current_group = group_list[current_index]
            count = 0;

        #Add the member
        current_group.add_member(party);

        #Add the members ip to the group
        current_group.add_ip(ip_list[ip_index]);
        
        ip_index += 1;
        count += 1;

    return group_list;

def main(num_parties, group_size, num_groups):
    
    #create the parties
    #party_list, ip_list, agg_node, agg_ip = createParties(num_parties, num_groups, group_size);
    party_list, ip_list = createParties(num_parties, num_groups, group_size);

    #default
    agg_ip = "127.0.0.1"

    #create the groups
    group_list = createGroups(party_list, group_size, num_groups, ip_list);

    print("Starting Simulation")
    net.start();

    #test with CLI
    #CLI(net)

    #print("Aggregator node: " + str(agg_node));
    #print("Aggregator IP: " + str(agg_ip));

    #don't start the aggregator yet
    #agg_node.sendCmd("python3 source/old/aggregator.py -g " + str(num_groups) + " -p " + str(agg_ip));

    command = "python3 summation.py -I{} -H {} -C config{}.ini -A " + str(agg_ip)

    start_time = time.time();
    group_index = 0;
    for group in group_list:

        index = 0;
            
        for member in group.get_members():

            if index == group_size - 1:
                member.sendCmd(command.format(index, member.name, group_index));

                for m in (group.get_members())[::-1]:
                    print(m.waitOutput());

            else:
                member.sendCmd(command.format(index, member.name, group_index));
            
            index += 1;
        group_index += 1;

    #print("Waiting on aggregator")
    #print(agg_node.waitOutput());
    end_time = time.time();

    print("Total Time: " + str(end_time - start_time));

    print("Shutting down...");

    net.stop();

if __name__ == "__main__":
    setup();
