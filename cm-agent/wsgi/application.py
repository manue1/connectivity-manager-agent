# Copyright 2015 Technische Universitaet Berlin
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

import json
import logging

from bottle import Bottle, response, request
from core.agent import Agent as CMAgent

__author__ = 'beb'


"""
# Private error methods
"""


def bad_request(param):
    response.body = param
    response.status = 400
    response.content_type = 'application/json'
    return response


def internal_error(message):
    response.body = message
    response.status = 500
    response.content_type = 'application/json'
    return response


def not_found(message):
    response.body = message
    response.status = 404
    response.content_type = 'application/json'
    return response


def encode_dict_json(data_dict):
    data_json = json.dumps(data_dict)
    return data_json


"""
# ReST API
"""


class Application:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._app = Bottle()
        self._route()
        self._debug = True
        self.agent = CMAgent()

    def _route(self):
        # Welcome Screen
        self._app.route('/', method="GET", callback=self._welcome)

        # Hypervisor methods
        self._app.route('/hosts', method="GET", callback=self._hosts_list)

        # QoS methods
        self._app.route('/qoses', method=["POST", "OPTIONS"], callback=self._qoses_set)

    def start(self):
        self._app.run(host=self._host, port=self._port)

    def _welcome(self):
        response.body = "Welcome to the Connectivity Manager Agent"
        response.status = 200
        return response

    def _hosts_list(self):
        """
        List all OpenStack hypervisors with runtime details
        """
        agent = CMAgent()
        hypervisors = agent.list_hypervisors()

        response.body = encode_dict_json(hypervisors)
        logging.debug('Hypervisor list response', response.body)
        response.status = 200
        response.content_type = 'application/json'
        return response

    def _qoses_set(self):
        """
        Set QoS for VMs
        """
        qos_json = request.body.getvalue()
        logging.debug('QoS JSON is: %s', qos_json)
        if not qos_json:
            return bad_request('This POST methods requires a valid JSON')
        try:
            set_qos = self.agent.set_qos(qos_json)
        except Exception, exc:
            logging.error(exc.message)
            return internal_error(exc.message)
        response.status = 200
        response.body = encode_dict_json(set_qos)
        logging.debug('QoS processed: %s', response.body)
        return response

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s_%(process)d:%(lineno)d [%(levelname)s] %(message)s',level=logging.INFO)
    server = Application(host='0.0.0.0', port=8091)
    print('Connectivity Manager Agent serving on port 8091...')
    server.start()
