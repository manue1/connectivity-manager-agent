__author__ = 'beb'

from model.Entities import Cloud

class Agent(object):

    def __init__(self):
        self.cloud = Cloud()

    def list_hypervisors(self):
        hypervisors = self.cloud.read_hypervisor_info()
        return hypervisors

    def select_hypervisor(self):
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