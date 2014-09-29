__author__ = 'mpa'

from util.KeystoneManager import KeystoneManager
from core.orchestrator import ServiceOrchestrator
from util.HeatManager import HeatManager
from heatclient import client
from heatclient.v1 import stacks
import os
import yaml
import pkg_resources
import json

if __name__ == '__main__':

    keystoneManager = KeystoneManager(username='username', password='password')

    kwargs = {}

    endpoint = keystoneManager.get_endpoint(service_type='orchestration')
    #print "endpoint: %s" % endpoint

    token = keystoneManager.get_token()
    kwargs['token'] = keystoneManager.get_token()
    print "token: %s" % kwargs.get('token')
    tenant_id = keystoneManager.get_tenant_id()
    tenant_name = keystoneManager.get_tenant_name()

    kwargs['username'] = keystoneManager.get_username()
    print "username: %s" % kwargs.get('username')

    kwargs['password'] = keystoneManager.get_password()
    print "password: %s" % kwargs.get('password')

    print "endpoint: %s" % endpoint
    print "token: %s" % token
    print "tenant_id: %s" % tenant_id
    print "tenant_name: %s" %  tenant_name

    #heatClient = client.Client("1", endpoint=endpoint, token = token)



    heatClient = HeatManager(endpoint=endpoint, **kwargs)
    resources = heatClient.get_resources(stack_id = 'f159b25a-26d3-4e57-8563-d6afb1d2132a', resource_names=['broker','connector'])
    print resources

    #f = open(os.path.join("/net/u/mpa/templates", 'nubo_templ.yaml'))
    #template_file = f.read()
    #f.close()

    #kcargs = {
    #        'stack_name': "nubomedia_stack",
    #        'template': template_file
   #     }
    #print "list: %s" % heatClient.stacks.list()
    #print "stack: %s" % heatClient.stacks.create(**kcargs)


    #kwargs['tenant_name'] = keystoneManager.get_tenant_name()
    #print "tenant_name: %s" % kwargs.get('tenant_name')

    #kwargs['tenant_id'] = keystoneManager.get_tenant_id()
    #print "tenant_id: %s" % kwargs.get('tenant_id')

    #orchestrator = ServiceOrchestrator(heat_url=endpoint, auth_token=auth_token, username=username, password=password)
    #orchestrator = ServiceOrchestrator(heat_url=endpoint, **kwargs)

    #f = open(os.path.join('/net/u/mpa/', 'nubomedia.json'))
    #config_file = f.read()
    #print config_file


    #print "deploy: %s" % orchestrator.so_d.deploy(config_file=config_file)
    #print "deploy: %s" % orchestrator.so_d.deploy(name="test_Stack", parameters=['bsg_flavor=m1.medium;msg_flavor=m1.medium'])



    #print "state: %s" % orchestrator.so_d.state()
    #print "show: %s" % orchestrator.so_d.show()
    #print "dispose: %s" % orchestrator.so_d.dispose()

