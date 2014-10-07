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

from heatclient.v1 import client as heat
from heatclient.common import utils
import heatclient.exc as exc


class Client(object):
    def __init__(self, endpoint, **kwargs):

        kc_args = {}
        if kwargs.get('tenant_id'):
            kc_args['tenant_id'] = kwargs.get('tenant_id')
        else:
            kc_args['tenant_name'] = kwargs.get('tenant_name')
        if kwargs.get('token'):
            kc_args['token'] = kwargs.get('token')
            #else:
            kc_args['username'] = kwargs.get('username')
            kc_args['password'] = kwargs.get('password')

        self.client = heat.Client(endpoint=endpoint, **kc_args)

    def deploy(self, **kwargs):
        kcargs = {
            'stack_name': kwargs.get('name'),
            'disable_rollback': not (bool(kwargs.get('enable_rollback'))),
            'parameters': utils.format_parameters(kwargs.get('parameters')),
            'template': kwargs.get('template')
        }

        timeout = kwargs.get('timeout') or kwargs.get('create_timeout')
        if timeout:
            kcargs['timeout_mins'] = timeout

        try:
            stack = self.client.stacks.create(**kcargs)
        except exc.HTTPNotFound:
            raise exc.CommandError('Stack already exists: %s' % kwargs.get('name'))
            #stack = "The stack %s already exists" % kwargs.get('name')
            #stack = {'stack': {'id':'Null','stack_status':'Stack already exists'}}
        return stack

    def delete(self, stack_id):
        fields = {'stack_id': stack_id}
        try:
            self.client.stacks.delete(**fields)
            return "Stack %s deletion in progress" % stack_id
        except exc.HTTPNotFound as e:
            print(e)


    def show(self, stack_id, properties=[]):
        fields = {'stack_id': stack_id}
        try:
            stack = self.client.stacks.get(**fields)
        except exc.HTTPNotFound:
            raise exc.CommandError('Stack not found: %s' % fields['stack_id'])
        else:
            tmp_stack = stack.to_dict()
            if properties:
                return_stack = {}
                print "tmp_sack %s" % tmp_stack
                for property in properties:
                    if tmp_stack.get(property):
                        return_stack[property] = tmp_stack.get(property)
            else:
                return_stack = tmp_stack
        #list = heatClient.resources.list(stack_id)
        #return_stack.update(list)
        return return_stack


    def get_stack_id(self):
        return self.stack_id

    def list(self, args=None):
        kwargs = {}
        if args:
            kwargs = {'limit': args.get['limit'],
                      'marker': args.get['marker'],
                      'filters': utils.format_parameters(args.get['filters']),
                      'global_tenant': args.get['global_tenant'],
                      'show_deleted': args.get['show_deleted']}
        stacks = self.client.stacks.list(**kwargs)
        fields = ['id', 'stack_name', 'stack_status', 'creation_time']
        #utils.print_list(stacks, fields)
        return stacks

    def list_resources(self, stack_id):
        resources_raw = self.client.resources.list(stack_id)
        resources = []
        for resource_raw in resources_raw:
            resources.append(resource_raw.to_dict())
        return resources

    def list_resource_ids(self, stack_id):
        resources_raw = self.client.resources.list(stack_id)
        resource_ids = []
        for resource_raw in resources_raw:
            resource_id = resource_raw.to_dict().get('physical_resource_id')
            if resource_id:
                resource_ids.append(resource_id)
        return resource_ids

    def get_resources(self, stack_id, resource_names=[]):
        resources = {}
        for resource_name in resource_names:
            try:
                resource = self.client.resources.get(stack_id, resource_name)
                resources[resource_name] = resource.to_dict()
            except:
                resources[resource_name] = None
        return resources