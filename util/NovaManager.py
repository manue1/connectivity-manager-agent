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
from novaclient.client import Client
from KeystoneManager import KeystoneManager
from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient.client import Client

AUTH_URL= 'http://80.96.122.48:5000/v2.0'

class NovaManager(object):

    def __init__(self, endpoint, **kwargs):

        kc_args={}
        if kwargs.get('tenant_id'):
            kc_args['tenant_id'] = kwargs.get('tenant_id')
        else:
            kc_args['tenant_name'] = kwargs.get('tenant_name')
        if kwargs.get('token'):
            token = kwargs.get('token')
        #else:
            username = kwargs.get('username')
            password = kwargs.get('password')
            project_id = kwargs.get('project_id')

        auth = v2.Password(auth_url=AUTH_URL, username=username, password=password, tenant_name=project_id)
        sess = session.Session(auth=auth)

        self.novaClient =Client(version=3, session=sess)
        #self.novaClient = Client(version=3, username=username, password=password, auth_url = AUTH_URL)
        #self.novaClient = Client(version=3, auth_token = token, auth_url = AUTH_URL,)
        #self.novaClient.authenticate()

    def show_resource(self, stack_id=None, resource=None):
        return self.novaClient.servers.list()
        #return self.novaClient.flavors.list()



if __name__ == '__main__':
    keystoneManager = KeystoneManager(username="username", password="password", interface='public')

    endpoint = keystoneManager.get_endpoint(service_type='compute')
    print "endpoint: %s" % endpoint

    kwargs = {}
    kwargs['username'] = keystoneManager.get_username()
    print "username: %s" % kwargs.get('username')

    kwargs['password'] = keystoneManager.get_password()
    print "password: %s" % kwargs.get('password')

    kwargs['token'] = keystoneManager.get_token()
    print "token: %s" % kwargs.get('token')

    project_id = keystoneManager.get_tenant_name()
    kwargs['project_id'] = project_id
    print project_id

    novaClient = NovaManager(endpoint=endpoint, **kwargs)


    print novaClient.show_resource()