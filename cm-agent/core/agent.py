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
        qoss = {}
        queues = {}
        queue_rates = {}
        hypervisors_servers = {}
        hypervisors = self.cloud.read_hypervisor_info()
        logging.info('Getting list of hypervisors: %s', hypervisors)
        servers = self.cloud.read_server_info()
        logging.info('Getting list of servers: %s', servers)

        server_ips = self.cloud.get_server_ips()
        logging.info('Getting list of all server IPs: %s', server_ips)

        for kh, vh in hypervisors.items():
            cloud_info[kh] = vh
            cloud_info[kh]['servers'] = {}

            hypervisors_servers[kh] = self.cloud.get_server_hypervisor_info(servers, kh)
            logging.info('Getting list of servers matched with hypervisor: %s', hypervisors_servers)

            interfaces[kh] = Host(kh).list_interfaces_hypervisor(hypervisors)
            logging.info('Interfaces for %s: %s', kh, interfaces)

            queues[kh] = Host(kh).list_queues_hypervisor(vh.get('ip'))
            logging.info('Queues for %s: %s', kh, queues)

            queue_rates[kh] = self.cloud.get_queue_rates(vh.get('ip'))
            logging.info('Queue rates for %s: %s', kh, queue_rates)

            qoss[kh] = Host(kh).list_qos_hypervisor(vh.get('ip'))
            logging.info('QoS\'s for %s: %s', kh, qoss)

            for hs in hypervisors_servers[kh]:
                cloud_info[kh]['servers'][hs] = {}
                for ks, vs in servers.items():
                    if ks == hs:
                        cloud_info[kh]['servers'][hs]['name'] = vs.get('name')
                        for ki, vi in server_ips.items():
                            if ki == hs:
                                try:
                                    cloud_info[kh]['servers'][hs]['ip'] = vi[0]
                                    neutron_port_id = self.cloud.get_neutron_port(vi[0])
                                    ovs_port_id = self.cloud.get_port_id(interfaces[kh], neutron_port_id)[0]
                                    cloud_info[kh]['servers'][hs]['neutron_port'] = neutron_port_id
                                    cloud_info[kh]['servers'][hs]['ovs_port_id'] = ovs_port_id
                                    qos_id = Host(kh).get_port_qos(vh.get('ip'), ovs_port_id)
                                    cloud_info[kh]['servers'][hs]['qos'] = self.cloud.get_qos_queue(qos_id, queues[kh],
                                                                                     qoss[kh])
                                except Exception, e:
                                    logging.info('Exception %s', e)
                                    cloud_info[kh]['servers'][hs]['ip'] = None
                                    cloud_info[kh]['servers'][hs]['neutron_port'] = None
                                    cloud_info[kh]['servers'][hs]['ovs_port_id'] = None
                                    cloud_info[kh]['servers'][hs]['qos'] = None
                                    continue


        logging.info('Cloud info: %s', cloud_info)
        return cloud_info

    def set_qos(self, qos_args):
        qos_status = {}
        hypervisors = self.cloud.read_hypervisor_info()

        _qos_args = json.loads(qos_args)
        for hypervisor_hostname, v in _qos_args.items():
            interfaces = Host(hypervisor_hostname).list_interfaces_hypervisor(hypervisors)
            for ks, vs in v.items():
                if type(vs) != unicode:
                    logging.info('QoS rates for server %s: %s', ks, vs.get('qos'))
                    qos_status[ks] = Host(hypervisor_hostname).set_qos_vm(self.cloud.get_hypervisor_ip(hypervisor_hostname),
                                                            interfaces, ks, vs.get('qos'))
        return qos_status


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
            host_info[hypervisor.hypervisor_hostname]['instances'] = hypervisor.running_vms
            host_info[hypervisor.hypervisor_hostname]['cpu_used'] = hypervisor.vcpus_used
            host_info[hypervisor.hypervisor_hostname]['cpu_total'] = hypervisor.vcpus
            host_info[hypervisor.hypervisor_hostname]['ram_used'] = hypervisor.memory_mb_used
            host_info[hypervisor.hypervisor_hostname]['ram_total'] = hypervisor.memory_mb
        logging.info('Reading info of all hypervisors %s', host_info)
        return host_info

    def get_hypervisor_ip(self, hyp_hostname):
        hypervisors = self.novaclient.get_hypervisors()
        for hypervisor in hypervisors:
            if hypervisor.hypervisor_hostname == hyp_hostname:
                return hypervisor.host_ip

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
            ips[server.id] = self.get_server_ip(server)
        logging.info('All server IPs %s', ips)
        return ips

    def get_neutron_port(self, ip):
        port = self.neutronclient.get_ports(ip)
        logging.info('Getting Neutron port ID %s for IP %s', port, ip)
        return port

    def get_qos_queue(self, qos_id, queues, hypervisor_qos):
        qos = {'queues': {}}

        for qoi in hypervisor_qos:
            match = 0
            if type(qoi) == unicode:
                qos['type'] = qoi
            else:
                for li in qoi:
                    if li[1] == qos_id:
                        match = 1
                        if li[0] == 'uuid':
                            qos['uuid'] = li[1]
                    elif match:
                        match = 0
                        for item_inner in li:
                            if type(item_inner) == list and item_inner[0][0] == 0:
                                qos['queues'][0] = {}
                                for queue_inner in item_inner[0][1]:
                                    if queue_inner != 'uuid':
                                        qos['queues'][0]['uuid'] = queue_inner
                                        for qui in queues:
                                            if qui[0][0] == 'uuid':
                                                if qui[0][1] == queue_inner:
                                                    qos['queues'][0]['rates'] = self.get_queue_rates(qui)

        logging.info('Getting OVS queue for QoS ID %s: %s', qos_id, qos)
        return qos

    @staticmethod
    def get_server_hypervisor_info(servers, hostname):
        server_match = []
        for server in servers.values():
            if server['OS-EXT-SRV-ATTR:hypervisor_hostname'] == hostname:
                server_match.append(server['id'])
        logging.info('Getting servers for matching hypervisor %s: %s', hostname, server_match)
        return server_match

    @staticmethod
    def get_queue_rates(queue):
        queue_rates = {}

        for item in queue:
            for li in item:
                if item[0] == 'uuid':
                    queue_rates['uuid'] = item[1]
                if li == 'map':
                    for item_inner in item:
                        if type(item_inner) == list and len(item_inner) > 0:
                            for rate_inner in item_inner:
                                if rate_inner[0] == 'max-rate':
                                    queue_rates['rates'] = {}
                                    queue_rates['rates']['max-rate'] = rate_inner[1]
                                if rate_inner[0] == 'min-rate':
                                    queue_rates['rates']['min-rate'] = rate_inner[1]
        logging.info('Queue port rates: %s', queue_rates)
        return queue_rates

    @staticmethod
    def get_server_ip(server):
        ips = []
        if hasattr(server, 'addresses'):
            for interface in server.addresses.values():
                ips.append(interface[0]['addr'])
        return ips

    @staticmethod
    def get_port_id(interfaces, server_port):
        end = re.search(server_port, interfaces).start()
        start = end - 75
        ovs_port = re.findall("(qvo.*?[^\'])\"", interfaces[start:end])
        logging.info('Getting OVS port: %s, for Neutron Port ID: %s', ovs_port, server_port)
        return ovs_port


