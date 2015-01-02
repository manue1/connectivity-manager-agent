#!/usr/bin/python

from neutronclient.neutron import client as NeutronClient

__author__ = 'beb'

class Client(object):
    def __init__(self, endpoint, token):
        self.neutron = NeutronClient.Client('2.0', endpoint_url=endpoint, token=token)

    def list_ports(self):
        res = []
        lst = self.neutron.list_ports()
        for pt in lst.get('ports'):
            ips = {}
            for _ips in pt.get('fixed_ips'):
                ips[_ips.get('subnet_id')] = _ips.get('ip_address')
            print ips
        return res

    def get_ports(self, unit):
        ports = []
        lst = self.neutron.list_ports()
        for pt in lst.get('ports'):
            for subnet, ip in unit.ips.iteritems():
                for net in pt.get('fixed_ips'):
                    if ip == net.get('ip_address'):
                        ips = {net.get('subnet_id'): ip}
            for subnet, ip in unit.floating_ips.iteritems():
                for net in pt.get('fixed_ips'):
                    if ip == net.get('ip_address'):
                        ips = {net.get('subnet_id'): ip}
        return ports