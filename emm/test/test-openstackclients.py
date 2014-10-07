#!/usr/bin/python
from keystoneclient.v3.client import Client as ksclient
from novaclient.v1_1.client import Client as novaclient
from ceilometerclient import client as cmclient

from util import utils, heat







# from heatclient.v1.client import Client as heatclient
#from KeystoneManager import KeystoneManager
import yaml
import os

__author__ = 'mpa'

USER_FILE = '/net/u/mpa/user.cfg'
AUTH_URL = 'http://80.96.122.48:5000/v2.0'
AUTH_URL1 = 'http://80.96.122.48:5000/v3'

if __name__ == '__main__':
    tenant_name, username, password = utils.get_credentials(USER_FILE)

    kwargs = {}
    kwargs['username'] = username
    kwargs['password'] = password
    #kwargs['auth_url'] = AUTH_URL1
    kwargs['tenant_name'] = tenant_name

    keystone = ksclient(auth_url=AUTH_URL1, **kwargs)
    #keystone = ksclient(username=None, password=None, tenant_name=None, project_name=None, **kwargs)

    keystone.authenticate()
    print keystone.auth_token
    print keystone.tenant_id
    print keystone.tenant_name
    print keystone.project_id
    print keystone.project_name
    #print keystone.endpoints.list()


    kwargs['token'] = keystone.auth_token

    #kwargs['project_name'] = TENANT
    #kwargs['endpoint_type'] = 'publicURL'
    endpoint = 'http://80.96.122.48:8004/v1/fba35e226f4441c6b3b8bbd276f5d41a'

    heatcl = heat.Client(endpoint=endpoint, **kwargs)
    #print heat.stacks.list()
    #print heat.resources.list(stack_id='422d94f2-8b98-4391-a2e6-6040ce62fec2')

    template_file = open(os.path.join(os.path.dirname(__file__), '/net/u/mpa/templates/nubo_templ.yaml')).read()

    print template_file
    template = yaml.load(template_file, Loader=yaml.Loader)

    print heatcl.deploy(name='teststack', template=template_file)



    #print keystone.endpoints.list()


    #keystone = KeystoneManager(username=username, password=password)
    #print keystone.token
    #print keystone.endpoints.list()

    kwargs = {}
    kwargs['username'] = username
    kwargs['password'] = password
    #kwargs['auth_url'] = AUTH_URL
    #novaargs['endpoint'] = AUTH_URL
    #kwargs['service_type'] = 'compute'
    #kwargs['endpoint_type'] = 'publicURL'

    #nova = novaclient(**kwargs)
    nova = novaclient(username, password, tenant_name, auth_url=AUTH_URL)
    #nova = novaclient(username=username,password=password,tenant_id='nubomedia',auth_url=AUTH_URL)
    #nova = novaclient(**kwargs)
    #nova = novaclient.Client(3,username, password=password, auth_url=AUTH_URL)
    #nova.authenticate()
    servers = nova.servers.list()
    for server in servers:
        print server._info
    print nova.servers.get('336e32cf-8958-4f2b-918e-408e1959a41b')._info
    #print nova.endpoints.list()


    #ceilo = cmclient.get_client(2,username=username,password=password,tenant_name=username,auth_url=AUTH_URL)
    kwargs = {}
    kwargs['version'] = 2
    kwargs['username'] = username
    kwargs['password'] = password
    #kwargs['auth_url'] = AUTH_URL
    kwargs['tenant_name'] = username

    ceilo = cmclient.get_client(auth_url=AUTH_URL, **kwargs)

    print ceilo.alarms.list()
    resources = ceilo.resources.get('336e32cf-8958-4f2b-918e-408e1959a41b')._info
    print resources
    for resource in resources:
        print resource

    query = [dict(field='resource_id', op='eq', value='336e32cf-8958-4f2b-918e-408e1959a41b')]
    samples = ceilo.samples.list(meter_name='cpu_util', limit=1, q=query)

    for sample in samples:
        print sample._info['counter_volume']
