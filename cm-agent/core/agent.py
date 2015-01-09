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
        interfaces = {}
        hypervisors = self.cloud.read_hypervisor_info()
        logging.info('Getting list of hypervisors .. %s', hypervisors)
        servers = self.cloud.read_server_info()
        logging.info('Getting list of servers .. %s', servers)
        hypervisors_servers = get_server_hypervisor_info(servers)
        logging.info('Getting list of servers matched with hypervisor .. %s', hypervisors_servers)
        server_ips = self.cloud.get_server_ips()
        logging.info('Getting list of all server IPs.. %s', server_ips)

        for kh, vh in hypervisors.items():
            cloud_info[kh] = vh
            logging.info('### vh: %s', vh.get('ip'))
            cloud_info[kh]['servers'] = {}
            interfaces[kh] = Host(kh).list_interfaces_hypervisor(hypervisors)
            logging.info('Interfaces for %s : %s ... ', kh, interfaces)
            for khs, vhs in hypervisors_servers.items():
                if kh == khs:
                    cloud_info[kh]['servers'][vhs] = {}
                    for ks, vs in servers.items():
                        if ks == vhs:
                            cloud_info[kh]['servers'][vhs]['name'] = vs.get('name')
                            for ki, vi in server_ips.items():
                                if ki == vhs:
                                    cloud_info[kh]['servers'][vhs]['ip'] = vi[0]
                                    neutron_port_id = self.cloud.get_neutron_port(vi[0])
                                    cloud_info[kh]['servers'][vhs]['neutron_port'] = neutron_port_id
                                    cloud_info[kh]['servers'][vhs]['ovs_port_id'] = get_port_id(interfaces[kh],
                                                                                                neutron_port_id)[0]
                                    cloud_info[kh]['servers'][vhs]['qos'] = {}
                                    cloud_info[kh]['servers'][vhs]['qos'] = Host(kh).list_qos_hypervisor(vh.get('ip'))

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
            ips[server.hostId] = get_server_ip(server)
        logging.info('All server IPs %s', ips)
        return ips

    def get_neutron_port(self, ip):
        port = self.neutronclient.get_ports(ip)
        logging.info('Getting Neutron port ID %s for IP %s', port, ip)
        return port


class Host(object):
    def __init__(self, hypervisor):
        self.hypervisor = hypervisor
        self.ovsclient = OVSClient()

    # ToDO: Use hypervisor IP as input instead, can save one for?!
    def list_interfaces_hypervisor(self, hypervisors):
        interfaces = {}
        for k, v in hypervisors.items():
            if k == self.hypervisor:
                for k_inner, v_inner in v.items():
                    if k_inner == 'ip':
                        ip = v_inner
                        interfaces = self.ovsclient.list_interfaces(ip)
                        logging.info('Getting OVS interfaces %s for IP %s', interfaces, ip)
        return interfaces

    def list_qos_hypervisor(self, hypervisor_ip):
        qos = self.ovsclient.list_qos(hypervisor_ip)
        logging.info('Getting OVS QoS %s for IP %s', qos, hypervisor_ip)
        return qos


def get_server_ip(server):
    ips = []
    if hasattr(server, 'addresses'):
        for interface in server.addresses.values():
            ips.append(interface[0]['addr'])
    return ips


def get_server_hypervisor_info(servers):
    server_match = {}
    for server in servers.values():
        server_match[server['OS-EXT-SRV-ATTR:hypervisor_hostname']] = server['hostId']
    logging.info('Getting servers for matching hypervisor: %s', server_match)
    return server_match


def get_port_id(interfaces, server_port):
    end = re.search(server_port, interfaces).start()
    start = end - 75
    ovs_port = re.findall("(qvo.*?[^\'])\"", interfaces[start:end])
    logging.info('Getting OVS port: %s, for Neutron Port ID: %s', ovs_port, server_port)
    return ovs_port