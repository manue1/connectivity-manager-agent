#!/usr/bin/python
# Copyright 2014 Technische Universitaet Berlin
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
__author__ = 'mpa'
from novaclient.v1_1.client import Client as novaclient


class Client(object):
    def __init__(self, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')
        tenant_name = kwargs.get('tenant_name')
        auth_url = kwargs.get('auth_url')
        self.novaclient = novaclient(username, password, tenant_name, auth_url)

    def show_resource(self, resource_id):
        print 'resource id: %s' % resource_id
        resource = self.novaclient.servers.get(resource_id)._info
        print "nova: %s" % resource
        return resource

