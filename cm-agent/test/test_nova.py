#!/usr/bin/python

from clients.nova import Client

__author__ = 'beb'


if __name__ == '__main__':

    client = Client()

    hypervisors = client.get_hypervisors()
    for hypervisor in hypervisors:
        print hypervisor._info

    servers = client.get_servers()
    for server in servers:
        print server._info
