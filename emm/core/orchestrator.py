# Copyright 2014 Technische Universitaet Berlin
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


__author__ = 'giuseppe'

from core.config import Config as Config
import model.entities as entities
import util.nova as nova
import util.ceilometer as ceilometer
import util.keystone as keystone
import util.heat as heat
import util.utils as utils

AUTH_URL_KEYSTONE = 'http://80.96.122.48:5000/v3'
AUTH_URL = 'http://80.96.122.48:5000/v2.0'
#CONFIG_PATH = "/net/u/mpa/"
CONFIG_PATH = '/etc/nubomedia/'
USER_PATH = CONFIG_PATH + 'user.cfg'

class SoExecution(object):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        self.clients = {}

        tenant_name, username, password = utils.get_credentials(USER_PATH)
        kwargs = {}
        kwargs['tenant_name'] = tenant_name
        kwargs['username'] = username
        kwargs['password'] = password

        keystoneclient = keystone.Client(auth_url=AUTH_URL_KEYSTONE, **kwargs)
        self.clients.update({'keystoneclient': keystoneclient})

        kwargs['token'] = keystoneclient.token

        heat_endpoint = keystoneclient.get_endpoint(service_type='orchestration')
        heatclient = heat.Client(endpoint=heat_endpoint, auth_url=AUTH_URL, **kwargs)
        self.clients.update({'heatclient': heatclient})

        novaclient = nova.Client(auth_url=AUTH_URL, **kwargs)
        self.clients.update({'novaclient': novaclient})

        ceilometerclient = ceilometer.Client(auth_url=AUTH_URL, **kwargs)
        self.clients.update({'ceilometerclient': ceilometerclient})

        self.stack = None
        self.config = None

    def design(self):
        """
        Design method
        """
        pass


    def deploy(self, **kwargs):
        """
        Deploy method
        """
        if kwargs.get('config_file'):
            user_config = kwargs.get('config_file')
            config = Config(user_config_file=user_config)
            self.stack = entities.Stack(clients=self.clients, config=config)
        else:
            return {'ERROR': 'No config file was provided'}

        if self.stack.stack_id is None:
            stack_details = self.stack.deploy()
            return stack_details
        else:
            return {'ERROR': 'Stack is already deployed'}


    def provision(self):
        """
        Provision method
        """
        pass

    def dispose(self):
        """
        Dispose method
        """
        if self.stack.stack_id is not None:
            self.stack.delete()
            #self.stack_id = None
            return None
        else:
            return {'ERROR': 'Stack is not deployed'}


    def state(self):
        """
        Report on state.
        """
        if self.stack.stack_id is not None:
            tmp = self.stack.show(self.stack.stack_id)
            if tmp['stack_status'] != 'CREATE_COMPLETE':
                return 'Stack is currently being deployed...'
            else:
                return 'All good - Stack id is: ' + str(self.stack_id) + \
                       ' - Output is: ' + str(tmp['output'][0]['output_value'])
        else:
            return 'Stack is not deployed atm.'

    def show(self):
        """
        Show stack information
        """
        if self.stack.stack_id is not None:
            response = {}
            stack = self.stack.show_runtime_information()
            response.update(stack)
            return response
        else:
            return 'Stack is not deployed atm.'


class SoDecision(object):
    '''
    classdocs
    '''


    def __init__(self, executor):
        '''
        Constructor
        '''
        self.executor = executor


    def design(self):
        """
        Deisgn method
        """
        pass


    def deploy(self, **kwargs):
        """
        Deploy method
        """
        return self.executor.deploy(**kwargs)


    def provision(self):
        """
        Provision method
        """
        pass

    def dispose(self):
        """
        Dispose method
        """
        return self.executor.dispose()


    def state(self):
        """
        Report on state.
        """
        return self.executor.state()

    def show(self):
        """
        Show stack information
        """
        return self.executor.show()


class ServiceOrchestrator(object):
    def __init__(self):
        self.so_d = SoDecision(SoExecution())


