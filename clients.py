__author__ = 'mpa'


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

from keystoneclient.client import Client as keystoneClient
from novaclient.client import Client

AUTH_URL= 'http://80.96.122.48:5000/v3'

class KeystoneManager(object):

    def __init__(self, **kwargs):
        """Get an endpoint and auth token from Keystone.
        :param username: name of user
        :param password: user's password
        :param tenant_id: unique identifier of tenant
        :param tenant_name: name of tenant
        :param auth_url: endpoint to authenticate against
        :param token: token to use instead of username/password
        """

        kc_args = {'auth_url': kwargs.get('auth_url') or AUTH_URL,
                'insecure': kwargs.get('insecure'),
                'cacert': kwargs.get('cacert')}
        if kwargs.get('tenant_id'):
            kc_args['tenant_id'] = kwargs.get('tenant_id')
        else:
            kc_args['tenant_name'] = kwargs.get('tenant_name')
        if kwargs.get('token'):
            kc_args['token'] = kwargs.get('token')
        else:
            kc_args['username'] = kwargs.get('username')
            kc_args['password'] = kwargs.get('password')

        self.ksclient = keystoneClient(version=2, **kc_args)
        self.token = self.ksclient.auth_token
        self.tenant_id = self.ksclient.project_id
        self.tenant_name = self.ksclient.tenant_name
        self.username = self.ksclient.username
        self.password = self.ksclient.password
        self.project_id = self.ksclient.project_id

    def get_endpoint(self, **kwargs):
        """Get an endpoint using the provided keystone client."""
        #ksclient.endpoints.get('orchestration')
        if kwargs.get('region_name'):
            return ''.join(self.ksclient.service_catalog.get_urls(
                service_type=kwargs.get('service_type') or 'orchestration',
                attr='region',
                filter_value=kwargs.get('region_name'),
                endpoint_type=kwargs.get('endpoint_type') or 'publicURL'))
        return ''.join(self.ksclient.service_catalog.get_urls(
            service_type=kwargs.get('service_type') or 'orchestration',
            endpoint_type=kwargs.get('endpoint_type') or 'publicURL'))

    def get_token(self):
        if self.token is None:
            self.token = self.ksclient.auth_token
        return self.token

    def get_tenant_id(self):
        if self.tenant_id is None:
            self.tenant_id = self.ksclient.project_id
        return self.tenant_id

    def get_tenant_name(self):
        if self.tenant_name is None:
            self.tenant_name = self.ksclient.tenant_name
        return self.tenant_name

    def get_username(self):
        if self.username is None:
            self.username = self.ksclient.username
        return self.username

    def get_password(self):
        if self.password is None:
            self.password = self.ksclient.password
        return self.password

    def get_project_id(self):
        if self.project_id is None:
            self.project_id = self.ksclient.project_id
        return self.project_id


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

        self.novaClient = Client(version=2, username=username, password=password)
        #self.novaClient = Client(version=2, username=username, auth_url = AUTH_URL, auth_token = token)
        #self.novaClient = Client(version=2, username=username, password=password, auth_url = endpoint)
        #self.novaClient.authenticate()

    def show_resource(self, stack_id=None, resource=None):
        self.novaClient.servers.get('218b8010-eec9-4938-81f2-b37706c0136e')
        #return self.novaClient.servers.list()
        #return self.novaClient.flavors.list()



if __name__ == '__main__':
    keystoneManager = KeystoneManager(username="nubomedia", password="nub0m3d1@")

    endpoint = keystoneManager.get_endpoint(service_type='compute')
    #endpoint = "http://80.96.122.48:8774/v2"
    print "endpoint: %s" % endpoint

    kwargs = {}
    kwargs['username'] = keystoneManager.get_username()
    print "username: %s" % kwargs.get('username')

    kwargs['password'] = keystoneManager.get_password()
    print "password: %s" % kwargs.get('password')

    kwargs['token'] = keystoneManager.get_token()
    print "token: %s" % kwargs.get('token')

    project_id = keystoneManager.get_project_id()
    kwargs['project_id'] = project_id
    print project_id

    novaClient = NovaManager(endpoint=endpoint, **kwargs)

    print novaClient.show_resource()