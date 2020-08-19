
import nacl.utils
from nacl.public import PrivateKey, PublicKey
from nacl.encoding import Base64Encoder
import argparse
import ipaddress

def convert_key_to_string(key):

    return key.encode(encoder=nacl.encoding.Base64Encoder).decode('utf-8')


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--members", action="store", required=True, type=int, default=0, help="party size")
parser.add_argument("-g", "--groups", action="store", required=True, type=int, default=0, help="group size")
args = parser.parse_args()

num_members = args.members
group_size = args.groups

if group_size == 0 or num_members % group_size != 0:
    print("Error: bad arguments")
    quit()

num_groups = num_members // group_size
start_ip = ipaddress.ip_address("10.0.1.1")
host_one_eth0 = "10.0.{}.2".format(num_members)
port = 8700


#create config.ini files
for index in range(num_groups):
    
    f = open("configs/config{}.ini".format(index), "w")
    for i in range(group_size):

        #generate public and private key
        private_key = PrivateKey.generate()
        public_key = private_key.public_key

        f.write("[Party {}]\n".format(i))
        if i == 0:
            f.write("host = {}\n".format(host_one_eth0))
        else:
            f.write("host = {}\n".format(start_ip))
            start_ip += 256
        f.write("port = {}\n".format(port))
        f.write("public = {}\n".format(convert_key_to_string(public_key)))
        f.write("private = {}\n".format(convert_key_to_string(private_key)))
        f.write("\n")

    f.close()


