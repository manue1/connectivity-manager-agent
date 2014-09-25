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
__author__ = 'giuseppe'

import os
import util.TemplateManager as TemplateManager
from util.HeatManager import HeatManager
import json
from core.manager import TopologyManger

HERE = '/net/u/mpa'


class SoExecution(object):
    """
    classdocs
    """
    def __init__(self, endpoint, **kwargs):
        """
        Constructor
        """
        self.endpoint = endpoint
        self.stack_id = None
        self.name = None
        self.resources = {}
        self.config = {}
        # make sure we can talk to deployer...
        #self.heatManager = HeatManager(heat_url, **kc_args)
        self.heatManager = HeatManager(endpoint=endpoint, **kwargs)


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
            self.config = json.loads(kwargs.get('config_file'))
            self.name, template = TemplateManager.substitute_template(config_file=kwargs.get('config_file'))
            parameters = None
        elif kwargs.get('parameters'):
            template = self.template
        else:
            template = self.template

        if self.stack_id is None:
            self.stack_id = self.heatManager.deploy(name=self.name, template=template, parameters=parameters)
        return self.stack_id



    def provision(self):
        """
        Provision method
        """
        pass

    def dispose(self):
        """
        Dispose method
        """
        if self.stack_id is not None:
            self.heatManager.delete(self.stack_id)
            #self.stack_id = None
        return self.stack_id


    def state(self):
        """
        Report on state.
        """
        if self.stack_id is not None:
            tmp = self.heatManager.show(self.stack_id)
            if tmp['stack_status'] != 'CREATE_COMPLETE':
                return 'Stack is currently being deployed...'
            else:
                return 'All good - Stack id is: ' + str(self.stack_id) + \
                       ' - Output is: ' + str(tmp['output'][0]['output_value'])
        else:
            return 'Stack is not deployed atm.'

    def show(self, properties=[]):
        """
        Show stack information
        """
        if self.stack_id is not None:
            response = {}
            stack = self.heatManager.show(self.stack_id, properties = properties)
            resources = self.heatManager.get_resources(self.stack_id, resource_names=['connector','broker','media_server_group'])
            if self.config:
                topology = TopologyManger(stack=stack, config=self.config, resources=resources)
                resources = topology.dump()
            #resources = self.heatManager.get_resources(self.stack_id, resource_names=['broker','connector'])
            response.update(stack)
            response.update(resources)
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

    def show(self, properties=[]):
        """
        Show stack information
        """
        return self.executor.show(properties=properties)

class ServiceOrchestrator(object):

    def __init__(self, endpoint, **kwargs):
        self.so_d = SoDecision(SoExecution(endpoint=endpoint, **kwargs))





