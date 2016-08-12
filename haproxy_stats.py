#!/usr/bin/env python

# 2016 - Collin M. ziggit@starhawking.com

import socket
import prettytable
import os

STAT_FILE = '/var/lib/haproxy/stats'

def socket_collect(sock_file):
    class socket_open(object):
        def __init__(self,sock_file):
            self.sock_file = sock_file
	    
        def __enter__(self):
            self.client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.client.connect(self.sock_file)
            return self.client
        def __exit__(self,type,value,traceback):
            self.client.close()
	    
    class socket_generator():
        def __init__(self,client):
            self.client = client
    
        def __iter__(self):
            return self
        def __next__(self):
            return self.next()
        def next(self):
            (result,sockfile) = self.client.recvfrom(1024)
            if sockfile != None:
                return result
            else:
                raise StopIteration()
    
    with socket_open(sock_file) as f:
        f.sendall('show stat\n')
        socket_results = socket_generator(f)
        return ''.join(socket_results)


def print_haproxy_columns(haproxy_stats):
    table = prettytable.PrettyTable(haproxy_stats.strip().split('\n')[0][2:-1].split(','))
    columns = ['pxname','svname','bin','bout','status','chkfail','chkdown','lastchg','downtime']
    [ table.add_row(row[:-1].split(',') ) for row in haproxy_stats.strip().split('\n')[1:] ]
    print table.get_string(fields=columns)

if __name__ == '__main__':
    try:
        haproxy_stats = socket_collect(STAT_FILE)
        print_haproxy_columns(haproxy_stats)
    except:
        pass
