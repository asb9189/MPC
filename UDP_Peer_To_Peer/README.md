# UDP MPC Simulation

A Simulation to showcase MPC with a large number of parties using peer to peer communication
following the UDP protocol.

# Prerequisites

You may wish to change the amount of sleep as the number of parties grows or shrinks. At
the time of pushing this I don't know what the sleep will be set too but it is easy to find
in summation.py. There are two locations for sleep, one before starting the protocol and another
during the sending of messages to give the linux machines UDP Buffer a chance to stay caught up.

## Running the Simulation

```
sudo python3 simulation.py -p [number of parties]
```
