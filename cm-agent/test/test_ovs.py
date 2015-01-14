#!/usr/bin/python

import logging
from clients.ovs import Client

__author__ = 'beb'

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s_%(process)d:%(lineno)d [%(levelname)s] %(message)s',level=logging.DEBUG)


    client = Client()

    host_ip = '192.168.120.15'

    # ------------------
    # Retrieve lists:
    # ------------------
    ports = client.list_ports(host_ip)
    logging.info('Get ports for %s: %s', host_ip, ports)

    interfaces = client.list_interfaces(host_ip)
    logging.info('Get interfaces for %s: %s', host_ip, interfaces)

    # ------------------
    # Test setting QoS:
    # ------------------
    host_ip = '192.168.120.15'
    ovs_port = 'qvo641e9d9d-a5'
    min_rate = 100000
    max_rate = 1000000

    queue = client.create_queue(host_ip, min_rate, max_rate)
    logging.info('Create queue on ovs port %s, with min-rate: %d, max-rate: %d = %s', ovs_port, min_rate, max_rate, queue)

    qos = client.create_qos(host_ip, queue)
    logging.info('Create QoS for queue: %s = %s', queue, qos)

    setport = client.set_port(host_ip, ovs_port, 'qos', qos)
    logging.info('Set QoS: %s on port: %s ! Result = %s', qos, ovs_port, setport)
