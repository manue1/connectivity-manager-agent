#!/usr/bin/python

from novaclient.v1_1.client import Client as NovaClient

__author__ = 'beb'

AUTH_URLv2 = 'http://192.168.120.15:5000/v2.0'
AUTH_URLv3 = 'http://192.168.120.15:5000/v3'
USERNAME = 'admin'
PASSWORD = 'pass'
TENANT_NAME = 'demo'

class Client(object):
    def __init__(self):
        kwargs = [USERNAME, PASSWORD, TENANT_NAME, AUTH_URLv2]
        self.novaclient = NovaClient(*kwargs)

    def get_hypervisors(self):
        hypervisors = self.novaclient.hypervisors.list()
        return hypervisors
