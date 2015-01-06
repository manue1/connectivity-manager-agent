#!/usr/bin/python

from clients.ovs import Client

__author__ = 'beb'

if __name__ == '__main__':

    client = Client()

    ports = client.list_ports('192.168.120.15')
    print ports

    interfaces = client.list_interfaces('192.168.120.15')
    print interfaces