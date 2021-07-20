#!/usr/bin/env python3
import requests
import json
import warnings
import os
import logging
import multiprocessing

warnings.filterwarnings("ignore")

# Wing Controller info
wlc = "10.0.20.4"
login = {"user":"admin","password":"c0bra42b"}
# RF-Domain the controller is assigned - this rf-domain will be skipped to not check for devices
CentralDomain = 'Central'

#name of file - full path can be added to store in a seperate location
filename = 'wing_lldp_report.csv'
#filename = '/Users/timsmith/Desktop/wing_lldp_report.csv'

baseurl = 'https://{}/rest'.format(wlc)

HEADERS= {
    'Content-Type': 'application/json'
    }

#-------------------------
# logging file and info
PATH = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
	filename='{}/wing_lldp_collector.log'.format(PATH),
	filemode='a',
	level=os.environ.get("LOGLEVEL", "INFO"),
    format= '%(asctime)s: %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

def get_api_token():
    url = '{}/v1/act/login'.format(baseurl)
    try:
        r = requests.get(url, headers=HEADERS, verify=False, auth=(login['user'], login['password']), timeout=3)
    except:
        raise TypeError("API Auth request failed")
    data = json.loads(r.text)
    auth_token = data['data']['auth_token']
    return(auth_token)

def close_api_session():
    url = '{}/v1/act/logout'.format(baseurl)
    try:
        r = requests.post(url, headers=HEADERS, verify=False, timeout=3)
    except:
        raise TypeError("API close session request failed")
    try:
        data = json.loads(r.text)
    except:
        logmsg = r.text
        log_msg = "Closing sessions {} failed with message: {}".format(HEADERS['cookie'],logmsg)
        logging.error(log_msg)
        raise TypeError("Failed to close session {}".format(HEADERS['cookie']))
    if 'return_code' in data:
        if data['return_code'] != 0:
            logging.error("\n\nClosing session returned error {} for sessions {}").format(data['return_code'],HEADERS['cookie'])
        #else:
        #    print("\n\nSuccessfully closed session")

def post_api_call(url, rf_domain=None, device=None):
    url = '{}{}'.format(baseurl,url) 
    if rf_domain:
        payload = "{\n\t\"rf-domain\":\"RF_DOMAIN\"\n}"
        payload=payload.replace('RF_DOMAIN',rf_domain)
    elif device:
        payload = "{\n\t\"device\":\"DEVICE\"\n}"
        payload=payload.replace('DEVICE',device)
    else:
        payload = {}
    try:
        r = requests.post(url, headers=HEADERS, data=payload, verify=False, timeout=3)
    except:
        log_msg = "API request {} failed for site {}".format(url, rf_domain)
        logging.error(log_msg)
        raise TypeError(log_msg)
    try:
        data = json.loads(r.text)
    except:
        logmsg = r.text
        log_msg = "API post call failed with message: {}".format(logmsg)
        logging.error(log_msg)
        raise TypeError("Failed to read info from API request {}".format(url))
    if data['return_code'] == 0:
        return(data['data'])
    else:
        log_msg = "{} returned code {}\n{}".format(url,data['return_code'],data['errors'])
        raise ValueError("{}".format(data['errors']))

def lldp_collector(apname, HEADERS, mp_queue):
    url = '/v1/stats/lldp-neighbors'
    try:
        rawlldp = post_api_call(url, device=apname)
    except TypeError as e:
        print(f"{str(e)} on {apname}")
        exit()
    except:
        print(f'UNKNOWN ERROR: LLDP API Failed on {apname}')
    mp_queue.put(f"{apname}, {rawlldp[0]['dev_id']},{rawlldp[0]['port_id']}\n")
    close_api_session()


def main():
    global HEADERS
    ap_list = []
    auth_token = get_api_token()
    HEADERS['cookie']='auth_token={}'.format(auth_token)
    url = '/v1/stats/noc/domains'
    try:
        rawList = post_api_call(url)
    except TypeError as e:
        print(e)
        exit()
    except:
        print('Unknown')
        exit()
    url = '/v1/stats/wireless/ap-info'
    for domain in rawList:
        domain_name = (domain['name'])
        if domain_name == CentralDomain:
            print(f"Skipping domain '{domain_name}': Flagged as controller domain")
            continue
        try:
            ap_info = post_api_call(url, rf_domain=domain_name)
        except TypeError as e:
            print(e)
            exit()
        except ValueError as e:
            if 'Unable to locate rf-domain manager' in str(e):
                log_msg = (f"Skipping domain '{domain_name}': Unable to locate rf-domain manager")
                logging.warning(log_msg)
                print(log_msg)
                continue
            else:
                print(e)
                exit()
        except:
            print('Unknown')
            exit()
        for device in ap_info:
            ap_list.append(device['hostname'])
    #print(ap_list)
    try:
        close_api_session()
    except TypeError as e:
        print(e)
    except:
        print(f"Failed to disconnect {HEADERS['cookie']}")
    ### add some Logging?
    msg = 'Device name, lldp neighbor name, lldp neighbor port\n'
    # Sets amount of Per Device API calls to make simultaneously
    sizeofbatch = 50
    for i in range(0, len(ap_list), sizeofbatch):
        batch = ap_list[i:i+sizeofbatch]
        mp_queue = multiprocessing.Queue()
        processes = []
        auth_token = get_api_token()
        HEADERS['cookie']='auth_token={}'.format(auth_token)
        for apname in batch:
            p = multiprocessing.Process(target=lldp_collector,args=(apname, HEADERS, mp_queue))
            processes.append(p)
            p.start()
        for p in processes:
            try:
                p.join()
                p.terminate()
            except:
                print("Error occurred in thread")
        mp_queue.put('STOP')
        for line in iter(mp_queue.get, 'STOP'):
            msg += line

    with open(filename, 'w') as f:
        f.write(msg)

    

if __name__ == '__main__':
    main()