# WiNG LLDP Collector 
## wing_lldp_collector.py
### Purpose
This script will go through each device on a WiNG controller and gather the lldp neighbor system name and port id and saves this to a csv to quickly identify an LLDP Neighbor.

### User Input Data
###### lines 10-16
```
#Wing Controller info
wlc = "<IP ADDRESS OR DNS NAME>"
login = {"user":"<NAME>","password":"<PASSWORD>"}

# RF-Domain the controller is assigned - this rf-domain will be skipped to not check for devices
CentralDomain = "<RF-DOMAIN>"
```
### Requirements
The python requests module will need to be installed