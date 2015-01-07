#!/usr/bin/python

import logging
from clients.keystone import Client as KeystoneClient
from clients.nova import Client as NovaClient
from clients.neutron import Client as NeutronClient
from clients.ovs import Client as OVSClient

__author__ = 'beb'

class Agent(object):

    def __init__(self):
        self.cloud = Cloud()
        self.host = Host()

    def list_hypervisors(self):
        hypervisors = self.cloud.read_hypervisor_info()
        logging.info('Getting list of hypervisors .. %s', hypervisors)
        return hypervisors

    def list_servers(self):
        servers = self.cloud.read_server_info()
        logging.info('Getting list of all servers .. %s', servers)
        return servers

    def print_server_hypervisor(self, serv):
        server_match = {}
        for servers in serv.values():
            server_match[servers['OS-EXT-SRV-ATTR:hypervisor_hostname']] = servers['hostId']
        logging.info('Getting servers for matching hypervisor %s: %s', server_match, serv)
        return server_match

    def list_qoss(self):
        pass


class Cloud(object):
    def __init__(self):
        self.keystoneclient = KeystoneClient()
        self.endpoint = self.keystoneclient.get_endpoint(service_type='network', endpoint_type=None)
        self.novaclient = NovaClient()
        self.neutronclient = NeutronClient(self.endpoint, self.keystoneclient.get_token())

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
        logging.info('Reading info of all hypervisors %s', host_info)
        return host_info

    def read_server_info(self):
        server_info = {}
        servers = self.novaclient.get_servers()
        for server in servers:
            server_info[server.hostId] = {}
            server_info[server.hostId] = server._info
        logging.info('Reading info of all servers %s', server_info)
        return server_info

    def merge_server_info(self):
        servers = self.novaclient.get_servers()
        ips = {}
        for server in servers:
            ips = self.get_server_ip(server)
            logging.info('Getting IP %s for server %s', ips, server)
        return ips

    def get_server_ip(self, server):
        ips = []
        if hasattr(server, 'addresses'):
            for interface in server.addresses.values():
                ips.append(interface[0]['addr'])
        return ips

    def get_neutron_port(self, ip):
        port = self.neutronclient.get_ports(ip)
        logging.info('Getting Neutron port ID %s for IP %s', port, ip)
        return port


class Host(object):

    def __init__(self):
        self.ovsclient = OVSClient()

    def list_interfaces_hypervisor(self, hypervisor, hypervisors):
        interfaces = {}
        for k,v in hypervisors.items():
            if k == hypervisor:
                for k_inner, v_inner in v.items():
                    if k_inner == 'ip':
                        ip = v_inner
                        interfaces = self.ovsclient.list_interfaces(ip)
                        logging.info('Getting OVS interfaces %s for IP %s', interfaces, ip)
        return interfaces

    def read_port_info(self, interfaces, server_port):
        
        pass


class QoS(object):
    pass