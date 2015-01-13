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
        ports = {}
        qoss = {}
        hypervisors_servers = {}
        hypervisors = self.cloud.read_hypervisor_info()
        logging.info('Getting list of hypervisors .. %s', hypervisors)
        servers = self.cloud.read_server_info()
        logging.info('Getting list of servers .. %s', servers)

        server_ips = self.cloud.get_server_ips()
        logging.info('Getting list of all server IPs.. %s', server_ips)

        for kh, vh in hypervisors.items():
            logging.info('### vh: %s', vh.get('ip'))
            cloud_info[kh] = vh
            cloud_info[kh]['servers'] = {}

            hypervisors_servers[kh] = Host(kh).get_server_hypervisor_info(servers, kh)
            logging.info('Getting list of servers matched with hypervisor .. %s', hypervisors_servers)

            interfaces[kh] = Host(kh).list_interfaces_hypervisor(hypervisors)
            logging.info('Interfaces for %s : %s ... ', kh, interfaces)
            ports[kh] = Host(kh).list_ports_hypervisor(vh.get('ip'))
            logging.info('Ports for %s : %s ... ', kh, ports)
            qoss[kh] = get_qos(Host(kh).list_qos_hypervisor(vh.get('ip')))
            logging.info('QoS\'s for %s : %s ... ', kh, qoss)
            for hs in hypervisors_servers[kh]:
                cloud_info[kh]['servers'][hs] = {}
                for ks, vs in servers.items():
                    if ks == hs:
                        cloud_info[kh]['servers'][hs]['name'] = vs.get('name')
                        for ki, vi in server_ips.items():
                            if ki == hs:
                                cloud_info[kh]['servers'][hs]['ip'] = vi[0]
                                neutron_port_id = self.cloud.get_neutron_port(vi[0])
                                ovs_port_id = get_port_id(interfaces[kh], neutron_port_id)[0]
                                cloud_info[kh]['servers'][hs]['neutron_port'] = neutron_port_id
                                cloud_info[kh]['servers'][hs]['ovs_port_id'] = ovs_port_id
                                cloud_info[kh]['servers'][hs]['qos'] = {}
                                #for kq, vq in qoss[kh].data.items():
                                #    logging.info('### kq: %s vq: %s ... ', kq, vq)

                                #cloud_info[kh]['servers'][vhs]['qos'] = get_port_qos(ports[kh])

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
            server_info[server.id] = {}
            server_info[server.id] = server._info
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
        logging.info('Getting OVS interfaces %s :', interfaces)
        return interfaces

    def get_server_hypervisor_info(self, servers, hostname):
        server_match = []
        for server in servers.values():
            if server['OS-EXT-SRV-ATTR:hypervisor_hostname'] == hostname:
                server_match.append(server['id'])
        logging.info('Getting servers for matching hypervisor %s: %s', hostname, server_match)
        return server_match

    def list_ports_hypervisor(self, hypervisor_ip):
        ports = self.ovsclient.list_ports(hypervisor_ip)
        logging.info('Getting OVS ports: %s for Hypervisor IP: %s', ports, hypervisor_ip)
        return ports

    def list_qos_hypervisor(self, hypervisor_ip):
        qos = self.ovsclient.list_qos(hypervisor_ip)
        logging.info('Getting OVS QoS %s for IP %s', qos, hypervisor_ip)
        return qos


def get_qos(qos_raw):

    _qos_raw = qos_raw.split(',')
    logging.info('#### QoS SPLIT: %s ', _qos_raw)
    #before_keyword, keyword, after_keyword = qos_raw.partition(keyword)
    #logging.info('#### QoS after keyword', after_keyword)
    #qos_uuid_start = re.search(keyword, qos_raw).end()
    #logging.info('#### QoS start uuid', qos_uuid_start)
    #qoss_uuids.append(qos_raw[qos_uuid_start:(qos_uuid_start + 36)])
    #logging.info('#### QoS', qoss_uuids)
    # return qoss


def get_server_ip(server):
    ips = []
    if hasattr(server, 'addresses'):
        for interface in server.addresses.values():
            ips.append(interface[0]['addr'])
    return ips


def get_port_id(interfaces, server_port):
    end = re.search(server_port, interfaces).start()
    start = end - 75
    ovs_port = re.findall("(qvo.*?[^\'])\"", interfaces[start:end])
    logging.info('Getting OVS port: %s, for Neutron Port ID: %s', ovs_port, server_port)
    return ovs_port


def get_port_qos(ports, qos):
    port_qos = {}
    end = re.search(qos, ports).start()
    start = end - 37
    ovs_port = re.findall("(qvo.*?[^\'])\"", ports[start:end])
    port_qos[ovs_port] = qos
    logging.info('Getting OVS QoS for Port: %s', port_qos)
    return port_qos