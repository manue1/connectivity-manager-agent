#!/usr/bin/python

import os
import httplib
import requests
import time
import json

__author__ = 'mpa'

PUBLIC_NET = '2e2bc7f9-c29c-467c-94b6-5ef3724d79ac'
PRIVATE_NET = 'fd704f1b-9238-4c2c-a0f5-4ffb4543e33a'
PRIVATE_SUBNET = 'ab4595bf-12d5-4e92-baa8-b5dfb3c1a31d'

STATIC_CONFIG_PATH = '../data/static_config.json'

class Template(object):
    def __init__(self, user_config_file):
        user_config = json.loads(user_config_file)
        static_config = json.loads(open(os.path.join(os.path.dirname(__file__), STATIC_CONFIG_PATH)).read())

        #Connector
        connector_args = {}
        connector_args['name'] = static_config['nubomedia']['connector']['name']
        connector_args['image'] = static_config['nubomedia']['connector']['image']
        connector_args['flavor'] = user_config['nubomedia']['connector']['flavor']
        connector_args['key_name'] = user_config['nubomedia']['key_name']
        connector_args['port_enable'] = True
        connector_args['floating_ip_enable'] = True
        connector_args['security_groups'] = []
        connector_args['user_data'] = static_config['nubomedia']['connector']['user_data']

        self.connector = Server(connector_args)

        print self.connector.dump_to_dict()

        media_server_group_args = {}
        media_server_group_args['user_data'] = static_config['nubomedia']['media_server_group']['user_data']
        print media_server_group_args['user_data']



class Server(object):
    def __init__(self, args):
    #def __init__(self, name, image, flavor, key_name, port_enable=False, floating_ip_enable=False, security_groups=None, user_data=None):
        self.name = args.get('name')
        self.type = "OS::Nova::Server"
        self.properties = {}
        self.properties['name'] = args.get('name')
        self.properties['image'] = args.get('image')
        self.properties['flavor'] = args.get('flavor')
        self.properties['key_name'] = args.get('key_name')
        if args.get('user_data'):
            self.properties['user_data_format'] = 'RAW'
            self.properties['user_data'] = {}
            self.properties['user_data']['str_replace'] = args.get('user_data')

        self.port_enable = args.get('port_enable')
        self.floating_ip_enable = args.get('floating_ip_enable')
        self.security_groups = args.get('security_groups')
        if self.port_enable or self.floating_ip_enable:
            self.port_enable = True
            self.port = Port(name="%s_port" % self.name, security_groups = self.security_groups)
            self.properties['networks'] = []
            self.properties['networks'] = [{'port': {'get_resource': '%s' % self.port.name}}]

        if self.floating_ip_enable:
            self.floating_ip = FloatingIP(name='%s_floating_ip' % self.name, port=self.port)

    def dump_to_dict(self):
        resources = {}
        server_config = {}
        server_config['type'] = self.type
        server_config['properties'] = self.properties
        resources['%s' % self.name] = server_config

        if self.port_enable:
            port_config = self.port.dump_to_dict()
            resources.update(port_config)

        if self.floating_ip_enable:
            floating_ip_config = self.floating_ip.dump_to_dict()
            resources.update(floating_ip_config)

        return resources

class Port(object):
    def __init__(self, name, security_groups = None):
        self.name = name
        self.type = 'OS::Neutron::Port'
        self.properties = {}
        self.properties['network_id'] = PRIVATE_NET
        self.properties['fixed_ips'] = [{'subnet_id': PRIVATE_SUBNET}]
        if security_groups:
            self.properties['security_groups']=[]
            for security_group in security_groups:
                self.properties['security_groups'].append({'get_resource':security_group.name})

    def dump_to_dict(self):
        resource = {}
        port_config = {}
        port_config['type'] = self.type
        port_config['properties'] = self.properties
        resource[self.name] = port_config

        return resource


