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

from heatclient.v1 import Client as heatClient
from heatclient.common import template_utils
from heatclient.common import utils
from heatclient.openstack.common import jsonutils

import heatclient.exc as exc



class HeatManager(object):

    def __init__(self, endpoint, **kwargs):

        kc_args={}
        if kwargs.get('tenant_id'):
            kc_args['tenant_id'] = kwargs.get('tenant_id')
        else:
            kc_args['tenant_name'] = kwargs.get('tenant_name')
        if kwargs.get('token'):
            kc_args['token'] = kwargs.get('token')
        #else:
            kc_args['username'] = kwargs.get('username')
            kc_args['password'] = kwargs.get('password')

        self.heatClient = heatClient(endpoint=endpoint, **kc_args)

    def deploy(self, **kwargs):
        kcargs = {
            'stack_name': kwargs.get('name'),
            'disable_rollback': not(bool(kwargs.get('enable_rollback'))),
            'parameters': utils.format_parameters(kwargs.get('parameters')),
            'template': kwargs.get('template')
        }

        timeout = kwargs.get('timeout') or kwargs.get('create_timeout')
        if timeout:
            kcargs['timeout_mins'] = timeout

        stack = self.heatClient.stacks.create(**kcargs)
        if stack is not None:
            stack_id = stack['stack']['id']
        return stack_id

    def delete(self, stack_id):
        fields = {'stack_id': stack_id}
        try:
            self.heatClient.stacks.delete(**fields)
            return "Stack %s deletion in progress" % stack_id
        except exc.HTTPNotFound as e:
            print(e)


    def show(self, stack_id, properties = []):
        fields = {'stack_id': stack_id}
        try:
            stack = self.heatClient.stacks.get(**fields)
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
        stacks = self.heatClient.stacks.list(**kwargs)
        fields = ['id', 'stack_name', 'stack_status', 'creation_time']
        #utils.print_list(stacks, fields)
        return stacks

    def output_list(self, stack_id):
        '''Show available outputs.'''
        try:
            stack = self.heatClient.stacks.get(stack_id=stack_id)
        except exc.HTTPNotFound:
            raise exc.CommandError('Stack not found: %s' % stack_id)
        else:
            status = stack.to_dict()['stack_status']
            if status == "CREATE_COMPLETE":
                outputs = stack.to_dict()['outputs']
                fields = ['output_key', 'description']
                formatters = {
                    'output_key': lambda x: x['output_key'],
                    'description': lambda x: x['description'],
                }
                utils.print_list(outputs, fields, formatters=formatters)

    def output_show(self, stack_id):
        '''Show a specific stack output.'''
        try:
            stack = self.heatClient.stacks.get(stack_id=stack_id)
        except exc.HTTPNotFound:
            raise exc.CommandError('Stack not found: %s' % stack_id)
        else:
            status = stack.to_dict()['stack_status']
            if status == "CREATE_COMPLETE":
                for output in stack.to_dict().get('outputs', []):
                    if output['output_key'] == output:
                        value = output['output_value']
                        break
                    else:
                        return
                print (jsonutils.dumps(value, indent=2, ensure_ascii=False))

    def get_resource_ids(self, stack_id, resource_names=[]):
        resources_raw = self.heatClient.resources.list(stack_id)
        resources = {}
        for resource_raw in resources_raw:
            resource = resource_raw.to_dict()
            resource_name = resource['resource_name']
            if resource_name in resource_names:
                resources.update({resource_name:resource['physical_resource_id']})
        return resources

    def get_resources(self, stack_id, resource_names=[]):
        resources = {}
        for resource_name in resource_names:
            try:
                resource = self.heatClient.resources.get(stack_id, resource_name)
                resources[resource_name] = resource.to_dict()
            except:
                resources[resource_name] = None
        return resources
