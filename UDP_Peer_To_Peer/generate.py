
import nacl.utils
from nacl.public import PrivateKey, PublicKey
from nacl.encoding import Base64Encoder
import argparse
import ipaddress

def convert_key_to_string(key):

    return key.encode(encoder=nacl.encoding.Base64Encoder).decode('utf-8')


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--members", action="store", required=True, type=int, default=0, help="party size")
args = parser.parse_args()

num_members = args.members
port = 8888




f = open("configs/config.ini", "w")
for i in range(num_members):

    #generate public and private key
    private_key = PrivateKey.generate()
    public_key = private_key.public_key

    f.write("[Party {}]\n".format(i))
    f.write("port = {}\n".format(port))
    f.write("public = {}\n".format(convert_key_to_string(public_key)))
    f.write("private = {}\n".format(convert_key_to_string(private_key)))
    f.write("\n")
    port += 1
f.close()
