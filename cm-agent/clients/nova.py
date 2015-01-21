#!/usr/bin/python

from novaclient import client
from clients import util

__author__ = 'beb'


class Client(object):
    def __init__(self):
        self.args = util.read_properties()
        self.novaclient = client.Client('2', self.args['os_username'], self.args['os_password'], self.args['os_tenant'], self.args['os_auth_url'])

    def get_hypervisors(self):
        hypervisors = self.novaclient.hypervisors.list()
        return hypervisors

    def get_servers(self):
        servers = self.novaclient.servers.list()
        return servers
