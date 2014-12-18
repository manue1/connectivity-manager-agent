#!/usr/bin/python

from core.agent import Agent

__author__ = 'beb'

AUTH_URL_KEYSTONE = 'http://192.168.120.15:5000/v2.0'
AUTH_URL = 'http://192.168.120.15:5000/v2.0'

USERNAME = 'demo'
PASSWORD = 'pass'
TENANT_NAME = 'demo'

if __name__ == '__main__':

    agent = Agent()

    hypervisors = agent.list_hypervisors()
    print hypervisors