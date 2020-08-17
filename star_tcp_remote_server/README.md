# TCP Star Topology MPC Simulation

A mininet simulation to showcase MPC with a large number of parties following the star topology
with one machine acting as an isolated server and another hosting all nodes (without mininet).

# Prerequisites

You will have to change the Server IP and Client IP inside of summation.py and server.py

Also, Editing the number of desired rounds takes place in both summation.py and server.py

## Running the Simulation

Execute the client side script with

```
sudo python3 simulation.py -p [number of parties] -n [number of open ports on server side]
```

Then execute server side script with

```
sudo python3 server.py -H [number of parties] -P [number of open ports on server side]
```
