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

    # This test includes all others
    hypervisors = agent.list_hypervisors()

    #servers = agent.cloud.read_server_info()

    #hypervisors_servers = get_server_hypervisor_info(servers)

    #server_ips = agent.cloud.get_server_ips()

    #neutronport = agent.cloud.get_neutron_port('172.24.4.3')

    #interfaces = agent.cloud.list_interfaces_hypervisor('control', hypervisors)

    #port_info = get_port_id(interfaces, neutronport)

    # Test QoS
    #host = Host('control')
    #qos = agent.host.list_qos_hypervisor('192.168.120.15')

    # Test get port for QoS
    #host = Host('control')
    #ports = host.list_ports_hypervisor('192.168.120.15')
    #qoss = host.list_qos_hypervisor('192.168.120.15')