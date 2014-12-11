#!/usr/bin/python

from clients.nova import Client as NovaClient

__author__ = 'beb'

class Agent(object):
    def __init__(self):
        self.novaclient = NovaClient()

    def read_hypervisor_info(self):

        host_info = {}
        hypervisors = self.novaclient.list_hypervisors()
        #for hypervisor in hypervisors:
        #    host_info['hostname']