class Host(object):
    def __init__(self, hypervisor):
        self.hypervisor = hypervisor
        self.ovsclient = OVSClient()
        self.cloud = Cloud()

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

    def list_ports_hypervisor(self, hypervisor_ip):
        ports = self.ovsclient.list_ports(hypervisor_ip)
        logging.info('Getting OVS ports: %s for Hypervisor IP: %s', ports, hypervisor_ip)
        return ports

    def list_qos_hypervisor(self, hypervisor_ip):
        qos_raw = json.loads(self.ovsclient.list_qos(hypervisor_ip))
        hypervisor_qos = []

        for q in qos_raw.get('data'):
            hypervisor_qos.append(q)

        logging.info('Getting final OVS QoS %s for IP %s', hypervisor_qos, hypervisor_ip)
        return hypervisor_qos

    def list_queues_hypervisor(self, hypervisor_ip):
        queues = []
        queues_raw = json.loads(self.ovsclient.list_queue(hypervisor_ip))
        logging.info('Queues for comparison for %s : %s ... ', hypervisor_ip, queues_raw)

        for q in queues_raw.get('data'):
            queues.append(q)
        logging.info('Queues from queue list: %s', queues)
        return queues

    def get_port_qos(self, hypervisor_ip, ovs_port):
        ports_raw = json.loads(self.list_ports_hypervisor(hypervisor_ip))
        logging.info('Ports for %s: %s', hypervisor_ip, ports_raw)
        qos_id = '0'
        for port in ports_raw.get('data'):
            isvm = 0
            for port_key in port:
                if type(port_key) == unicode and port_key == ovs_port:
                    isvm = 1
                if type(port_key) == list and isvm:
                    isvm = 0
                    for pv in port_key:
                        if pv != 'uuid':
                            qos_id = pv
                            logging.info('QoS ID for port: %s is: %s', ovs_port, qos_id)
        return qos_id

    def set_qos_vm(self, hypervisor_ip, interfaces, vm_id, qos_rates):
        qos_status = 0
        server_ips = self.cloud.get_server_ips()

        for ks, vs in server_ips.items():
            if ks == vm_id:
                neutron_port = self.cloud.get_neutron_port(vs[0])
                ovs_port_id = self.cloud.get_port_id(interfaces, neutron_port)[0]
                logging.info('OVS port ID for Server %s: %s', ks, ovs_port_id)
                logging.info('Server %s gets Min-rate %s Max-rate %s', ks, qos_rates.get('min-rate'), qos_rates.get('max-rate'))
                queue_id = self.ovsclient.create_queue(hypervisor_ip, int(qos_rates.get('min-rate')), int(qos_rates.get('max-rate')))
                logging.info('Queue ID for Server %s: %s', ks, queue_id)
                qos_id = self.ovsclient.create_qos(hypervisor_ip, queue_id)
                qos_status = self.ovsclient.set_port(hypervisor_ip, ovs_port_id, 'qos', qos_id)
                logging.info('QoS status for Server %s: %s', ks, qos_status)
        return qos_status
