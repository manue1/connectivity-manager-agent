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

import os
import json
import yaml

CONFIG_PATH = '/etc/nubomedia/'
#CONFIG_PATH = '/net/u/mpa/project/nubomedia/emm/data/'
#STATIC_ENV_PATH = BASE_PATH + 'environment.yaml'
#STATIC_MEDIA_SERVER_PATH = BASE_PATH + 'nubomedia_media_server.yaml'
STATIC_CONFIG_PATH = CONFIG_PATH + 'static_config.json'



class Config(object):
    def __init__(self, user_config_file):
        user_config = json.loads(user_config_file)
        static_config = json.loads(open(os.path.join(os.path.dirname(__file__), STATIC_CONFIG_PATH)).read())

        ###Stack name###
        self.name = user_config['nubomedia']['name']

        ###Networks###
        self.private_net = user_config['nubomedia']['networks']['private_net']
        self.private_subnet = user_config['nubomedia']['networks']['private_subnet']
        self.public_net = user_config['nubomedia']['networks']['public_net']

        ###Connector###
        connector_args = {}
        connector_args['name'] = static_config['nubomedia']['connector']['name']
        connector_args['image'] = static_config['nubomedia']['connector']['image']
        connector_args['flavor'] = user_config['nubomedia']['connector']['flavor']
        connector_args['key_name'] = user_config['nubomedia']['key_name']
        connector_args['port_enable'] = static_config['nubomedia']['connector']['port_enable']
        connector_args['floating_ip_enable'] = static_config['nubomedia']['connector']['floating_ip_enable']
        connector_args['private_net'] = self.private_net
        connector_args['private_subnet'] = self.private_subnet
        connector_args['public_net'] = self.public_net
        connector_args['user_data'] = static_config['nubomedia']['connector']['user_data']
        connector_args['security_group'] = static_config['nubomedia']['connector']['security_group']
        self.connector = Server(**connector_args)

        ###Broker###
        broker_args = {}
        broker_args['name'] = static_config['nubomedia']['broker']['name']
        broker_args['image'] = static_config['nubomedia']['broker']['image']
        broker_args['flavor'] = user_config['nubomedia']['broker']['flavor']
        broker_args['key_name'] = user_config['nubomedia']['key_name']
        broker_args['port_enable'] = static_config['nubomedia']['broker']['port_enable']
        broker_args['floating_ip_enable'] = static_config['nubomedia']['broker']['floating_ip_enable']
        broker_args['private_net'] = self.private_net
        broker_args['private_subnet'] = self.private_subnet
        broker_args['public_net'] = self.public_net
        broker_args['user_data'] = static_config['nubomedia']['broker']['user_data']
        broker_args['security_group'] = static_config['nubomedia']['broker']['security_group']
        self.broker = Server(**broker_args)

        ###Media Server Group###
        media_server_group_args = {}
        media_server_group_args['group_name'] = static_config['nubomedia']['media_server_group']['group_name']
        media_server_group_args['instance_name'] = static_config['nubomedia']['media_server_group']['instance_name']
        media_server_group_args['image'] = static_config['nubomedia']['media_server_group']['image']
        media_server_group_args['key_name'] = user_config['nubomedia']['key_name']
        media_server_group_args['flavor'] = user_config['nubomedia']['media_server_group']['flavor']
        media_server_group_args['min_size'] = user_config['nubomedia']['media_server_group']['min_size']
        media_server_group_args['max_size'] = user_config['nubomedia']['media_server_group']['max_size']
        media_server_group_args['user_data'] = static_config['nubomedia']['media_server_group']['user_data']
        media_server_group_args['security_group'] = static_config['nubomedia']['media_server_group']['security_group']
        media_server_group_args['private_net'] = self.private_net
        media_server_group_args['private_subnet'] = self.private_subnet
        media_server_group_args['public_net'] = self.public_net


        policies_user = user_config['nubomedia']['media_server_group']['policies']
        policies = []
        i = 1
        for policy_user in policies_user:
            policy = {}
            policy['name'] = policy_user.get('name') or 'scaling_%s' % i

            action = {}
            action['adjustment_type'] = policy_user['action']['adjustment_type']
            action['scaling_adjustment'] = policy_user['action']['scaling_adjustment']
            action['cooldown'] = policy_user['action']['cooldown']
            policy['action'] = action

            alarm = {}
            alarm['meter_name'] = policy_user['alarm']['meter_name']
            alarm['comparison_operator'] = policy_user['alarm']['comparison_operator']
            alarm['threshold'] = policy_user['alarm']['threshold']
            alarm['statistic'] = policy_user['alarm']['statistic']
            alarm['period'] = policy_user['alarm']['period']
            alarm['evaluation_periods'] = static_config['nubomedia']['media_server_group']['policies']['alarm'][
                'evaluation_periods']
            alarm['repeat_actions'] = static_config['nubomedia']['media_server_group']['policies']['alarm'][
                'repeat_actions']
            policy['alarm'] = alarm

            policies.append(policy)
            i += 1

        media_server_group_args['policies'] = policies
        self.media_server_group = Heat_AutoScalingGroup(**media_server_group_args)

    def get_template(self):
        resources = {}
        resources.update(self.connector.dump_to_dict())
        resources.update(self.broker.dump_to_dict())
        resources.update(self.media_server_group.dump_to_dict())

        outputs = {}
        outputs['broker_private_ip'] = {}
        outputs['broker_private_ip']['value'] = {'get_attr': [self.broker.name, 'first_address']}
        outputs['broker_private_ip']['description'] = 'Private IP of the broker'

        outputs['connector_private_ip'] = {}
        outputs['connector_private_ip']['value'] = {'get_attr': [self.connector.name, 'first_address']}
        outputs['connector_private_ip']['description'] = 'Private IP of the connector'

        outputs['connector_public_ip'] = {}
        outputs['connector_public_ip']['value'] = {'get_attr': [self.connector.floating_ip.name, 'floating_ip_address']}
        outputs['connector_public_ip']['description'] = 'Public IP of the connector'

        #outputs['media_server_group_ips'] = {}
        #outputs['media_server_group_ips']['value'] = {'get_attr': [self.media_server_group.name, 'InstanceList']}
        #outputs['media_server_group_ips']['description'] = 'Private IPs of the media server group'

        template = {}
        template['heat_template_version'] = '2013-05-23'
        template['resources'] = resources
        template['outputs'] = outputs

        yaml.add_representer(unicode, lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:str', value))
        yaml.add_representer(utils.literal_unicode, utils.literal_unicode_representer)
        #return yaml.dump(template, allow_unicode=True, default_flow_style=False, encoding = False, default_style='')

        #f = open('/net/u/mpa/templ.yaml', 'w')
        #f.write(yaml.dump(template))
        return yaml.dump(template)


class Server(object):
    def __init__(self, **kwargs):
        ###Resource Type###
        self.type = "OS::Nova::Server"

        ###Basic parameters###
        self.name = kwargs.get('name')
        self.image = kwargs.get('image')
        self.flavor = kwargs.get('flavor')
        self.key_name = kwargs.get('key_name')

        ###Security Group###
        security_group_config = kwargs.get('security_group')
        security_group_args = {}
        security_group_args['name'] = security_group_config.get('name')
        rules_user = security_group_config.get('rules')
        rules = []
        for rule_user in rules_user:
            rule = {}
            rule['name'] = rule_user['name']
            rule['remote_ip_prefix'] = rule_user['remote_ip_prefix']
            rule['protocol'] = rule_user['protocol']
            rule['port_range_min'] = rule_user.get('port_range_min')
            rule['port_range_max'] = rule_user.get('port_range_max')
            rules.append(rule)

        security_group_args['rules'] = rules
        self.security_groups = []
        self.security_groups.append(SecurityGroup(**security_group_args))

        ###User Data###
        if kwargs.get('user_data'):
            self.user_data_format = 'RAW'
            self.user_data = {}
            self.user_data = kwargs.get('user_data')
        else:
            self.user_data = None

        ###Port and floating IP config###
        self.port_enable = kwargs.get('port_enable')
        self.floating_ip_enable = kwargs.get('floating_ip_enable')
        if self.port_enable or self.floating_ip_enable:
            self.port_enable = True
            port_args = {}
            port_args['name'] = '%s_port' % self.name
            port_args['private_net'] = kwargs.get('private_net')
            port_args['private_subnet'] = kwargs.get('private_subnet')
            port_args['security_groups'] = self.security_groups
            self.port = Port(**port_args)
            self.networks = [self.port.name]
        else:
            self.port = None
            self.networks = None
        if self.floating_ip_enable:
            floating_ip_args = {}
            floating_ip_args['name'] = '%s_floating_ip' % self.name
            floating_ip_args['public_net'] = kwargs.get('public_net')
            floating_ip_args['port'] = self.port
            self.floating_ip = FloatingIP(**floating_ip_args)
        else:
            self.floating_ip = None

    def dump_to_dict(self):
        resources = {}
        server_config = {}
        server_config['type'] = self.type
        properties = {}
        properties['name'] = self.name
        properties['image'] = self.image
        properties['flavor'] = self.flavor
        properties['key_name'] = self.key_name
        if self.user_data:
            properties['user_data_format'] = self.user_data_format
            properties['user_data'] = {}
            properties['user_data']['str_replace'] = {}
            properties['user_data']['str_replace']['params'] = self.user_data['params']
            properties['user_data']['str_replace']['template'] = utils.literal_unicode(self.user_data['template'])

        server_config['properties'] = properties
        resources[self.name] = server_config

        if self.port_enable or self.floating_ip_enable:
            for network in self.networks:
                properties['networks'] = [{'port': {'get_resource': network}}]
            port_config = self.port.dump_to_dict()
            resources.update(port_config)

        if self.floating_ip_enable:
            floating_ip_config = self.floating_ip.dump_to_dict()
            resources.update(floating_ip_config)

        for security_group in self.security_groups:
            resources.update(security_group.dump_to_dict())

        return resources


class Port(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = 'OS::Neutron::Port'
        self.network_id = kwargs.get('private_net')
        self.fixed_ips = kwargs.get('private_subnet')
        self.security_groups = kwargs.get('security_groups')

    def dump_to_dict(self):
        resource = {}
        port_config = {}
        port_config['type'] = self.type

        properties = {}
        properties['network_id'] = self.network_id
        properties['fixed_ips'] = [{'subnet_id': self.fixed_ips}]
        if self.security_groups:
            properties['security_groups'] = []
            for security_group in self.security_groups:
                properties['security_groups'].append({'get_resource': security_group.name})

        port_config['properties'] = properties
        resource[self.name] = port_config

        return resource


class FloatingIP(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = 'OS::Neutron::FloatingIP'

        self.floating_network_id = kwargs.get('public_net')
        self.port_id = kwargs.get('port').name

    def dump_to_dict(self):
        resource = {}
        floating_ip_config = {}
        floating_ip_config['type'] = self.type

        properties = {}
        properties['floating_network_id'] = self.floating_network_id
        properties['port_id'] = {'get_resource': self.port_id}

        floating_ip_config['properties'] = properties
        resource[self.name] = floating_ip_config

        return resource


class SecurityGroup(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = 'OS::Neutron::SecurityGroup'
        self.rules = []

        rules_config = kwargs.get('rules')
        for rule_config in rules_config:
            rule = Rule(**rule_config)
            self.rules.append(rule)


    def dump_to_dict(self):
        resource = {}
        security_group_config = {}
        security_group_config['type'] = self.type

        properties = {}
        properties['rules'] = []
        for rule in self.rules:
            properties['rules'].append(rule.dump_to_dict())

        security_group_config['properties'] = properties
        resource[self.name] = security_group_config
        return resource


class Rule(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.remote_ip_prefix = kwargs.get('remote_ip_prefix')
        self.protocol = kwargs.get('protocol')
        self.port_range_max = kwargs.get('port_range_max')
        self.port_range_min = kwargs.get('port_range_min')

    def dump_to_dict(self):
        rule_config = {}
        rule_config['remote_ip_prefix'] = self.remote_ip_prefix
        rule_config['protocol'] = self.protocol
        if self.port_range_min and self.port_range_max:
            rule_config['port_range_max'] = self.port_range_max
            rule_config['port_range_min'] = self.port_range_min

        return rule_config

class Heat_AutoScalingGroup(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('group_name')
        self.type = 'OS::Heat::AutoScalingGroup'

        self.instance_name = kwargs.get('instance_name')
        self.min_size = kwargs.get('min_size')
        self.max_size = kwargs.get('max_size')

        self.image = kwargs.get('image')
        self.flavor = kwargs.get('flavor')
        self.key_name = kwargs.get('key_name')
        self.user_data = kwargs.get('user_data')

        self.private_net = kwargs.get('private_net')
        self.private_subnet = kwargs.get('private_subnet')
        self.public_net = kwargs.get('public_net')

        ###Security Group###
        security_group_config = kwargs.get('security_group')
        security_group_args = {}
        security_group_args['name'] = security_group_config.get('name')
        rules_user = security_group_config.get('rules')
        rules = []
        for rule_user in rules_user:
            rule = {}
            rule['name'] = rule_user['name']
            rule['remote_ip_prefix'] = rule_user['remote_ip_prefix']
            rule['protocol'] = rule_user['protocol']
            rule['port_range_min'] = rule_user.get('port_range_min')
            rule['port_range_max'] = rule_user.get('port_range_max')
            rules.append(rule)
        security_group_args['rules'] = rules

        self.security_groups = []
        self.security_groups.append(SecurityGroup(**security_group_args))

        self.policies = kwargs.get('policies')
        self.alarms = []
        self.actions = []

        if self.policies:
            for policy in self.policies:
                policy_action = policy.get('action')
                policy_args = {}
                policy_args['name'] = '%s_policy' % policy.get('name')
                policy_args['adjustment_type'] = policy_action.get('adjustment_type')
                policy_args['scaling_adjustment'] = policy_action.get('scaling_adjustment')
                policy_args['cooldown'] = policy_action.get('cooldown')
                policy_args['scaling_group'] = self
                action = ScalingPolicy(**policy_args)
                self.actions.append(action)

                policy_alarm = policy.get('alarm')
                alarm_args = {}
                alarm_args['name'] = '%s_alarm' % policy.get('name')
                alarm_args['meter_name'] = policy_alarm.get('meter_name')
                alarm_args['comparison_operator'] = policy_alarm.get('comparison_operator')
                alarm_args['threshold'] = policy_alarm.get('threshold')
                alarm_args['statistic'] = policy_alarm.get('statistic')
                alarm_args['period'] = policy_alarm.get('period')
                alarm_args['evaluation_periods'] = policy_alarm.get('evaluation_periods')
                alarm_args['repeat_actions'] = policy_alarm.get('repeat_actions')
                alarm_args['scaling_group'] = self
                alarm_args['policy'] = action
                alarm = Alarm(**alarm_args)
                self.alarms.append(alarm)

    def dump_to_dict(self):
        resources = {}
        scaling_group_config = {}
        scaling_group_config['type'] = self.type

        group_properties = {}
        group_properties['min_size'] = self.min_size
        group_properties['max_size'] = self.max_size

        group_properties['resource'] = {}
        group_properties['resource']['type'] = "Nubomedia::MediaServer"
        #group_properties['resource']['type'] = "OS::Heat::Server"

        resource_properties = {}
        resource_properties['name'] = self.instance_name
        resource_properties['image'] = self.image
        resource_properties['flavor'] = self.flavor
        resource_properties['key_name'] = self.key_name
        resource_properties['metadata'] = {'metering.stack' : self.name}
        if self.user_data:
            resource_properties['user_data'] = {}
            resource_properties['user_data']['str_replace'] = {}
            resource_properties['user_data']['str_replace']['params'] = self.user_data['params']
            resource_properties['user_data']['str_replace']['template'] = utils.literal_unicode(self.user_data['template'])
        if self.security_groups:
            resource_properties['security_groups'] = []
            for security_group in self.security_groups:
                resource_properties['security_groups'].append({'get_resource': security_group.name})
        resource_properties['public_net'] = self.public_net
        resource_properties['private_net'] = self.private_net
        resource_properties['private_subnet'] = self.private_subnet

        group_properties['resource']['properties'] = resource_properties

        scaling_group_config['properties'] = group_properties

        resources[self.name] = scaling_group_config

        for alarm in self.alarms:
            resources.update(alarm.dump_to_dict())
        for action in self.actions:
            resources.update(action.dump_to_dict())
        for security_group in self.security_groups:
            resources.update(security_group.dump_to_dict())

        return resources


class AWS_AutoScalingGroup(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('group_name')
        self.type = 'AWS::AutoScaling::AutoScalingGroup'
        self.min_size = kwargs.get('min_size')
        self.max_size = kwargs.get('max_size')

        launch_args = {}
        launch_args['name'] = '%s_launch_configuration' % self.name
        launch_args['image'] = kwargs.get('image')
        launch_args['flavor'] = kwargs.get('flavor')
        launch_args['key_name'] = kwargs.get('key_name')
        launch_args['security_groups'] = kwargs.get('security_groups')
        launch_args['user_data'] = kwargs.get('user_data')

        self.launch_config = LaunchConfiguration(**launch_args)

        self.policies = kwargs.get('policies')
        self.alarms = []
        self.actions = []

        if self.policies:
            for policy in self.policies:
                policy_action = policy.get('action')
                policy_args = {}
                policy_args['name'] = '%s_policy' % policy.get('name')
                policy_args['adjustment_type'] = policy_action.get('adjustment_type')
                policy_args['scaling_adjustment'] = policy_action.get('scaling_adjustment')
                policy_args['cooldown'] = policy_action.get('cooldown')
                policy_args['scaling_group'] = self
                action = ScalingPolicy(**policy_args)
                self.actions.append(action)

                policy_alarm = policy.get('alarm')
                alarm_args = {}
                alarm_args['name'] = '%s_alarm' % policy.get('name')
                alarm_args['meter_name'] = policy_alarm.get('meter_name')
                alarm_args['comparison_operator'] = policy_alarm.get('comparison_operator')
                alarm_args['threshold'] = policy_alarm.get('threshold')
                alarm_args['statistic'] = policy_alarm.get('statistic')
                alarm_args['period'] = policy_alarm.get('period')
                alarm_args['evaluation_periods'] = policy_alarm.get('evaluation_periods')
                alarm_args['repeat_actions'] = policy_alarm.get('repeat_actions')
                alarm_args['scaling_group'] = self
                alarm_args['policy'] = action
                alarm = Alarm(**alarm_args)
                self.alarms.append(alarm)

    def dump_to_dict(self):
        resources = {}
        scaling_group_config = {}
        scaling_group_config['type'] = self.type

        properties = {}
        properties['MinSize'] = self.min_size
        properties['MaxSize'] = self.max_size
        properties['AvailabilityZones'] = [{'FN::GetAZs': ''}]
        properties['LaunchConfigurationName'] = {'get_resource': self.launch_config.name}

        scaling_group_config['properties'] = properties
        resources[self.name] = scaling_group_config

        resources.update(self.launch_config.dump_to_dict())

        for alarm in self.alarms:
            resources.update(alarm.dump_to_dict())
        for action in self.actions:
            resources.update(action.dump_to_dict())

        return resources


class LaunchConfiguration(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = 'AWS::AutoScaling::LaunchConfiguration'
        self.image = kwargs.get('image')
        self.flavor = kwargs.get('flavor')
        self.key_name = kwargs.get('key_name')
        self.security_groups = kwargs.get('security_groups')
        self.user_data = kwargs.get('user_data')


    def dump_to_dict(self):
        resource = {}
        launch_config = {}
        launch_config['type'] = self.type

        properties = {}
        properties['ImageId'] = self.image
        properties['InstanceType'] = self.flavor
        properties['KeyName'] = self.key_name

        if self.security_groups:
            properties['SecurityGroups'] = []
            for security_group in self.security_groups:
                properties['SecurityGroups'].append({'get_resource': security_group.name})

        if self.user_data:
            properties['UserData'] = {}
            properties['UserData']['str_replace'] = {}
            properties['UserData']['str_replace']['params'] = self.user_data['params']
            properties['UserData']['str_replace']['template'] = utils.literal_unicode(self.user_data['template'])

        launch_config['properties'] = properties
        resource[self.name] = launch_config
        return resource


class ScalingPolicy(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = 'AWS::AutoScaling::ScalingPolicy'
        self.adjustment_type = kwargs.get('adjustment_type')
        self.scaling_adjustment = kwargs.get('scaling_adjustment')
        self.cooldown = kwargs.get('cooldown')
        self.scaling_group = kwargs.get('scaling_group')

    def dump_to_dict(self):
        resource = {}
        scaling_config = {}
        scaling_config['type'] = self.type

        properties = {}
        properties['AdjustmentType'] = self.adjustment_type
        properties['AutoScalingGroupName'] = {'get_resource': self.scaling_group.name}
        properties['Cooldown'] = self.cooldown
        properties['ScalingAdjustment'] = self.scaling_adjustment

        scaling_config['properties'] = properties
        resource[self.name] = scaling_config
        return resource


class Alarm(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = 'OS::Ceilometer::Alarm'
        self.meter_name = kwargs.get('meter_name')
        self.statistic = kwargs.get('statistic')
        self.comparison_operator = kwargs.get('comparison_operator')
        self.period = kwargs.get('period')
        self.evaluation_periods = kwargs.get('evaluation_periods')
        self.threshold = kwargs.get('threshold')
        self.repeat_actions = kwargs.get('repeat_actions')
        self.policy = kwargs.get('policy')
        self.scaling_group = kwargs.get('scaling_group')

    def dump_to_dict(self):
        resource = {}
        alarm_config = {}
        alarm_config['type'] = self.type

        properties = {}
        properties['meter_name'] = self.meter_name
        properties['statistic'] = self.statistic
        properties['comparison_operator'] = self.comparison_operator
        properties['period'] = self.period
        properties['evaluation_periods'] = self.evaluation_periods
        properties['threshold'] = self.threshold
        properties['repeat_actions'] = self.repeat_actions
        properties['alarm_actions'] = [{'get_attr': [self.policy.name, 'AlarmUrl']}]
        if self.scaling_group.type == 'OS::Heat::AutoScalingGroup':
            properties['matching_metadata'] = {
                'metadata.user_metadata.stack': self.scaling_group.name }
        if self.scaling_group.type == 'AWS::AutoScaling::AutoScalingGroup':
            properties['matching_metadata'] = {
                'metadata.user_metadata.groupname': {'get_resource': self.scaling_group.name}}

        alarm_config['properties'] = properties
        resource[self.name] = alarm_config
        return resource


###OLD: substitute template with a static template file

TEMPLATE_PATH = '/etc/nubomedia/nubo_templ.yaml'
#TEMPLATE_PATH = '/net/u/mpa/templates/nubo_templ.yaml'


def substitute_template(config_file, template_file=None):
    if template_file is None:
        template_file = open(os.path.join(os.path.dirname(__file__), TEMPLATE_PATH)).read()

    template = yaml.load(template_file, Loader=yaml.Loader)
    config = json.loads(config_file)

    name = config['nubomedia']['name']
    print name
    key_name = config['nubomedia']['key_name']
    print key_name
    template['resources']['connector']['properties']['key_name'] = str(key_name)
    template['resources']['broker']['properties']['key_name'] = str(key_name)
    template['resources']['msg_launch_configuration']['properties']['KeyName'] = str(key_name)

    template['resources']['connector']['properties']['flavor'] = str(config['nubomedia']['connector']['flavor'])
    template['resources']['broker']['properties']['flavor'] = str(config['nubomedia']['broker']['flavor'])

    template['resources']['media_server_group']['properties']['MinSize'] = str(
        config['nubomedia']['media_server_group']['min_size'])
    template['resources']['media_server_group']['properties']['MaxSize'] = str(
        config['nubomedia']['media_server_group']['max_size'])
    template['resources']['msg_launch_configuration']['properties']['InstanceType'] = str(
        config['nubomedia']['media_server_group']['flavor'])

    template['resources']['msg_scaleup_alarm']['properties']['meter_name'] = str(
        config['nubomedia']['media_server_group']['policies'][0]['alarm']['meter_name'])
    template['resources']['msg_scaleup_alarm']['properties']['comparison_operator'] = str(
        config['nubomedia']['media_server_group']['policies'][0]['alarm']['comparison_operator'])
    template['resources']['msg_scaleup_alarm']['properties']['threshold'] = str(
        config['nubomedia']['media_server_group']['policies'][0]['alarm']['threshold'])
    template['resources']['msg_scaleup_alarm']['properties']['statistic'] = str(
        config['nubomedia']['media_server_group']['policies'][0]['alarm']['statistic'])
    template['resources']['msg_scaleup_alarm']['properties']['period'] = str(
        config['nubomedia']['media_server_group']['policies'][0]['alarm']['period'])
    template['resources']['msg_scaleup_policy']['properties']['AdjustmentType'] = str(
        config['nubomedia']['media_server_group']['policies'][0]['action']['adjustment_type'])
    template['resources']['msg_scaleup_policy']['properties']['ScalingAdjustment'] = str(
        config['nubomedia']['media_server_group']['policies'][0]['action']['scaling_adjustment'])
    template['resources']['msg_scaleup_policy']['properties']['Cooldown'] = str(
        config['nubomedia']['media_server_group']['policies'][0]['action']['cooldown'])

    template['resources']['msg_scaledown_alarm']['properties']['meter_name'] = str(
        config['nubomedia']['media_server_group']['policies'][1]['alarm']['meter_name'])
    template['resources']['msg_scaledown_alarm']['properties']['comparison_operator'] = str(
        config['nubomedia']['media_server_group']['policies'][1]['alarm']['comparison_operator'])
    template['resources']['msg_scaledown_alarm']['properties']['threshold'] = str(
        config['nubomedia']['media_server_group']['policies'][1]['alarm']['threshold'])
    template['resources']['msg_scaledown_alarm']['properties']['statistic'] = str(
        config['nubomedia']['media_server_group']['policies'][1]['alarm']['statistic'])
    template['resources']['msg_scaledown_alarm']['properties']['period'] = str(
        config['nubomedia']['media_server_group']['policies'][1]['alarm']['period'])
    template['resources']['msg_scaledown_policy']['properties']['AdjustmentType'] = str(
        config['nubomedia']['media_server_group']['policies'][1]['action']['adjustment_type'])
    template['resources']['msg_scaledown_policy']['properties']['ScalingAdjustment'] = str(
        config['nubomedia']['media_server_group']['policies'][1]['action']['scaling_adjustment'])
    template['resources']['msg_scaledown_policy']['properties']['Cooldown'] = str(
        config['nubomedia']['media_server_group']['policies'][1]['action']['cooldown'])

    template_file = yaml.dump(template)

    return name, template_file