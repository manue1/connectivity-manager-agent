#!/usr/bin/python

#   Copyright (c) 2013-2015, Intel Performance Learning Solutions Ltd, Intel Corporation.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from core.orchestrator import ServiceOrchestrator
from util.KeystoneManager import KeystoneManager
from bottle import hook, route, run, request, response, HTTPResponse
#from heatclient.common import utils
#import json
import util.utils as utils
import os

#USER_FILE = '/net/u/mpa/user.cfg'
USER_FILE = '/etc/nubomedia/user.cfg'

orchestrators = {}


@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

@route('/stacks', method = 'OPTIONS')
def deploy():
    return HTTPResponse(status=200, body="OK")

@route('/stacks/<stack_id>', method = 'OPTIONS')
def deploy(stack_id):
    return HTTPResponse(status=200, body="OK")

@route('/stacks', method = "GET")
def list():
    stacks = []
    for orchestrator in orchestrators.values():
        #stacks[orchestrator.so_d.executor.name] = orchestrator.so_d.executor.stack_id
        #stacks.append(orchestrator.so_d.show(properties = ['stack_name', 'id', 'creation_time','parameters','stack_status']))
        stacks.append(orchestrator.so_d.show())
        #stacks.append(orchestrator.so_d.show())
        print stacks
    response.body = utils.dict_to_json({"stacks":stacks})
    response.status = 200
    return response

@route('/stacks/<stack_id>', method = "GET")
def show(stack_id):
    print "requested stack id: %s" % stack_id
    orchestrator = orchestrators.get(stack_id)
    if orchestrator is not None:
        #stack = orchestrator.so_d.show(properties = ['stack_name', 'id', 'creation_time','parameters','stack_status', 'outputs'])
        stack = orchestrator.so_d.show()
        response.body = utils.dict_to_json({'stack':stack})
        response.status = 200
        response.content_type = 'application/json'
        print "orchestrator: %s for stack (%s)" % (orchestrator, stack_id)
    else:
        response.body = utils.dict_to_json({"Error":"Stack (%s) was not found" % stack_id})
        response.status = 404
        response.content_type = 'application/json'
        print "Stack (%s) not found" % stack_id
    print "response body: %s" % response.body
    return response

@route('/stacks', method = 'POST')
def deploy():
    config = request.body.getvalue()
    username, password = utils.get_username_and_password(USER_FILE)
    keystoneManager = KeystoneManager(username=username, password=password)

    endpoint = keystoneManager.get_endpoint(service_type='orchestration')
    print "endpoint: %s" % endpoint

    kwargs = {}
    kwargs['username'] = keystoneManager.get_username()
    print "username: %s" % kwargs.get('username')

    kwargs['password'] = keystoneManager.get_password()
    print "password: %s" % kwargs.get('password')

    kwargs['token'] = keystoneManager.get_token()
    print "token: %s" % kwargs.get('token')

    orchestrator = ServiceOrchestrator(endpoint=endpoint, **kwargs)

    stack_id = str(orchestrator.so_d.deploy(config_file=config))

    stack = {}
    global orchestrators
    if orchestrators.get(stack_id) is None:
        orchestrators[stack_id] = orchestrator
        #stack = {orchestrator.so_d.executor.name:stack_id}

    #stack = orchestrator.so_d.show(properties = ['stack_name', 'id', 'creation_time','parameters','stack_status', 'output'])
    stack = orchestrator.so_d.show()
    response.body = utils.dict_to_json({"stack":stack})
    response.status = 200
    response.content_type = 'application/json'
    return response


@route('/stacks/<stack_id>', method = "DELETE")
def dispose(stack_id):
    orchestrator = orchestrators.get(stack_id)
    if orchestrator is not None:
        status = orchestrator.so_d.dispose()
        #stack = orchestrator.so_d.show(properties = ['stack_name', 'id', 'creation_time', 'stack_status', 'output'])
        stack = orchestrator.so_d.show()
        response.body = utils.dict_to_json({"stack":stack})
        response.status = 200
        response.content_type = 'application/json'
        print "orchestrator: %s for stack (%s)" % (orchestrator, stack_id)
        if status is None:
            del orchestrators[stack_id]
    else:
        response.body = utils.dict_to_json({"Error":"Stack (%s) was not found." % stack_id})
        response.status = 404
        response.content_type = 'application/json'
        print "Stack not found"
    return response


if __name__ == '__main__':
    if os.path.isfile(USER_FILE):
        run(host='0.0.0.0', port=8080, debug=True)
    else:
        print 'The user file "%s" does not exists. Please run "./emm.sh init" or set it manually.' % USER_FILE
        exit(1)


