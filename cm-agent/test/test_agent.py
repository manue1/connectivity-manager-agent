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

    agent = Agent()

    hypervisors = agent.list_hypervisors()
    print hypervisors

    servers = agent.list_servers()
    print servers

    matches = agent.print_server_hypervisor(servers)
    logging.info('Printing matches')

    print matches

    serverips = agent.cloud.merge_server_info()
    print serverips

    interfaces = agent.host.list_interfaces_hypervisor('compute', hypervisors)
    print interfaces
