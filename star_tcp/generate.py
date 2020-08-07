
#Author: Aleksei Bingham

'''
generate.py creates the config.ini file found in the configs directory.
This files contain important information for each client such as their public / private key,
IP, ID, and Port. Every party member recieves one of these config.ini files and while it does
give everyone access to everyone elses private key this issue can easily be solved by storing public keys
in a database. This method saves time and allows us to run the simulation with 'pre-generated' keys.
'''


import nacl.utils
from nacl.public import PrivateKey, PublicKey
from nacl.encoding import Base64Encoder
import argparse
import ipaddress

def convert_key_to_string(key):
    '''turn the given PyNaCl key into a string format of utf-8'''

    return key.encode(encoder=nacl.encoding.Base64Encoder).decode('utf-8')

def main():
    
    #command line arguments for the number of parties
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