class FloatingIP(object):
    def __init__(self, name, port):
        self.name = name
        self.type = 'OS::Neutron::FloatingIP'
        self.properties = {}
        self.properties['floating_network_id'] = PUBLIC_NET
        self.properties['port_id'] = {'get_resource': '%s' % port.name}

    def dump_to_dict(self):
        resource = {}
        floating_ip_config = {}
        floating_ip_config['type'] = self.type
        floating_ip_config['properties'] = self.properties
        resource[self.name] = floating_ip_config

        return resource


class SecurityGroup(object):
    def __init__(self, name=None):
        self.name = name or 'security_group'
        self.type = 'OS::Neutron::SecurityGroup'
        self.properties = {}
        self.properties['rules'] = []

        ssh_rule = Rule(remote_ip_prefix='0.0.0.0/0', port_range_max=22, port_range_min=22, protocol='tcp')
        icmp_rule = Rule(remote_ip_prefix='0.0.0.0/0', protocol='icmp')

        self.properties['rules'].append(ssh_rule.dump_to_dict())
        self.properties['rules'].append(icmp_rule.dump_to_dict())

    def dump_to_dict(self):
        resource = {}
        security_group_config = {}
        security_group_config['type'] = self.type
        security_group_config['properties'] = self.properties
        resource[self.name] = security_group_config
        return resource

class Rule(object):
    def __init__(self, remote_ip_prefix, protocol, port_range_max=None, port_range_min=None):
        self.remote_ip_prefix = remote_ip_prefix
        self.protocol = protocol
        self.port_range_max = port_range_max
        self.port_range_min = port_range_min


    def dump_to_dict(self):
        config = {}
        config['remote_ip_prefix'] = self.remote_ip_prefix
        config['protocol'] = self.protocol
        if self.port_range_min and self.port_range_max:
            config['port_range_max'] = self.port_range_max
            config['port_range_min'] = self.port_range_min

        return config

class AutoScalingGroup(object):
    def __init__(self, name, min_size, max_size, image, flavor, key_name, policies = None, security_groups = None, user_data = None):
        self.name = name
        self.type = 'AWS::AutoScaling::AutoScalingGroup'
        self.properties = {}
        self.properties['MinSize'] = min_size
        self.properties['MaxSize'] = max_size
        self.properties['AvailabiltyZones'] = [{'FN::GetAZs':''}]

        self.launch_config = LaunchConfiguration(name = '%s_launch_configuration' % self.name, image = image, flavor = flavor, key_name = key_name, security_groups = security_groups, user_data = user_data)
        self.properties['LaunchConfigurationName'] = { 'get_resource': self.launch_config.name }

        self.alarms = []
        self.actions = []
        if policies:
            for policy in policies:
                policy_name = str(policy.get('name'))

                policy_action = policy.get('action')
                adjustment_type = str(policy_action.get('adjustment_type'))
                scaling_adjustment = str(policy_action.get('scaling_adjustment'))
                cooldown = str(policy_action.get('cooldown'))
                action = ScalingPolicy(name = '%s_policy' % policy_name, adjustment_type=adjustment_type, scaling_adjustment=scaling_adjustment, cooldown=cooldown, scaling_group=self)
                self.actions.append(action)

                policy_alarm = policy.get('alarm')
                meter_name = str(policy_alarm.get('meter_name'))
                comparison_operator = str(policy_alarm.get('comparison_operator'))
                threshold = str(policy_alarm.get('threshold'))
                statistic = str(policy_alarm.get('statistic'))
                period = str(policy_alarm.get('period'))
                alarm = Alarm(name = '%s_alarm' % policy_name, meter_name=meter_name, statistic = statistic, comparison_operator=comparison_operator, threshold=threshold, period = period, scaling_group=self, policy = action)
                self.alarms.append(alarm)

    def dump_to_dict(self):
        resources = {}
        scaling_group_config = {}
        scaling_group_config['type'] = self.type
        scaling_group_config['properties'] = self.properties
        resources[self.name] = scaling_group_config

        resources.update(self.launch_config.dump_to_dict())

        for alarm in self.alarms:
            resources.update(alarm.dump_to_dict())
        for action in self.actions:
            resources.update(action.dump_to_dict())

        return resources


