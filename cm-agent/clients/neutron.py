#!/usr/bin/python

from neutronclient.neutron import client as NeutronClient

__author__ = 'beb'

class Client(object):
    def __init__(self, endpoint, token):
        self.neutron = NeutronClient.Client('2.0', endpoint_url=endpoint, token=token)

    def list_ports(self):
        lst = self.neutron.list_ports()
        print lst
        for pt in lst.get('ports'):
            ips = {}
            for _ips in pt.get('fixed_ips'):
                ips[pt.get('id')] = _ips.get('ip_address')
            print ips
        return ips

    def get_ports(self, ip):
        ports = []
        lst = self.list_ports()
        for pt in lst:
            print pt
            if ip == pt:
                print ip
                return pt.id
