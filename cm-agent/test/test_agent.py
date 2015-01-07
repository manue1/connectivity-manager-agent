#!/usr/bin/python

import logging
from core.agent import Agent, Cloud

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

    servers = agent.list_servers()

    matches = agent.print_server_hypervisor(servers)

    serverips = agent.cloud.merge_server_info()

    neutronport = agent.cloud.get_neutron_port('172.24.4.3')

    interfaces = agent.host.list_interfaces_hypervisor('compute', hypervisors)

    port_info = agent.host.read_port_info(interfaces, neutronport)
