#!/usr/bin/python

# Copyright (c) 2013-2015, Intel Performance Learning Solutions Ltd, Intel Corporation.
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

from emm.core.orchestrator import ServiceOrchestrator

from emm.util import utils as utils
import os
from bottle import hook, route, run, request, response

USER_FILE = '/net/u/mpa/user.cfg'
#USER_FILE = '/etc/nubomedia/user.cfg'

orchestrators = {}


@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization'


@route('/stacks', method='OPTIONS')
def deploy():
    response.body = "OK"
    response.status = 200
    return response


@route('/stacks/<stack_id>', method='OPTIONS')
def deploy(stack_id):
    response.body = "OK"
    response.status = 200
    return response


@route('/stacks', method="GET")
def list():
    stacks = []
    for orchestrator in orchestrators.values():
        stacks.append(orchestrator.so_d.show())
        print stacks
    response.body = utils.dict_to_json({"stacks": stacks})
    response.status = 200
    return response


@route('/stacks/<stack_id>', method="GET")
def show(stack_id):
    print "requested stack id: %s" % stack_id
    orchestrator = orchestrators.get(stack_id)
    if orchestrator is not None:
        stack = orchestrator.so_d.show()
        response.body = utils.dict_to_json({'stack': stack})
        response.status = 200
        response.content_type = 'application/json'
        print "orchestrator: %s for stack (%s)" % (orchestrator, stack_id)
    else:
        response.body = utils.dict_to_json({"Error": "Stack (%s) was not found" % stack_id})
        response.status = 404
        response.content_type = 'application/json'
        print "Stack (%s) not found" % stack_id
    print "response body: %s" % response.body
    return response


@route('/stacks', method='POST')
def deploy():
    config = request.body.getvalue()
    orchestrator = ServiceOrchestrator()
    stack = orchestrator.so_d.deploy(config_file=config)
    stack_id = stack['stack']['id']
    global orchestrators
    if orchestrators.get(stack_id) is None:
        orchestrators[stack_id] = orchestrator
    stack = orchestrator.so_d.show()
    response.body = utils.dict_to_json({"stack": stack})
    response.status = 200
    response.content_type = 'application/json'
    return response


@route('/stacks/<stack_id>', method="DELETE")
def dispose(stack_id):
    orchestrator = orchestrators.get(stack_id)
    if orchestrator is not None:
        status = orchestrator.so_d.dispose()
        stack = orchestrator.so_d.show()
        response.body = utils.dict_to_json({"stack": stack})
        response.status = 200
        response.content_type = 'application/json'
        print "orchestrator: %s for stack (%s)" % (orchestrator, stack_id)
        if status is None:
            del orchestrators[stack_id]
    else:
        response.body = utils.dict_to_json({"Error": "Stack (%s) was not found." % stack_id})
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

