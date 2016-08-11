#!/usr/bin/env python

# 2016 - Collin M. ziggit@starhawking.com
# Script to gather updated nic information from a local node deployed by fuel after updating NICs
# This script will be run from the node its self and will generate a set of SQL statements that can be used to update Nailgun's database
# The easiest way to use this script would be to tee the output to a file, copy that to the fuel node, and pipe the results into psql
# node-4# python gather_nic_info.py | tee node-4-interfaces.sql
# fuel# cat node-4-interfaces.sql | dockerctl shell postgres sudo -u postgres psql -d "nailgun"
# You will want to manually review the generated sql statements before running them.



import re
import subprocess
from xml.etree import ElementTree
import yaml

INTERFACE_ELEMENTS = ['logicalname','serial','businfo']

def get_yaml():
    with open('/etc/astute.yaml') as f:
        return yaml.load(f)

def get_node_id():
    try:
        with open('/etc/nailgun_uid') as f:
            return f.read()
    except:
        print "Please manually set the Node ID in the script"
        # Uncomment the follow line, and update with the node's UID
        # return 148

def get_pxe_ip(astute_yaml,node_id):
    node_ip = [v for k,v in astute_yaml['network_metadata']['nodes'].items() if v['uid'] == node_id ][0]['network_roles']['admin/pxe']
    return node_ip

def collect_interfaces():
    lshw_output = subprocess.check_output('lshw -xml -c network -quiet', stderr=None, shell=True)
    all_nics = ElementTree.fromstring(lshw_output)
    nics = [x for x in all_nics if 'PCI' in x.attrib['handle']]
    return nics

def get_nic_attr(nic_attrs):
    nic=dict(map(lambda element: (element, nic_attrs.find(element).text),INTERFACE_ELEMENTS))
    nic['businfo']=re.search('(?<=pci@).*',nic['businfo']).group(0)
    return nic

def gen_sql_cmds(uid,nics, pxe_ip=None):
    print("SELECT id, node_id, pxe, name, mac, ip_addr, state, parent_id, bus_info FROM node_nic_interfaces WHERE node_id = '%s';" % uid )
    print("SELECT id, hostname ,uuid ,ip ,mac, status, online  FROM nodes WHERE id = '%s';" % uid )

    for nic in nics:
        if nic['logicalname'] == 'eth0':
            print("UPDATE nodes SET mac = '%s' WHERE id = '%s';" % ( nic['serial'], uid ))
            if [ pxe_ip != None ]:
                print("UPDATE node_nic_interfaces SET ip_addr = '%s' WHERE node_id = '%s' AND name = '%s';" % (pxe_ip, uid, nic['logicalname']))
                print("UPDATE nodes SET ip = '%s' WHERE id = '%s';" % (pxe_ip, uid))
                

        print("UPDATE node_nic_interfaces SET mac = '%s', bus_info = '%s' WHERE node_id = '%s' AND name = '%s';" % ( nic['serial'], nic['businfo'], uid, nic['logicalname']))

    print("SELECT id, node_id, pxe, name, mac, ip_addr, state, parent_id, bus_info FROM node_nic_interfaces WHERE node_id = '%s';" % uid )
    print("SELECT id, hostname ,uuid ,ip ,mac, status, online  FROM nodes WHERE id = '%s';" % uid )

              

interfaces = collect_interfaces()

nics = [ get_nic_attr(nic) for nic in interfaces ]

uid = get_node_id()

astute = get_yaml()
            
              
pxe_ip = get_pxe_ip(astute,uid)

# for nic in nics:
#    print("%s %s %s" % (nic['serial'],nic['logicalname'],nic['businfo']))


gen_sql_cmds(uid,nics,pxe_ip=pxe_ip)
