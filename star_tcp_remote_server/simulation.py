import argparse
import subprocess

parser = argparse.ArgumentParser(description=None);
parser.add_argument("-p", "--parties", action="store", required=True, type=int, help="number of parties");
args = parser.parse_args();


num_parties = args.parties
port = 8888

print("Generating config.ini file...")
subprocess.Popen(["sudo", "python3", "generate.py", "-p{}".format(num_parties)]).wait()
print("Finished creating config.ini file")
print("Starting all nodes")

active_parties = []
for i in range(num_parties):

    active_parties.append(subprocess.Popen(["sudo", "python3", "summation.py", "-p{}".format(port)]))
    port += 1

#Wait for parties to finish
for i in active_parties[::-1]:
    i.wait()

print("Done")
