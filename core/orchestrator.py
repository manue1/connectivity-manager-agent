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

from sdk.mcn import util

HERE = os.environ.get('OPENSHIFT_REPO_DIR', '.')


class SoExecution(object):
    """
    classdocs
    """


    def __init__(self, token, tenant_name):
        """
        Constructor
        """
        # read template...
        f = open(os.path.join(HERE, 'data', 'imsaas-standalone.yaml'))
        self.template = f.read()
        self.token = token
        self.tenant_name = tenant_name
        f.close()
        self.stack_id = None
        # make sure we can talk to deployer...
        self.deployer = util.get_deployer(self.token, url_type='public', tenant_name=self.tenant_name)


    def design(self):
        """
        Deisgn method
        """
        pass


    def deploy(self):
        """
        Deploy method
        """
        print self.token
        if self.stack_id is None:
            self.stack_id = self.deployer.deploy(self.template, self.token)



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
            self.deployer.dispose(self.stack_id, self.token)
            self.stack_id = None


    def state(self):
        """
        Report on state.
        """
        if self.stack_id is not None:
            tmp = self.deployer.details(self.stack_id, self.token)
            if tmp['state'] != 'CREATE_COMPLETE':
                return 'Stack is currently being deployed...'
            else:
                return 'All good - Stack id is: ' + str(self.stack_id) + \
                       ' - Output is: ' + str(tmp['output'][0]['output_value'])
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


    def deploy(self):
        """
        Deploy method
        """
        self.executor.deploy()


    def provision(self):
        """
        Provision method
        """
        pass

    def dispose(self):
        """
        Dispose method
        """
        self.executor.dispose()



    def state(self):
        """
        Report on state.
        """
        return self.executor.state()


class ServiceOrchestrator(object):

    def __init__(self, token, tenant_name):
        self.so_d = SoDecision(SoExecution(token, tenant_name))





