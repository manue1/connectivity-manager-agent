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

from novaclient import client
from clients import util

__author__ = 'beb'


class Client(object):
    def __init__(self):
        self.args = util.read_properties()
        self.novaclient = client.Client('2', self.args['os_username'], self.args['os_password'], self.args['os_tenant'], self.args['os_auth_url'])

    def get_hypervisors(self):
        hypervisors = self.novaclient.hypervisors.list()
        return hypervisors

    def get_servers(self):
        servers = self.novaclient.servers.list()
        return servers
