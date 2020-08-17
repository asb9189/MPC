# TCP Star Topology MPC Simulation (No Mininet)

Simulation to showcase MPC with a large number of parties following the star topology
without the use of mininet.

# Prerequisites

you will need to change the IP's used inside of summation.py

## Running the Simulation

```
sudo python3 simulation.py -p [number of parties] -n [number of open ports on server side]
```

if option -n is not given it will default to 10.
