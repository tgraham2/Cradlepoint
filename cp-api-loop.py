#!/usr/bin/python
# contact all CP routers
#
import json
import requests

routerURL = 'https://www.cradlepointecm.com/api/v2/routers/'

headers = {
        'X-CP-API-ID': '6576d395',
        'X-CP-API-KEY': 'db1915a59ef1a9e87b62e384bb141baf',
        # RO keys
        'X-ECM-API-ID': '38364587-2faf-493f-98a6-4c29f9fc45cf',
        'X-ECM-API-KEY': '3263a0543e52f847d822ecc875609fa9534471b0',
        'Content-Type': 'application/json' 
}

from cpssh_lib import cpssh
from cssh_lib import csshpw
username = 'noc_offshore'
pw=csshpw(username)
localuser = 'tgraham'
localpw=csshpw(localuser)

def processRecord(r,fw):
    global username,pw,localuser,localpw
    if r['state'] == 'online':
        # connect to CP
        s=cpssh(username,pw,r['ipv4_address'])
        if r['description']:
            desc = r['description'].strip()
        else:
            desc = ' '
        if s.connected:
            desc =(s.send_serial(localuser,localpw))
            fw.write('%s\t%s\t%s\t%s\t%s\n' %  \
                     (s.routerid,r['description'],r['name'], \
                     r['ipv4_address'],r['serial_number'] ) )
        else:
             fw.write('%s\t%s\t%s\t%s\t%s\n' %  \
                     ("Unknown",r['description'],r['name'], \
                     r['ipv4_address'],r['serial_number'] ) )
    else:
        fw.write('%s\t%s\t%s\t%s\t%s\n' %  \
                ("No Connection",r['description'],r['name'], \
                r['ipv4_address'],r['serial_number'] ) )

def upDate(rURL):
    headers = {
        'X-CP-API-ID': '6576d395',
        'X-CP-API-KEY': 'db1915a59ef1a9e87b62e384bb141baf',
        # RO keys
        'X-ECM-API-ID': '38364587-2faf-493f-98a6-4c29f9fc45cf',
        'X-ECM-API-KEY': '3263a0543e52f847d822ecc875609fa9534471b0',
        'Content-Type': 'application/json' 
    }
    # to update, pull the resource for the router
    # get record for individual router
    # data in resp['key']
    #resourceURL = routers_resp['data'][i]['resource_url']
    r = requests.get(rURL, headers=headers)
    resp = r.json()
    print 'GET:',r.reason
    #
    payload = {} 
    # set payload for update #payload = {'key' : 'value'}
    #
    #update record 
    r = requests.put(resourceURL,json=payload, headers=headers)   
    resp = r.json()
    print "UPD:",r.reason
    
def dbLoop(resultFile):
    global routerURL
    url = routerURL
    with open(resultFile,'w') as fw:
        while url:
            # get group of router records
            req = requests.get(url, headers=headers)
            routers_resp = req.json()

            for i,j in enumerate(routers_resp['data']):
                # get resource record for each router
                # data is in j['key']
                #
                #read_only
                #processRecord(j,fw) # get data from aggregate
                print j['name'],j[ipv4_address]
                #
                upDate(routers_resp['data'][i]['resource_url'])
            #
            # Get URL for next set of resources
            url = routers_resp['meta']['next']
    
if __name__ == '__main__':
    dbLoop('cp-check-out.txt')
