# TCP Star Topology MPC Simulation

A mininet simulation to showcase MPC with a large number of parties following the star topology


### Prerequisites

* Python3 (Python 3.8 was used)

* Pip3 (used to install missing packages. Example: pip3 install pynacl)

* Mininet

	See official website for instructions

	Note: I used 'Option 2: Native Installation from Source'

	http://mininet.org/download/

## Running the Simulation

```
sudo python3 simulation.py -p [number of parties] -n [number of open ports on server side]
```

if '-n' is not given it will default to 10.

Note: sudo is required for mininet

## Fixing Error on Launch

If the program halts unexpectedly during execution run the following command

```
sudo mn -c
```
**If this is not executed after an error occurred you may see errors when trying to restart the simulation**


## Built With

* [Mininet](http://www.mininet.org) - The simulation framework

## Authors

* **Aleksei Bingham** - simulation.py, summation.py, generate.py
* **Joe Near** - node.py, server.py, constants.py
* **Zachary Ward** - node.py, server.py, constants.py
