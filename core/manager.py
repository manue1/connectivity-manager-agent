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

__author__ = 'gca'
import config

class TopologyManger(object):
    def __init__(self, stack, config, resources):

        self.connector = {}
        self.connector['name'] = 'connector'
        self.connector['image'] = 'kurento-connector'
        self.connector['flavor'] = config.connector.flavor
        self.connector['key_name'] = config.connector.key_name
        if resources.get('connector'):
            self.connector['status'] = resources['connector']['resource_status']
        else:
            self.connector['status'] = 'Null'

        self.broker = {}
        self.broker['name'] = 'broker'
        self.broker['image'] = 'kurento-broker'
        self.broker['flavor'] = config.broker.flavor
        self.broker['key_name'] = config.broker.key_name
        if resources.get('broker'):
            self.broker['status'] = resources['broker']['resource_status']
        else:
            self.broker['status'] = 'Null'

        self.media_server_group = {}
        self.media_server_group['name'] = 'media_server_group'
        self.media_server_group['image'] = 'kurento-media-server'
        self.media_server_group['flavor'] = config.media_server_group.launch_config.flavor
        self.media_server_group['min_size'] = config.media_server_group.min_size
        self.media_server_group['max_size'] = config.media_server_group.max_size
        self.media_server_group['policies'] = config.media_server_group.policies
        if resources.get('media_server_group'):
            self.media_server_group['status'] = resources['media_server_group']['resource_status']
        else:
            self.media_server_group['status'] = 'Null'

        outputs = stack.get('outputs')
        if outputs:
            for output in outputs:
                output_key = output.get('output_key')
                if output_key == 'connector_private_ip':
                    self.connector['private_ip'] = output.get('output_value')
                elif output_key == 'connector_public_ip':
                    self.connector['public_ip'] = output.get('output_value')
                elif output_key == 'broker_private_ip':
                    self.broker['private_ip'] = output.get('output_value')
                elif output_key == 'media_server_group_ips':
                    self.media_server_group['private_ips'] = output.get('output_value').split(',')

    def dump(self):
        resources = {}
        resources.update({'connector':self.connector})
        resources.update({'broker':self.broker})
        resources.update({'media_server_group':self.media_server_group})
        return {'resources':resources}
