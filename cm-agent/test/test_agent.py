#!/usr/bin/python

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

    #for hypervisor in hypervisors:
    #    print agent.cloud.read_hypervisor_server_info(hypervisor)