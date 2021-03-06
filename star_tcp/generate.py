
#Author: Aleksei Bingham

"""
generate.py creates the config.ini file found in the configs directory.
This files contain important information for each client such as their public / private key,
IP, ID, and Port. Every party member recieves one of these config.ini files and while it does
give everyone access to everyone elses private key this issue can easily be solved by storing public / priate keys
in a database. This method saves time and allows us to run the simulation with 'pre-generated' keys.

Also, generate.py can be found across all simulations in this repository. There are minor tweaks and changes
depending on how the simulation is run (with or without mininet or single vs distributed network). Because of this,
I did not document each individual generate.py script. Understanding this will allow you to understand all of them.
"""

import nacl.utils
from nacl.public import PrivateKey, PublicKey
from nacl.encoding import Base64Encoder
import argparse
import ipaddress

def convert_key_to_string(key):
    """Turns the given PyNaCl key into a string format of utf-8

    :param key: PyNaCl public / private key

    :return: String representation of PyNaCl key

    """

    return key.encode(encoder=nacl.encoding.Base64Encoder).decode('utf-8')

def main():

    """Creates a file called config.ini in the configs directory. This file
    includes information about all other nodes such as IP, PORT, and their Public and Private Key.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--members", action="store", required=True, type=int, default=0, help="party size")
    args = parser.parse_args()

    num_members = args.members
    start_ip = ipaddress.ip_address("10.0.1.1")
    port = 8888

    #create config.ini and write informaton for each party seperated by [Party {ID}]
    f = open("configs/config.ini", "w")
    for i in range(num_members):

        #generate public and private key
        private_key = PrivateKey.generate()
        public_key = private_key.public_key

        f.write("[Party {}]\n".format(i))
        f.write("host = {}\n".format(start_ip))
        f.write("port = {}\n".format(port))
        f.write("public = {}\n".format(convert_key_to_string(public_key)))
        f.write("private = {}\n".format(convert_key_to_string(private_key)))
        f.write("\n")
        start_ip += 256
        port += 1

    f.close()

if __name__ == '__main__':
    main()
