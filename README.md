# GNS3-Topology-Auto-Configurer
 Configures a GNS3 network topology connected to a management switch with ssh enabled in the devices. IP assignment & description is handled as of now.  


# Pre-requisites: 
 1. All devices in the topology should be connected to a management switch, then connected to the host running the script.
 2. The host should be able to reach all the devices in the topology using a management IP.
 3. The routers need to have ssh setup, configured, and enabled.
 4. You can either use the precompiled Windows/Linux/MacOS executables to run or you need Tkinter and certain other dependencies to # compile.
 5. Works on real Cisco devices as well (Not restricted to GNS3 topology)


# Working:
 1. Router hostname
 2. IP assignment and Interface description.
 3. Basic show commands for Cisco devices.
 4. Topology convergence using OSPF that will advertise 0.0.0.0 network on all devices.


# Future:
 Extend the configuration as per your convinience. This is just the beginning.

# Owner:
 Aswath Gopalan Yagya Narayanan (asya2181@colorado.edu)


 Copyrights Standard GPL v2.0 (a.k.a Free)
#T#H#A#N#K##Y#O#U#

