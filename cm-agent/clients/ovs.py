# Copyright 2015 Technische Universitaet Berlin
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import subprocess

__author__ = 'beb'


class Client(object):
    def exe_vsctl(self, args):
        # vsctl_args = ["ovs-vsctl"] + args
        pass

    def set_manager(self):
        # Implement subprocess to run this cmd on remote machine for other hosts, or define as prerequisite that has to
        #  be configured manually?
        subprocess.check_call(["sudo", "ovs-vsctl", "set-manager", "ptcp:6640"])
        pass

    def get_port(self):
        pass

    def set_port(self, host_ip, port_id, action, action_id):
        subprocess.check_call(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % host_ip, "set", "port", "%s" % port_id,
                               "%s=%s" % (action, action_id)])

    def list_ports(self, host_ip):
        ports = subprocess.check_output(["sudo", "ovs-vsctl", "--format=json", "--db=tcp:%s:6640" % host_ip,
                                         "--columns=name,qos,tag", "list", "port"])
        return ports

    def list_interfaces(self, host_ip):
        interfaces = subprocess.check_output(["sudo", "ovs-vsctl", "--format=json", "--db=tcp:%s:6640" % host_ip,
                                              "--columns=name,external-ids,other-config", "list", "interface"])
        return interfaces

    def create_queue(self, host_ip, min_rate, max_rate):
        queue_id = subprocess.check_output(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % host_ip, "create", "queue",
                                            "other-config:min-rate=%d" % min_rate,
                                            "other-config:max-rate=%d" % max_rate])
        return queue_id.strip('\n')

    def del_queue(self, host_ip, queue_id):
        subprocess.check_call(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % host_ip, "destroy", "queue", "%s" % queue_id])

    def list_queue(self, host_ip):
        queues = subprocess.check_output(["sudo", "ovs-vsctl", "--format=json", "--db=tcp:%s:6640" % host_ip,
                                          "list", "queue"])
        return queues

    def create_qos(self, host_ip, queue_id):
        qos_id = subprocess.check_output(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % host_ip, "create", "qos",
                                          "type=linux-htb", "queues=0=%s" % queue_id ])
        return qos_id.strip('\n')

    def del_qos(self, host_ip, qos_id):
        subprocess.check_call(["sudo", "ovs-vsctl", "--db=tcp:%s:6640" % host_ip, "destroy", "qos", "%s" % qos_id])

    def list_qos(self, host_ip):
        qoss = subprocess.check_output(["sudo", "ovs-vsctl", "--format=json", "--db=tcp:%s:6640" % host_ip,
                                        "--columns=_uuid,queues,type", "list", "qos"])
        return qoss
