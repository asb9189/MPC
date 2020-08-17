# TCP Star Topology With an Isolated Server MPC Simulation

Simulation to showcase MPC with a large number of parties following the star topology
with one machine hosting all the nodes and another acting as the server in a distributed network.

## Running the Simulation

Execute the client side script with

```
sudo python3 simulation.py -p [number of parties] -n [number of open ports on server side]
```

Then execute server side script with

```
sudo python3 server.py -H [number of parties] -P [number of open ports on server side]
```
