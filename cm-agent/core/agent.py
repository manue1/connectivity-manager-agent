#!/usr/bin/python

import logging
import json
import re
from clients.keystone import Client as KeystoneClient
from clients.nova import Client as NovaClient
from clients.neutron import Client as NeutronClient
from clients.ovs import Client as OVSClient

__author__ = 'beb'

class Agent(object):

    def __init__(self):
        self.cloud = Cloud()

    def list_hypervisors(self):
        cloud_info = {}
        hypervisors = self.cloud.read_hypervisor_info()
        logging.info('Getting list of hypervisors .. %s', hypervisors)
        servers = self.cloud.read_server_info()
        logging.info('### Server list .. %s', servers)
        server_ips = self.cloud.get_server_ips()
        logging.info('### Server ips .. %s', server_ips)

        for k, v in hypervisors.items():
            cloud_info[k] = v
            server_id = [print_server_hypervisor_info(servers, k)]
            cloud_info[k]['servers'][server_id] = {}
            cloud_info[k]['servers'][server_id] =

        logging.info('Cloud info .. %s', cloud_info)
        return hypervisors

    def list_qoss(self):
        pass


class Cloud(object):
    def __init__(self):
        self.keystoneclient = KeystoneClient()
        self.endpoint = self.keystoneclient.get_endpoint(service_type='network', endpoint_type=None)
        self.novaclient = NovaClient()
        self.neutronclient = NeutronClient(self.endpoint, self.keystoneclient.get_token())
        self.ovsclient = OVSClient()


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

    def get_server_ips(self):
        servers = self.novaclient.get_servers()
        ips = {}
        for server in servers:
            ips = get_server_ip(server)
            logging.info('Getting IP %s for server %s', ips, server)
        return ips

    def get_neutron_port(self, ip):
        port = self.neutronclient.get_ports(ip)
        logging.info('Getting Neutron port ID %s for IP %s', port, ip)
        return port

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


def get_server_ip(server):
    ips = []
    if hasattr(server, 'addresses'):
        for interface in server.addresses.values():
            ips.append(interface[0]['addr'])
    return ips

def print_server_hypervisor_info(serv, hypervisor):
    server_match = []
    for servers in serv.values():
        if servers['OS-EXT-SRV-ATTR:hypervisor_hostname'] == hypervisor:
            server_match.append(servers['hostId'])
    logging.info('Getting servers for matching hypervisor: %s', server_match)
    return server_match

def read_port_info(interfaces, server_port):
    end = re.search(server_port, interfaces).start()
    start = end - 75
    ovs_port = re.findall("(qvo.*?[^\'])\"", interfaces[start:end])
    logging.info('Getting OVS port: %s, for Neutron Port ID: %s', ovs_port, server_port)
    return ovs_port