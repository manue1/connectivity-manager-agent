#!/usr/bin/python

import subprocess

__author__ = 'beb'

class Client(object):

    def __init__(self, host_ip):
        self.host_ip = host_ip
        self.set_manager()

    def exe_vsctl(self, args):
        # ToDo: ovs-vsctl wrapper
        # vsctl_args = ["ovs-vsctl"] + args
        pass

    def set_manager(self):
        # Implement subprocess to run this cmd on remote machine for other hosts, or define as prerequisite that has to be configured manually?
        subprocess.check_call(["sudo", "ovs-vsctl", "set-manager", "ptcp:6640"])
        pass

    def get_port(self):
        pass

    def set_port(self, port_id, action, action_id):
        subprocess.check_call(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % self.host_ip, "set", "port", "%s" % port_id, "%s=%s" % (action, action_id)])

    def list_ports(self):
        ports = subprocess.check_output(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % self.host_ip, "list", "port"])
        return ports

    def create_queue(self, min_rate, max_rate):
        queue_id = subprocess.check_output(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % self.host_ip, "create", "queue", "type=linux-htb", "other-config:min-rate=%d" % min_rate, "other-config:max-rate=%d" % max_rate])
        return queue_id

    def del_queue(self, queue_id):
        subprocess.check_call(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % self.host_ip, "destroy", "queue", "%s" % queue_id])

    def list_queue(self):
        queues = subprocess.check_output(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % self.host_ip, "list", "queue"])
        return queues

    def create_qos(self, queue_in, queue_out):
        qos_id = subprocess.check_output(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % self.host_ip, "create", "qos", "type=linux-htb", "queues=0=%s,1=%s" % (queue_in, queue_out) ])
        return qos_id

    def del_qos(self, qos_id):
        subprocess.check_call(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % self.host_ip, "destroy", "qos", "%s" % qos_id])

    def list_qos(self):
        qoss = subprocess.check_output(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % self.host_ip, "list", "qos"])
        return qoss