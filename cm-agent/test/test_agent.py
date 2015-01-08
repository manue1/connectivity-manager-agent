#!/usr/bin/python

import logging
from core.agent import *

__author__ = 'beb'

AUTH_URL_KEYSTONE = 'http://192.168.120.15:5000/v2.0'
AUTH_URL = 'http://192.168.120.15:5000/v2.0'

USERNAME = 'admin'
PASSWORD = 'pass'
TENANT_NAME = 'admin'

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s_%(process)d:%(lineno)d [%(levelname)s] %(message)s',level=logging.DEBUG)

    agent = Agent()

    hypervisors = agent.list_hypervisors()

    #servers = agent.cloud.read_server_info()

    #matches = print_server_hypervisor_info(servers, 'control')

    #serverips = agent.cloud.get_server_ips()

    #neutronport = agent.cloud.get_neutron_port('172.24.4.3')

    #interfaces = agent.cloud.list_interfaces_hypervisor('control', hypervisors)

    #port_info = read_port_info(interfaces, neutronport)
