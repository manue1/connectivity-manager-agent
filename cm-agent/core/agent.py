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
        queue_rates = {}
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
            queue_rates[kh] = Host(kh).get_queue_rates(vh.get('ip'))
            logging.info('Queues for %s : %s ... ', kh, queue_rates)
            qoss[kh] = Host(kh).list_qos_hypervisor(vh.get('ip'), queue_rates[kh])
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
                                cloud_info[kh]['servers'][hs]['qos'] = qoss[kh]
                                #for kq, vq in qoss[kh].data.items():
                                #    logging.info('### kq: %s vq: %s ... ', kq, vq)

                                #cloud_info[kh]['servers'][vhs]['qos'] = get_port_qos(ports[kh])

        logging.info('Cloud info .. %s', cloud_info)
        return hypervisors

    def set_qos(self):

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
            ips[server.id] = get_server_ip(server)
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

    def list_qos_hypervisor(self, hypervisor_ip, queue_rates):
        qos = {'queues': {}}
        qos_raw = json.loads(self.ovsclient.list_qos(hypervisor_ip))
        status = 0

        for q in qos_raw.get('data'):
            for item in q:
                if type(item) == unicode:
                    qos['type'] = item
                else:
                    for li in item:
                        if item[0] == 'uuid':
                            qos['uuid'] = item[1]
                        if li == 'map':
                            for item_inner in item:
                                if type(item_inner) == list and item_inner[0][0] == 0:
                                    qos['queues'][0] = {}
                                    for queue_inner in item_inner[0][1]:
                                        if queue_inner != 'uuid':
                                            qos['queues'][0]['uuid'] = queue_inner
                                            for qk, qv in queue_rates.items():
                                                logging.info('####### qk: %s qv: %s', qk, qv)
                                                if qk == 'uuid' and qv == queue_inner:
                                                    status = 1
                                                if qk == 'rates' and status:
                                                    qos['queues'][0]['rates'] = qv
                                            logging.info('##### Queue rates with qos %s', qos)

        logging.info('Getting final OVS QoS %s for IP %s', qos, hypervisor_ip)
        return qos

    def get_queue_rates(self, hypervisor_ip):
        queue_rates = {}
        queues = json.loads(self.ovsclient.list_queue(hypervisor_ip))
        logging.info('Queues: %s of type: %s', queues)

        for q in queues.get('data'):
            for item in q:
                for li in item:
                    if item[0] == 'uuid':
                        queue_rates['uuid'] = item[1]
                    if li == 'map':
                        for item_inner in item:
                            if type(item_inner) == list and len(item_inner) > 0:
                                for rate_inner in item_inner:
                                    if rate_inner[0] == 'max-rate':
                                        logging.info('max')
                                        queue_rates['rates'] = {}
                                        queue_rates['rates']['max-rate'] = rate_inner[1]
                                    if rate_inner[0] == 'min-rate':
                                        queue_rates['rates']['min-rate'] = rate_inner[1]
        logging.info('Queue port rates: %s', queue_rates)
        return queue_rates


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


