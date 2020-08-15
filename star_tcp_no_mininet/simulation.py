import argparse
import subprocess
import time

parser = argparse.ArgumentParser(description=None);
parser.add_argument("-p", "--parties", action="store", required=True, type=int, help="number of parties");
parser.add_argument("-n", "--ports", action="store", default=10, type=int, help="number of parties");
args = parser.parse_args();


num_parties = args.parties
port = 8888

print("Generating config.ini file...")
subprocess.Popen(["sudo", "python3", "generate.py", "-p{}".format(num_parties)]).wait()
print("Finished creating config.ini file")

active_parties = []
print("Starting Server")
active_parties.append(subprocess.Popen(["sudo", "python3", "server.py", "-H{}".format(num_parties), "-P{}".format(args.ports)]))
print("Starting all nodes\n")
for i in range(num_parties):

    active_parties.append(subprocess.Popen(["sudo", "python3", "summation.py", "-p{}".format(port), "-n{}".format(args.ports)]))
    port += 1

#Wait for parties to finish
for i in active_parties:
    i.wait()

print("Done")
