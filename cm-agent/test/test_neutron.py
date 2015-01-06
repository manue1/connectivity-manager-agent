#!/usr/bin/python

from clients.neutron import Client as NeutronClient
from clients.keystone import Client as KeystoneClient
from core import agent

__author__ = 'beb'


if __name__ == '__main__':

    ksclient = KeystoneClient()

    neutron = NeutronClient(agent._get_endpoint('network'), ksclient.get_token())

    ports = neutron.list_ports()
    print ports

    port = neutron.get_ports('10.0.0.2')
    print port