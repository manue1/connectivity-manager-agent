#!/usr/bin/python

__author__ = 'beb'

from keystoneclient.v2_0.client import Client as KeystoneClient

AUTH_URL_KEYSTONE = 'http://192.168.120.15:5000/v2.0'
AUTH_URL = 'http://192.168.120.15:5000/v2.0'
USERNAME = 'demo'
PASSWORD = 'demo'
TENANT_NAME = 'demo'

class Client(object):
    def __init__(self):
        kwargs = {'tenant_name': TENANT_NAME, 'username': USERNAME, 'password': PASSWORD}
        self.keystoneclient = KeystoneClient(auth_url=AUTH_URL, **kwargs)

    def list_tenants(self):
        tenants = self.keystoneclient.tenants.list()
        print "tenants list: %s" % tenants
        return tenants

