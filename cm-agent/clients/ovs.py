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

    def get_portid(self):
        pass

    def add_port(self):
        pass

    def mod_port(self):
        pass

    def del_port(self):
        pass

    def list_ports(self):
        out = subprocess.check_output(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % self.host_ip, "list", "port"])
        return out

    def add_queue(self):
        pass

    def del_queue(self):
        pass

    def add_qos(self):
        pass

    def del_qos(self):
        pass

    def list_qos(self):
        pass