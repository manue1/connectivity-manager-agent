#!/usr/bin/python

import json

from bottle import Bottle, response, request
from core.agent import Agent as CMAgent

__author__ = 'beb'

def not_found(message):
    response.body = message
    response.status = 404
    return response

def encode_dict_json(data_dict):
    data_json = json.dumps(data_dict)
    return data_json

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
        self._app.route('/hosts', method="POST", callback=self._hosts_select)

        # ToDo: QoS methods
        #self._app.route('/qos', method="GET", callback=self._qos_list)
        #self._app.route('/qos', method="POST", callback=self._qos_set)

    def start(self):
        self._app.run(host=self._host, port=self._port)

    def _welcome(self):
        response.body = "Welcome to the Connectivity Manager Agent"
        response.status = 200
        return response

    def _hosts_list(self):
        """
        List all OpenStack hypervisors
        """
        self.agent = CMAgent()

        hypervisors = self.agent.list_hypervisors()

        response.body = encode_dict_json(hypervisors)
        print "Hypervisor list response"
        print response.body
        response.status = 200
        response.content_type = 'application/json'
        return response

    def _hosts_select(self):
        """
        Select hypervisor to deploy Stack to
        """
        # TODO implement Select hypervisor method
        pass


if __name__ == '__main__':
    server = Application(host='0.0.0.0', port=8091)
    print('Connectivity Manager Agent serving on port 8091...')
    server.start()
