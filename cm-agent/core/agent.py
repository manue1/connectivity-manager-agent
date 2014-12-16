#!/usr/bin/python

from model.entities import Cloud

__author__ = 'beb'

class Agent(object):

    def __init__(self):
        self.cloud = Cloud()

    def list_hypervisors(self):
        hypervisors = self.cloud.read_hypervisor_info()
        return hypervisors

    def select_hypervisor(self):
        self.list_hypervisors()
        pass

    def list_ports(self):
        pass

    def list_qoss(self):
        pass

    def list_flows(self):
        pass

    def list_queues(self):
        pass

    pass