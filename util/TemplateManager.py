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

import yaml
import json
import os

TEMPLATE_PATH = '/etc/nubomedia/nubo_templ.yaml'
#TEMPLATE_PATH = '/net/u/mpa/templates/nubo_templ.yaml'


def substitute_template(config_file, template_file = None):
    if template_file is None:
        template_file = open(os.path.join(os.path.dirname(__file__), TEMPLATE_PATH)).read()

    template = yaml.load(template_file, Loader = yaml.Loader)
    config = json.loads(config_file)

    name = config['nubomedia']['name']

    key_name = config['nubomedia']['key_name']
    template['resources']['connector']['properties']['key_name'] = str(key_name)
    template['resources']['broker']['properties']['key_name'] = str(key_name)
    template['resources']['msg_launch_configuration']['properties']['KeyName'] = str(key_name)

    template['resources']['connector']['properties']['flavor'] = str(config['nubomedia']['connector']['flavor'])
    template['resources']['broker']['properties']['flavor'] = str(config['nubomedia']['broker']['flavor'])

    template['resources']['media_server_group']['properties']['MinSize'] = str(config['nubomedia']['media_server_group']['min_size'])
    template['resources']['media_server_group']['properties']['MaxSize'] = str(config['nubomedia']['media_server_group']['max_size'])
    template['resources']['msg_launch_configuration']['properties']['InstanceType'] = str(config['nubomedia']['media_server_group']['flavor'])

    template['resources']['msg_scaleup_alarm']['properties']['meter_name']  = str(config['nubomedia']['media_server_group']['policies'][0]['alarm']['meter_name'])
    template['resources']['msg_scaleup_alarm']['properties']['comparison_operator']  = str(config['nubomedia']['media_server_group']['policies'][0]['alarm']['comparison_operator'])
    template['resources']['msg_scaleup_alarm']['properties']['threshold']  = str(config['nubomedia']['media_server_group']['policies'][0]['alarm']['threshold'])
    template['resources']['msg_scaleup_alarm']['properties']['statistic']  = str(config['nubomedia']['media_server_group']['policies'][0]['alarm']['statistic'])
    template['resources']['msg_scaleup_alarm']['properties']['period']  = str(config['nubomedia']['media_server_group']['policies'][0]['alarm']['period'])
    template['resources']['msg_scaleup_policy']['properties']['AdjustmentType']  = str(config['nubomedia']['media_server_group']['policies'][0]['action']['adjustment_type'])
    template['resources']['msg_scaleup_policy']['properties']['ScalingAdjustment']  = str(config['nubomedia']['media_server_group']['policies'][0]['action']['scaling_adjustment'])
    template['resources']['msg_scaleup_policy']['properties']['Cooldown']  = str(config['nubomedia']['media_server_group']['policies'][0]['action']['cooldown'])

    template['resources']['msg_scaledown_alarm']['properties']['meter_name']  = str(config['nubomedia']['media_server_group']['policies'][1]['alarm']['meter_name'])
    template['resources']['msg_scaledown_alarm']['properties']['comparison_operator']  = str(config['nubomedia']['media_server_group']['policies'][1]['alarm']['comparison_operator'])
    template['resources']['msg_scaledown_alarm']['properties']['threshold']  = str(config['nubomedia']['media_server_group']['policies'][1]['alarm']['threshold'])
    template['resources']['msg_scaledown_alarm']['properties']['statistic']  = str(config['nubomedia']['media_server_group']['policies'][1]['alarm']['statistic'])
    template['resources']['msg_scaledown_alarm']['properties']['period']  = str(config['nubomedia']['media_server_group']['policies'][1]['alarm']['period'])
    template['resources']['msg_scaledown_policy']['properties']['AdjustmentType']  = str(config['nubomedia']['media_server_group']['policies'][1]['action']['adjustment_type'])
    template['resources']['msg_scaledown_policy']['properties']['ScalingAdjustment']  = str(config['nubomedia']['media_server_group']['policies'][1]['action']['scaling_adjustment'])
    template['resources']['msg_scaledown_policy']['properties']['Cooldown']  = str(config['nubomedia']['media_server_group']['policies'][1]['action']['cooldown'])

    template_file = yaml.dump(template)

    return name, template_file