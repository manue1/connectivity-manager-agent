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

from ceilometerclient import client
from KeystoneManager import KeystoneManager

AUTH_URL= 'http://80.96.122.48:5000/v2.0'

class CeilometerManager(object):

    def __init__(self, endpoint, **kwargs):

        kc_args={}
        if kwargs.get('tenant_id'):
            kc_args['tenant_id'] = kwargs.get('tenant_id')
        else:
            kc_args['tenant_name'] = kwargs.get('tenant_name')
        if kwargs.get('auth_token'):
            token = kwargs.get('auth_token')
        #else:
            username = kwargs.get('username')
            password = kwargs.get('password')
        endpoint = 'http://80.96.122.48:8774'
        auth_plugin = client.get_auth_plugin(auth_url=AUTH_URL, endpoint = endpoint, **kwargs )

        #self.ceiloClient = client.Client(version=2, auth_url=endpoint, username=username, password=password, token = token, auth_plugin='keystone')
        self.ceiloClient = client.Client(version=2, auth_url=endpoint, username=username, password=password, token = token, auth_plugin=auth_plugin)

    def get_resource(self, resource_id):
        return self.ceiloClient.resources.get(resource_id)

if __name__ == '__main__':
    keystoneManager = KeystoneManager(version=2, username="nubomedia", password="nub0m3d1@", interface='public')

    endpoint = keystoneManager.get_endpoint(service_type='compute')
    #endpoint = "http://80.96.122.48:8774/v2/fba35e226f4441c6b3b8bbd276f5d41a"
    print "endpoint: %s" % endpoint

    kwargs = {}
    kwargs['username'] = keystoneManager.get_username()
    print "username: %s" % kwargs.get('username')

    kwargs['password'] = keystoneManager.get_password()
    print "password: %s" % kwargs.get('password')

    kwargs['auth_token'] = keystoneManager.get_token()
    print "token: %s" % kwargs.get('auth_token')
    kwargs['token'] = keystoneManager.get_token()

    project_id = keystoneManager.get_project_id()
    kwargs['project_id'] = project_id
    print project_id

    ceiloManager = CeilometerManager(endpoint=endpoint, **kwargs)
    print ceiloManager.get_resource('f2f3e0dc-4585-47d7-90c6-056ab2ea0a91')


