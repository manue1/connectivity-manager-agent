#!/usr/bin/python

__author__ = 'beb'

class Tenant(object):
    def __init__(self, clients):
        self.clients = clients
        self.novaclient = clients.get('novaclient')

        self.tenant_id = None

    def retrieve(self):
        tenant_info = self.heatclient.deploy(name=self.config.name, template=self.config.get_template())

        stack_information = self.heatclient.deploy(name=self.config.name, template=self.config.get_template())
        #get stack id for the new stack
        self.stack_id = stack_information['stack']['id']
        return stack_information

    def delete(self):
        if self.stack_id is not None:
            self.heatclient.delete(stack_id=self.stack_id)



class Host(object):
    def __init__(self, clients, config, resource_id=None):
        self.config = config
        self.name = config.name
        self.resource_id = resource_id
        self.novaclient = clients.get('novaclient')
        self.ceilometerclient = clients.get('ceilometerclient')

    def show_static_information(self):
        static_information = {}
        static_information['key_name'] = self.config.key_name
        static_information['flavor'] = self.config.flavor
        static_information['image'] = self.config.image
        return static_information

    #returns runtime information for this instance
    def show_runtime_information(self):
        runtime_information = {}
        #print "name: %s, id: %s, config: %s" % (self.name, self.resource_id, self.config)
        if self.resource_id is not None:
            runtime_information = utils.filter_dict(data_dict=self.novaclient.show_resource(self.resource_id),
                                                    properties=['addresses', 'id', 'status', 'key_name', 'created'])
            runtime_information['cpu_util'] = self.ceilometerclient.get_last_sample_value(resource_id=self.resource_id,
                                                                                          meter_name='cpu_util')
        #print "instance information: %s" % runtime_information
        return runtime_information