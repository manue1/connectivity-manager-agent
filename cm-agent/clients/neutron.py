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

from neutronclient.neutron import client as NeutronClient

__author__ = 'beb'


class Client(object):
    def __init__(self, endpoint, token):
        self.neutron = NeutronClient.Client('2.0', endpoint_url=endpoint, token=token)

    def list_ports(self):
        ips = {}
        lst = self.neutron.list_ports()
        for pt in lst.get('ports'):
            for _ips in pt.get('fixed_ips'):
                ips[pt.get('id')] = _ips.get('ip_address')
        return ips

    def get_ports(self, ip):
        lst = self.list_ports()
        return next((k for k, v in lst.items() if v == ip), None)
