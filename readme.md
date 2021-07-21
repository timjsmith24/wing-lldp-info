# WiNG LLDP Collector 
## wing_lldp_collector.py
### Purpose
This script will go through each device on a WiNG controller and gather the lldp neighbor system name and port id and saves this to a csv to quickly identify an LLDP Neighbor.

### User Input Data
WiNG controller info, rf-domain of controller to skip, file name for csv output
###### lines 10-20
```
#Wing Controller info
wlc = "<IP ADDRESS OR DNS NAME>"
login = {"user":"<NAME>","password":"<PASSWORD>"}

# RF-Domain the controller is assigned - this rf-domain will be skipped to not check for devices
CentralDomain = "<RF-DOMAIN>"

#name of file - full path can be added to store in a seperate location
filename = "<CSV file name>"
```
### Outputs
#### csv file 
```
Device name, lldp neighbor name, lldp neighbor port
AP8533-PTP-RT, SR2208P, 1/0/1
AP7532-PTP-BR, USW-Switch, Port 10
AP-OFFICE-7532-01, SR2208P, 1/0/2
```
#### log file
stores any log information from the script
###### wing_lldp_collector.log
```
2021-07-21 09:48:28: root - WARNING - Skipping domain '0134': Unable to locate rf-domain manager
2021-07-21 09:48:28: root - WARNING - Skipping domain '0112': Unable to locate rf-domain manager
2021-07-21 09:48:28: root - WARNING - Skipping domain '0048': Unable to locate rf-domain manager
```
### Requirements
The python requests module will need to be installed