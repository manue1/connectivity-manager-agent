#!/usr/bin/python
# Copyright 2014 Technische Universitaet Berlin
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
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

import heatclient

class StackManager(object):

    def __init__(self, heat_url, tenant_name, auth_token):
        self.heat_url = heat_url
        self.tenant_name = tenant_name
        self.auth_token = auth_token
        #create heat client with the credentials connected to the endpoint
        self.heatClient = heatclient.Client('1', endpoint="%s/%s" % (heat_url, tenant_name), token=auth_token)

    def get_deployer(self):
        return self.heatClient

    def deploy(self, template):
        pass
