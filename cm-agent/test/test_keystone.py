#!/usr/bin/python
from keystoneclient.v3.client import Client as KeystoneClient

__author__ = 'beb'

AUTH_URL_KEYSTONE = 'http://192.168.120.15:5000/v2.0'
AUTH_URLv2 = 'http://192.168.120.15:5000/v2.0'
AUTH_URL = 'http://192.168.120.15:5000/v3'
USERNAME = 'demo'
PASSWORD = 'pass'
TENANT_NAME = 'demo'

if __name__ == '__main__':

    kwargs = {'tenant_name': TENANT_NAME, 'username': USERNAME, 'password': PASSWORD}

    keystone = KeystoneClient(auth_url=AUTH_URL, **kwargs)

    keystone.authenticate()
    print keystone.auth_token
    print keystone.tenant_id
    print keystone.tenant_name
    print keystone.project_id
    print keystone.project_name