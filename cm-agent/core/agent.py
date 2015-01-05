#!/usr/bin/python

from clients.nova import Client as NovaClient
from clients.ovs import Client as OVSClient

__author__ = 'beb'

class Agent(object):

    def __init__(self):
        self.cloud = Cloud()

    def list_hypervisors(self):
        hypervisors = self.cloud.read_hypervisor_info()
        return hypervisors

    # just for testing
    def list_servers(self):
        servers = self.cloud.read_server_info()
        return servers

    def list_ports(self):
        pass

    def list_qoss(self):
        pass

    def list_flows(self):
        pass

    def list_queues(self):
        pass

class Cloud(object):
    def __init__(self):
        self.novaclient = NovaClient()

    def read_hypervisor_info(self):
        host_info = {}
        hypervisors = self.novaclient.get_hypervisors()
        for hypervisor in hypervisors:
            host_info[hypervisor.id] = {}
            # host_info[hypervisor.id]['all'] = hypervisor._info
            host_info[hypervisor.id]['hostname'] = hypervisor.hypervisor_hostname
            host_info[hypervisor.id]['ip'] = hypervisor.host_ip
            host_info[hypervisor.id]['vm_count'] = hypervisor.running_vms
            host_info[hypervisor.id]['cpu_used'] = hypervisor.vcpus_used
            host_info[hypervisor.id]['cpu_total'] = hypervisor.vcpus
            host_info[hypervisor.id]['ram_free'] = hypervisor.free_ram_mb
        return host_info

    def read_server_info(self):
        server_info = {}
        servers = self.novaclient.get_servers()
        for server in servers:
            server_info[server.hostId] = {}
            # server_info[server.hostId]['all'] = server._info
            server_info[server.hostId]['name'] = server.name
            server_info[server.hostId]['ip_addr'] = server.addresses
            server_info[server.hostId]['status'] = server.status
        return server_info

class Host(object):
    def __init__(self):
        self.ovsclient = OVSClient()

    def read_port_info(self):
        port_info = {}
        ports = self.ovsclient.list_ports()
        pass

class Switch(object):
    pass

class Ports(object):
    pass

class QoS(object):
    pass

def _get_endpoint(service_type, endpoint_type=None):
    from clients import keystone
    # ##Init keystone client
    ksclient = keystone.Client()
    endpoint = ksclient.get_endpoint(service_type=service_type, endpoint_type=endpoint_type)
    return endpoint