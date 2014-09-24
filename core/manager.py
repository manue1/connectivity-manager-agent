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


class TopologyManger(object):
    def __init__(self, stack, config):

        self.connector = {}
        self.connector['name'] = 'connector'
        self.connector['image'] = 'kurento-connector'
        self.connector['flavor'] = config['nubomedia']['connector']['flavor']
        self.connector['key_name'] = config['nubomedia']['key_name']

        self.broker = {}
        self.broker['name'] = 'broker'
        self.broker['image'] = 'kurento-image'
        self.broker['flavor'] = config['nubomedia']['broker']['flavor']
        self.broker['key_name'] = config['nubomedia']['key_name']

        self.media_server_group = {}
        self.media_server_group['name'] = 'media_server_group'
        self.media_server_group['image'] = 'kurento-media-server'
        self.media_server_group['flavor'] = config['nubomedia']['media_server_group']['flavor']
        self.media_server_group['min_size'] = config['nubomedia']['media_server_group']['min_size']
        self.media_server_group['max_size'] = config['nubomedia']['media_server_group']['max_size']
        self.media_server_group['policies'] = config['nubomedia']['media_server_group']['policies']

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
                    self.media_server_group['private_ips'] = output.get('output_value')

    def dump(self):
        resources = {}
        resources.update({'connector':self.connector})
        resources.update({'broker':self.broker})
        resources.update({'media_server_group':self.media_server_group})
        return {'resources':resources}
