#!/usr/bin/python

from clients.ovs import Client

__author__ = 'beb'

if __name__ == '__main__':

    client = Client('192.168.120.15')

    ports = client.list_ports()
    print ports