class LaunchConfiguration(object):
    def __init__(self, name, image, flavor, key_name, security_groups = None, user_data = None):
        self.name = name
        self.type = 'AWS::AutoScaling::LaunchConfiguration'
        self.properties={}
        self.properties['ImageID'] = image
        self.properties['InstanceType'] = flavor
        self.properties['KeyName'] = key_name

        if security_groups:
            self.properties['SecurityGroups']=[]
            for security_group in security_groups:
                self.properties['SecurityGroups'].append({'get_resource':security_group.name})

        if user_data:
            self.properties['UserData'] = {}
            self.properties['UserData']['str_replace'] = user_data

    def dump_to_dict(self):
        resource = {}
        launch_config = {}
        launch_config['type'] = self.type
        launch_config['properties'] = self.properties
        resource[self.name] = launch_config
        return resource


class ScalingPolicy(object):
    def __init__(self, name, adjustment_type, scaling_group, cooldown, scaling_adjustment):
        self.name = name
        self.type = 'AWS::AutoScaling::ScalingPolicy'
        self.properties = {}
        self.properties['AdjustmentType'] = adjustment_type
        self.properties['AutoScalingGroupName'] = scaling_group.name
        self.properties['Cooldown'] = cooldown
        self.properties['ScalingAdjustment'] = scaling_adjustment

    def dump_to_dict(self):
        resource = {}
        scaling_config = {}
        scaling_config['type'] = self.type
        scaling_config['properties'] = self.properties
        resource[self.name] = scaling_config
        return resource

class Alarm(object):
    def __init__(self, name, meter_name, statistic, comparison_operator, period, threshold, scaling_group, policy):
        self.name = name
        self.type = 'OS::Ceilometer::Alarm'
        self.properties = {}
        self.properties['meter_name'] = meter_name
        self.properties['statistic'] = statistic
        self.properties['comparison_operator'] = comparison_operator
        self.properties['period'] = period
        self.properties['evaluation_periods'] = 1
        self.properties['threshold'] = threshold
        self.properties['repeat_actions'] = 'true'
        self.properties['alarm_actions'] = [{'get_attr':[policy.name, 'AlarmUrl']}]
        self.properties['matching_metadata'] = {'metadata.user_metadata.groupname':{'get_resource':scaling_group.name}}

    def dump_to_dict(self):
        resource = {}
        alarm_config = {}
        alarm_config['type'] = self.type
        alarm_config['properties'] = self.properties
        resource[self.name] = alarm_config
        return resource

