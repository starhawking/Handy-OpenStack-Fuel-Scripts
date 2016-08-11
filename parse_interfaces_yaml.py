#!/usr/bin/env python

# 2016 - Collin M. (ziggit@starhawking.com)
# Simple script to list out the interfaces in an interfaces.yaml as outputted by
# fuel node --node-id 2 --disk --download
# This script will accept a filename as an argument, or attempt to default to 
# reading an interfaces.yaml at the current directory

import yaml
import argparse
from prettytable import PrettyTable


parser = argparse.ArgumentParser()
parser.add_argument('interface_yaml', nargs='?', default='interfaces.yaml')
args=parser.parse_args()

with open(args.interface_yaml) as f:
    interfaces = yaml.load(f)


headers = ['ID','Name','MAC','Type','State']
columns = ['id','name','mac','type','state']


# All bond  keys:
# ['name', 'bond_properties', 'interface_properties', 'mac', 'state', 'mode', 'slaves', 'assigned_networks', 'offloading_modes', 'type']
bond_headers = ['Name','MAC','Mode','Slaves','Assigned Networks']
bond_columns = ['name','mac','mode','slaves','assigned_networks']

interface_table_ether = PrettyTable(headers)
interface_table_bond = PrettyTable(bond_headers)

[ interface_table_ether.add_row(map( lambda x: n[x], columns)) for n in interfaces if 'ether' in n['type'] ]
[ interface_table_bond.add_row(map( lambda x: n[x], bond_columns)) for n in interfaces if 'bond' in n['type'] ]

print interface_table_ether
print interface_table_bond
