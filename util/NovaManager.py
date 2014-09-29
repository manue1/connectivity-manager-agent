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
import utils

AUTH_URL= 'http://80.96.122.48:5000/v2.0'

class NovaManager(object):

    def __init__(self, username, password, project_id, auth_url):

        username, password = utils.get_username_and_password()
        self.novaClient = Client("2",username,password,"nubomedia","http://80.96.122.48:5000/v2.0")
        #self.novaClient = Client(2,username,password,project_id,auth_url)
        #self.novaClient.authenticate()

    def show_resource(self, stack_id=None, resource=None):
        return self.novaClient.servers.list()
        #return self.novaClient.flavors.list()



if __name__ == '__main__':
    username, password = utils.get_username_and_password()
    keystoneManager = KeystoneManager(username=username, password=password)

    username = keystoneManager.get_username()
    password = keystoneManager.get_password()
    project_id = keystoneManager.get_project_id()
    #auth_url = keystoneManager.get_auth_url()
    endpoint = keystoneManager.get_auth_url()
    print username
    print password
    print project_id
    print endpoint

    novaClient = NovaManager(username, password, project_id, endpoint)

    print novaClient.show_resource()