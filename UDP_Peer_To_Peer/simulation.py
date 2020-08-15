import argparse
import subprocess
import time

parser = argparse.ArgumentParser(description=None);
parser.add_argument("-p", "--parties", action="store", required=True, type=int, help="number of parties");
args = parser.parse_args();


num_parties = args.parties
port = 8888

print("Generating config.ini file...")
subprocess.Popen(["sudo", "python3", "generate.py", "-p{}".format(num_parties)]).wait()
print("Finished creating config.ini file")

active_parties = []
print("Starting all nodes\n")
timer = time.time()
for i in range(num_parties):

    active_parties.append(subprocess.Popen(["sudo", "python3", "summation.py", "-P{}".format(port)]))
    port += 1

print(f"It took {time.time() - timer} seconds to start {num_parties} parties")

#Wait for parties to finish
for i in active_parties:
    i.wait()

print("Done")
