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
from util import utils as utils

__author__ = 'mpa'

CONFIG_PATH = "/etc/nubomedia/"
#CONFIG_PATH = "/net/u/mpa/project/nubomedia/emm/data/"
STATIC_ENV_PATH= CONFIG_PATH + 'environment.yaml'

class Stack(object):
    def __init__(self, clients, config):
        self.config = config
        self.clients = clients
        self.heatclient = clients.get('heatclient')

        self.stack_id = None

        ###Initialize Instances###
        connector = Instance(clients=self.clients, config=config.connector)
        broker = Instance(clients=self.clients, config=config.broker)
        self.instances = [connector, broker]

        ###Initialize Media Server Group###
        media_server_group = ScalingGroup(clients=self.clients, config=config.media_server_group)
        self.scaling_groups = [media_server_group]


    def deploy(self):
        #get template
        template = self.config.get_template()
        #get environment
        heatclient = self.clients.get('heatclient')
        env, env_file = heatclient.get_environment_and_file(STATIC_ENV_PATH)
        #deploy a new stack and get the response with additional information
        stack_information = self.heatclient.deploy(name=self.config.name, template=template, environment=env, environment_file = env_file)
        #get stack id for the new stack
        self.stack_id = stack_information['stack']['id']
        return stack_information

    def delete(self):
        if self.stack_id is not None:
            self.heatclient.delete(stack_id=self.stack_id)

    def update_resources(self):
        deployed_resources = self.heatclient.list_resources(stack_id=self.stack_id)
        for instance in self.instances:
            for resource in deployed_resources:
                if resource['resource_name'] == instance.name:
                    instance.resource_id = resource['physical_resource_id']
        for scaling_group in self.scaling_groups:
            for resource in deployed_resources:
                if resource['resource_name'] == scaling_group.name:
                    scaling_group.resource_id = resource['physical_resource_id']


    def show_runtime_information(self):
        self.update_resources()
        stack_information = {}
        stack_information.update(utils.filter_dict(data_dict=self.heatclient.show(stack_id=self.stack_id),
                                                   properties=['stack_name', 'outputs', 'creation_time', 'stack_status',
                                                               'id']))
        stack_information['resources'] = {}
        for instance in self.instances:
            if instance.resource_id:
                stack_information['resources'][instance.name] = {}
                stack_information['resources'][instance.name].update(instance.show_runtime_information())
                stack_information['resources'][instance.name].update(instance.show_static_information())
            else:
                stack_information['resources'][instance.name] = instance.show_static_information()
                stack_information['resources'][instance.name]['name'] = instance.name
                stack_information['resources'][instance.name]['status'] = 'Null'
        for scaling_group in self.scaling_groups:
            if scaling_group.resource_id:
                stack_information['resources'][scaling_group.name] = {}
                stack_information['resources'][scaling_group.name].update(scaling_group.show_static_information())
                stack_information['resources'][scaling_group.name].update(scaling_group.show_runtime_information())
            else:
                stack_information['resources'][scaling_group.name] = scaling_group.show_static_information()
                stack_information['resources'][scaling_group.name]['status'] = 'Null'
                stack_information['resources'][scaling_group.name]['resources'] = 'Null'
        #print "stack information: %s" % stack_information
        return stack_information


class Instance(object):
    def __init__(self, clients, config, resource_id=None):
        self.config = config
        self.name = config.name
        self.resource_id = resource_id
        self.novaclient = clients.get('novaclient')
        self.ceilometerclient = clients.get('ceilometerclient')

    def show_static_information(self):
        static_information = {}
        static_information['key_name'] = self.config.key_name
        static_information['flavor'] = self.config.flavor
        static_information['image'] = self.config.image
        return static_information

    #returns runtime information for this instance
    def show_runtime_information(self):
        runtime_information = {}
        #print "name: %s, id: %s, config: %s" % (self.name, self.resource_id, self.config)
        if self.resource_id is not None:
            runtime_information = utils.filter_dict(data_dict=self.novaclient.show_resource(self.resource_id),
                                                    properties=['addresses', 'id', 'status', 'key_name', 'created'])
            runtime_information['cpu_util'] = self.ceilometerclient.get_last_sample_value(resource_id=self.resource_id,
                                                                                          meter_name='cpu_util')
        #print "instance information: %s" % runtime_information
        return runtime_information


class ScalingGroup(object):
    def __init__(self, clients, config, resource_id=None):
        self.config = config
        self.name = config.name
        self.resource_id = resource_id
        self.clients = clients
        self.heatclient = clients.get('heatclient')

        ###Instances of AutoScalingGroup###
        self.instances = []

    #updates deployed resources (add new ones, delete old ones)
    def update_resources(self):
        if self.resource_id is not None:
            #get existing resource ids
            existing_resource_ids = self.list_existing_resource_ids()
            #get deployed resource ids from openstack
            deployed_resource_ids = self.heatclient.list_resource_ids(stack_id=self.resource_id)
            #find new resources
            for deployed_resource_id in deployed_resource_ids:
                if deployed_resource_id not in existing_resource_ids:
                    new_instance = Instance(clients=self.clients, config=self.config.media_server_group,
                                            resource_id=deployed_resource_id)
                    self.instances.append(new_instance)
            #check that instances still exists
            for existing_resource_id in existing_resource_ids:
                if existing_resource_id not in deployed_resource_ids:
                    instance = self.get_resource(resource_id=existing_resource_id)
                    if instance:
                        self.instances.remove(instance)

    #return resource by resource id
    def get_resource(self, resource_id):
        for instance in self.instances:
            if instance.resource_id == resource_id:
                return instance
        return False

    #returns ids of existing instances
    def list_existing_resource_ids(self):
        resource_ids = []
        for resource in self.instances:
            resource_ids.append(resource.resource_id)
        return resource_ids

    def show_static_information(self):
        static_information = {}
        static_information['name'] = self.config.name
        static_information['min_size'] = self.config.min_size
        static_information['max_size'] = self.config.max_size
        static_information['image'] = self.config.image
        static_information['flavor'] = self.config.flavor
        static_information['key_name'] = self.config.key_name
        static_information['policies'] = self.config.policies
        return static_information

    def show_runtime_information(self):
        self.update_resources()
        #get nested stack information
        stack_information = self.heatclient.show(stack_id=self.resource_id)
        properties = ['stack_name', 'creation_time', 'stack_status', 'id']
        scaling_group_information = {}
        scaling_group_information.update(utils.filter_dict(data_dict=stack_information, properties=properties))
        scaling_group_information['resources'] = []
        for instance in self.instances:
            if instance.resource_id is not None:
                scaling_group_information['resources'].append(instance.show_runtime_information())
        return scaling_group_information