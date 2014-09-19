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


class Server(object):
    def __init__(self, name, image, flavor, key_name, port_enable=False, floating_ip_enable=False, security_groups=None, user_data=None):
        self.name = name
        self.type = "OS::Nova::Server"
        self.properties = {}
        self.properties['name'] = name
        self.properties['image'] = image
        self.properties['flavor'] = flavor
        self.properties['key_name'] = key_name
        if user_data:
            self.properties['user_data_format'] = 'RAW'
            self.properties['user_data'] = {}
            self.properties['user_data']['str_replace'] = user_data

        self.port_enable = port_enable
        if port_enable or floating_ip_enable:
            self.port_enable = True
            self.port = Port(name="%s_port" % name, security_groups = security_groups)
            self.properties['networks'] = []
            self.properties['networks'] = [{'port': {'get_resource': '%s' % self.port.name}}]

        self.floating_ip_enable = floating_ip_enable
        if floating_ip_enable:
            self.floating_ip = FloatingIP(name='%s_floating_ip' % name, port=self.port)

    def parse_to_dict(self):
        resources = {}
        server_config = {}
        server_config['type'] = self.type
        server_config['properties'] = self.properties
        resources['%s' % self.name] = server_config

        if self.port_enable:
            port_config = self.port.parse_to_dict()
            resources.update(port_config)

        if self.floating_ip_enable:
            floating_ip_config = self.floating_ip.parse_to_dict()
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
                self.properties['security_groups'].append({'get_resource':'%s' % security_group.name})

    def parse_to_dict(self):
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

    def parse_to_dict(self):
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

        self.properties['rules'].append(ssh_rule.parse_to_dict())
        self.properties['rules'].append(icmp_rule.parse_to_dict())

    def parse_to_dict(self):
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


    def parse_to_dict(self):
        config = {}
        config['remote_ip_prefix'] = self.remote_ip_prefix
        config['protocol'] = self.protocol
        if self.port_range_min and self.port_range_max:
            config['port_range_max'] = self.port_range_max
            config['port_range_min'] = self.port_range_min

        return config

class AutoScalingGroup(object):
    pass
class LaunchConfiguration(object):
    pass
class ScalingPolicy(object):
    pass
class Alarm(object):


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

    sec_group_config = sec_group.parse_to_dict()
    connector_config = connector.parse_to_dict()
    broker_config = broker.parse_to_dict()

    resources = {}
    resources.update(connector_config)
    resources.update(broker_config)
    resources.update(sec_group_config)

    #print yaml.dump(resources)

    #print (template['resources']['connector_port'])
    print (template['resources']['connector']['properties']['user_data'])
    print resources['connector']['properties']['user_data']
    #print (connector_config['connector_port'])
    #print yaml.dump(broker_config['broker_port'])
    print yaml.dump(resources)