if __name__ == '__main__':
    # f = open(os.path.join('/net/u/mpa/', 'nubomedia.json'))
    # config_file = f.read()
    # #print config_file
    #
    # config = json.loads(config_file)
    # config['nubomedia']['name'] = "nubo_stack12"
    # config_file1 = json.dumps(config)
    # config['nubomedia']['name'] = "nubo_stack13"
    # config_file2 = json.dumps(config)
    # #print config_file1
    #
    # #data_json_load = json.loads(config_file)
    # #print data_json_load
    # #data_json = json.dumps(data_json_load)
    # #print data_json
    # #payload = config_file
    # #print payload
    # #r = requests.get('http://localhost:8080/action=deploy', data=payload)
    #
    # #url = 'http://localhost:8080/action=dispose'
    # #url = 'http://localhost:8080/action=deploy'
    # #headers = {'content-type': 'application/json'}
    #
    # #response = requests.post(url, data=payload, headers=headers)
    # #response = requests.get(url)
    # #request = requests.get(url, data=payload, headers=headers)
    #
    # connection = httplib.HTTPConnection('10.147.65.176:8080')
    # headers = {'Content-type': 'application/json'}
    #
    # connection.request('POST', '/stacks', config_file1, headers)
    # response = connection.getresponse()
    # resp = response.read()
    #
    # print resp
    # stack_id = json.loads(resp)['stack']['id']
    # print stack_id
    #
    #
    # connection.request('POST', '/stacks', config_file2, headers)
    # response = connection.getresponse()
    # resp = response.read()
    #
    # print resp
    # stack_id1 = json.loads(resp)['stack']['id']
    # print stack_id1
    #
    # connection.request('GET', '/stacks', config_file, headers)
    # response = connection.getresponse()
    # print "stack overview: %s" % response.read()
    #
    # #cookie = requests.session().cookies.get("session")
    #
    # #headers.setdefault("set-cookie",cookie)
    #
    # #connection = httplib.HTTPConnection('localhost:8080')
    #
    # #headers.setdefault("set-cookie", cookie)
    # connection.request('GET', '/stacks/%s' % stack_id, config_file, headers)
    # response = connection.getresponse()
    # print response.read()
    #
    # time.sleep(10)
    #
    # connection.request('DELETE', '/stacks/%s' % stack_id, config_file, headers)
    # response = connection.getresponse()
    # print response.read()
    #
    # connection.request('DELETE', '/stacks/%s' % stack_id1, config_file, headers)
    # response = connection.getresponse()
    # print response.read()


    import yaml

    template_file = open(os.path.join(os.path.dirname(__file__), '/net/u/mpa/templates/nubo_templ.yaml')).read()
    config_file = open(os.path.join(os.path.dirname(__file__), '/net/u/mpa/nubomedia.json')).read()

    template = yaml.load(template_file, Loader=yaml.Loader)
    config = json.loads(config_file)

    name = config['nubomedia']['name']

    key_name = config['nubomedia']['key_name']
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

    # print template_file

    #print len(config['nubomedia']['media_server_group']['policies'])
    #print template['resources']['connector']['properties']
    #template['resources']['connector']['properties']['networks'] = {'port':'test'}
    #print template['resources']['connector']['properties']['networks']


    #print template['resources']['server_security_group']

    #connector_user_data = {}
    #connector_user_data['template'] = ("#!/bin/bash -v\n"
    #                                   "sudo sed -i \"s/^\(kmf.transport[ \t]*\)=thrift/\\1 = rabbitmq/\" /etc/kurento/media-connector.properties\n"
    #                                   "sudo sed -i \"\$arabbitmq.address=$BROKER_IP:5672\" /etc/kurento/media-connector.properties\n"
    #                                   "sudo service kmf-media-connector restart\n")

    #connector_user_data['params'] = {'$BROKER_IP': {'get_attr': ['broker', 'first_address']}}
    connector_user_data=    {'template':"#!/bin/bash -v\n"
                                "sudo sed -i \"s/^\(kmf.transport[ \\t]*\)=thrift/\\1 = rabbitmq/\" /etc/kurento/media-connector.properties\n"
                                "sudo sed -i \"\$arabbitmq.address=$BROKER_IP:5672\" /etc/kurento/media-connector.properties\n"
                                "sudo service kmf-media-connector restart\n",
                            'params':{'$BROKER_IP': {'get_attr': ['broker', 'first_address']}}}

    sec_group = SecurityGroup(name = 'security_group')
    connector = Server(name='connector', flavor='m1.small', image='kurento-connector', key_name='tub-nubomedia',
                       port_enable=True, floating_ip_enable=True, user_data=connector_user_data, security_groups=[sec_group])
    broker = Server(name='broker', flavor='m1.small', image='kurento-broker', key_name='tub-nubomedia',
                    port_enable=True)
    print config['nubomedia']['media_server_group']['policies']
    media_server_group = AutoScalingGroup(name='media_server_group', key_name='tub-nubomedia', flavor = 'm1.medium', image = 'kurento-media-server', min_size=1, max_size=3, security_groups=[sec_group], policies=config['nubomedia']['media_server_group']['policies'])



    sec_group_config = sec_group.dump_to_dict()
    connector_config = connector.dump_to_dict()
    broker_config = broker.dump_to_dict()
    media_server_config = media_server_group.dump_to_dict()


    resources = {}
    resources.update(connector_config)
    resources.update(broker_config)
    resources.update(sec_group_config)
    resources.update(media_server_config)

    #print yaml.dump(resources)

    #print (template['resources']['connector_port'])
    print template
    print resources
    #print (connector_config['connector_port'])
    #print yaml.dump(broker_config['broker_port'])
    print yaml.dump(resources)


    #print json.loads(config_file)
    template = Template(user_config_file=config_file)