#!/usr/bin/python

import os
import httplib
import requests
import time
import json

__author__ = 'mpa'

if __name__ == '__main__':
    ###Get the config file for testing purposes
    f = open(os.path.join('/net/u/mpa/', 'nubomedia.json'))
    config_file = f.read()
    #print config_file

    ###Set config files and names
    config = json.loads(config_file)
    config['nubomedia']['name'] = "nubo_stack20"
    config_file1 = json.dumps(config)
    config['nubomedia']['name'] = "nubo_stack"
    config_file2 = json.dumps(config)
    print config_file1


    # #data_json_load = json.loads(config_file)
    # #print data_json_load
    # #data_json = json.dumps(data_json_load)
    # #print data_json
    # #payload = config_file
    # #print payload
    # #r = requests.get('http://localhost:8080/action=deploy', data=payload)

    # #url = 'http://localhost:8080/action=dispose'
    # #url = 'http://localhost:8080/action=deploy'
    # #headers = {'content-type': 'application/json'}

    # #response = requests.post(url, data=payload, headers=headers)
    # #response = requests.get(url)
    # #request = requests.get(url, data=payload, headers=headers)

    #connection = httplib.HTTPConnection('80.96.122.53:8080')
    ###Connection to the local server
    connection = httplib.HTTPConnection('10.147.65.176:8080')
    headers = {'Content-type': 'application/json'}


    #connection.request('POST', '/stacks', config_file1, headers)
    #response = connection.getresponse()
    #resp = response.read()

    #print resp
    #stack_id = json.loads(resp)['stack']['id']
    #print stack_id


    ###If you do not create a new stack you can put here the stack id
    stack_id = 'bad99a6e-2231-4638-8a47-b7c6f4fd37d4'
    ###Create a new stack with the given config and name
    if True:
        connection.request('POST', '/stacks', config_file2, headers)
        response = connection.getresponse()
        resp = (response.read())

        print 'response: %s' % resp
        stack_id = json.loads(resp)['stack']['id']
        print stack_id

    #connection.request('GET', '/stacks', config_file, headers)
    #response = connection.getresponse()
    #print "stack overview: %s" % json.dumps(response.read())

    ###GET stack information of the deployed stack
    connection.request('GET', '/stacks/%s' % stack_id, config_file, headers)
    response = connection.getresponse()
    print response.read()

    ###Wait a moment
    time.sleep(10)

    ###GET stack information for all stacks
    connection.request('GET', '/stacks', config_file, headers)
    response = connection.getresponse()
    print "stack overview: %s" % response.read()

    ###DELETE the deployed stack
    connection.request('DELETE', '/stacks/%s' % stack_id, config_file, headers)
    response = connection.getresponse()
    print response.read()

    #connection.request('DELETE', '/stacks/%s' % stack_id1, config_file, headers)
    #response = connection.getresponse()
    #print response.read()

