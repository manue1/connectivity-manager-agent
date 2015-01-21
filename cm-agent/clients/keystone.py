#!/usr/bin/python

from keystoneclient.v2_0.client import Client as KeystoneClient
from clients import util

__author__ = 'beb'


class Client(object):
    def __init__(self):
        self.ks_args = util.get_credentials()
        self.ksclient = KeystoneClient(**self.ks_args)

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
