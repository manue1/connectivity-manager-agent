#!/usr/bin/python

from clients.ovs import Client

__author__ = 'beb'

if __name__ == '__main__':

    client = Client()

    ports = client.list_ports('192.168.120.15')
    print ports

    interfaces = client.list_interfaces('192.168.120.15')
    print interfaces

    # test setting QoS
    host_ip = '192.168.120.15'
    ovs_port = 'qvo641e9d9d-a5'
    min_rate = 100000
    max_rate = 1000000

    queue = client.create_queue(host_ip, min_rate, max_rate)
    print queue

    qos = client.create_qos(host_ip, queue)
    print qos

    setport = client.set_port(host_ip, ovs_port, 'qos', qos)
    print setport
