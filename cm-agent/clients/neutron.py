#!/usr/bin/python

from neutronclient.neutron import client as NeutronClient

__author__ = 'beb'

class Client(object):
    def __init__(self, endpoint, token):
        self.neutron = NeutronClient.Client('2.0', endpoint_url=endpoint, token=token)

    def list_ports(self):
        ips = {}
        lst = self.neutron.list_ports()
        for pt in lst.get('ports'):
            for _ips in pt.get('fixed_ips'):
                ips[pt.get('id')] = _ips.get('ip_address')
        return ips

    def get_ports(self, ip):
        lst = self.list_ports()
        return next((k for k, v in lst.items() if v == ip), None)