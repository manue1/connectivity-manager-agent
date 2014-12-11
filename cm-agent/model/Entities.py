#!/usr/bin/python

from clients.nova import Client as NovaClient

__author__ = 'beb'

class Cloud(object):
    def __init__(self):
        self.novaclient = NovaClient()

    def read_hypervisor_info(self):
        host_info = {}
        hypervisors = self.novaclient.get_hypervisors()
        for hypervisor in hypervisors:
            #host_info[hypervisor.hypervisor_hostname] = hypervisor._info
            host_info[hypervisor.hypervisor_hostname] = {}
            host_info[hypervisor.hypervisor_hostname]['ip'] = hypervisor.host_ip
            host_info[hypervisor.hypervisor_hostname]['vm_count'] = hypervisor.running_vms
            host_info[hypervisor.hypervisor_hostname]['cpu_used'] = hypervisor.vcpus_used
            host_info[hypervisor.hypervisor_hostname]['cpu_total'] = hypervisor.vcpus
            host_info[hypervisor.hypervisor_hostname]['ram_free'] = hypervisor.free_ram_mb
        return host_info

class Host(object):
    pass

class Switch(object):
    pass

class Ports(object):
    pass

class QoS(object):
    pass
