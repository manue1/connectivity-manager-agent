#!/usr/bin/python

from keystoneclient.v2_0.client import Client as KeystoneClient

__author__ = 'beb'

USERNAME = 'admin'
PASSWORD = 'pass'
TENANT_NAME = 'demo'
AUTH_URLv2 = 'http://192.168.120.15:5000/v2.0'

class Client(object):
    def __init__(self):
        creds = {}
        creds['tenant_name'] = TENANT_NAME
        creds['username'] = USERNAME
        creds['password'] = PASSWORD
        creds['auth_url'] = AUTH_URLv2
        self.ksclient = KeystoneClient(**creds)

    def get_endpoint(self, **kwargs):
        if kwargs.get('region_name'):
            return ''.join(self.ksclient.service_catalog.get_urls(
                service_type=kwargs.get('service_type') or 'orchestration',
                attr='region',
                filter_value=kwargs.get('region_name'),
                endpoint_type=kwargs.get('endpoint_type') or 'publicURL'))
        return ''.join(self.ksclient.service_catalog.get_urls(
            service_type=kwargs.get('service_type') or 'orchestration',
            endpoint_type=kwargs.get('endpoint_type') or 'publicURL'))

    def get_token(self):
        return self.ksclient.auth_token

