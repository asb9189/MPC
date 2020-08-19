# Docker-Free Simulation for Secure Federated Learning

A mininet simulation to showcase MPC with a large number of parties


### Prerequisites

* Python3

* Pip3

* Mininet

	See official website for instructions

	Note: I used 'Option 2: Native Installation from Source'

	http://mininet.org/download/

* Python Modules

	**Most of these should all be native to python but if error occurs from missing module run**

	```
	pip3 install [name-of-package]
	```

	Example

	```
	pip3 install pynacl
	```

	* ipaddress
	* argparse
	* socket
	* subprocess
	* sys
	* from abc ABCMeta, abstractmethod
	* uuid
	* json
	* select
	* threading
	* time
	* collections
	* os
	* warnings
	* configparser
	* random
	* PyNaCl (crypto lib **Not native to python. Must use pip3**)

* SVN (sudo apt-get install subversion)

## Installation

This GitHub repo has a lot of extra packages that are **not** needed for this simulation.
In order to clone the package we need we will use subversion (SVN).

Note: a new folder will be created in the current directory
after running the command below. There is no need to create a new directory.

```
svn checkout https://github.com/asb9189/Mininet/trunk/scripts/docker-free
```

## Running the Simulation

```
sudo python3 ring.py -p [number of parties]
```

Note: sudo is required for mininet

## Known Bugs

* If not enough time slept on main thread. Program will stall forever. Currently 10 seconds of sleep is used in summation.py. Feel free to edit these values if you experience issues running on large number of parties (ex: -p 1000).


## Fixing Error on Launch

If the program halts unexpectedly during execution run the following command

```
sudo mn -c
```
**If this is not executed after an error occured you may see errors when trying to restart the simulation**


## Built With

* [Mininet](http://www.mininet.org) - The simulation framework

## Authors

* **Aleksei Bingham** - simulation.py, summation.py, generate.py
* **Joe Near** - node.py, constants.py
* **Zachary Ward** - node.py, constants.py