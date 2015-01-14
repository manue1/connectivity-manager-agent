#!/usr/bin/python

from clients.nova import Client

__author__ = 'beb'

AUTH_URL_KEYSTONE = 'http://192.168.120.15:5000/v2.0'
AUTH_URL = 'http://192.168.120.15:5000/v2.0'

USERNAME = 'demo'
PASSWORD = 'pass'
TENANT_NAME = 'demo'

if __name__ == '__main__':

    client = Client()

    hypervisors = client.get_hypervisors()
    for hypervisor in hypervisors:
        print hypervisor._info

    servers = client.get_servers()
    for server in servers:
        print server._info

    servers = client.get_hypervisor_servers('control')
    for server in servers:
        print server