#!/usr/bin/python

import logging
from clients.nova import Client as NovaClient
from clients.ovs import Client as OVSClient

__author__ = 'beb'

class Agent(object):

    def __init__(self):
        self.cloud = Cloud()

    def list_hypervisors(self):
        hypervisors = self.cloud.read_hypervisor_info()
        logging.debug('Getting list of hypervisors .. %s', hypervisors)
        return hypervisors

    # just for testing
    def list_servers(self):
        servers = self.cloud.read_server_info()
        logging.debug('Getting list of all servers .. %s', servers)
        return servers

    # just for testing
    def match_servers(self, serv):
        match = self.cloud.match_server_hypervisor(serv)
        return match

    def print_server_hypervisor(self, serv):
        server_match = {}
        for servers in serv.values():
            server_match.append(servers['OS-EXT-SRV-ATTR:hypervisor_hostname'])
        return server_match

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
            host_info[hypervisor.hypervisor_hostname] = {}
            # host_info[hypervisor.id]['all'] = hypervisor._info
            host_info[hypervisor.hypervisor_hostname]['id'] = hypervisor.id
            host_info[hypervisor.hypervisor_hostname]['ip'] = hypervisor.host_ip
            host_info[hypervisor.hypervisor_hostname]['vm_count'] = hypervisor.running_vms
            host_info[hypervisor.hypervisor_hostname]['cpu_used'] = hypervisor.vcpus_used
            host_info[hypervisor.hypervisor_hostname]['cpu_total'] = hypervisor.vcpus
            host_info[hypervisor.hypervisor_hostname]['ram_free'] = hypervisor.free_ram_mb
        return host_info

    def read_server_info(self):
        server_info = {}
        servers = self.novaclient.get_servers()
        for server in servers:
            server_info[server.hostId] = {}
            server_info[server.hostId] = server._info
        return server_info

    def match_server_hypervisor(self, servers):
        return ', '.join("%s=%r" % (key,val) for (key,val) in servers.iteritems())

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