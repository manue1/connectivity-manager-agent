#!/usr/bin/python

import json
import logging

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
        ###Welcome Screen
        self._app.route('/', method="GET", callback=self._welcome)

        ###Hypervisor methods
        self._app.route('/hypervisors', method="GET", callback=self._hypervisor_list)
        self._app.route('/hypervisors', method="POST", callback=self._hypervisor_select)
        self._app.route('/hypervisors/<id>', method="GET", callback=self._hypervisor_show)

    def start(self):
        self._app.run(host=self._host, port=self._port)

    def _welcome(self):
        response.body = "Welcome to the Connectivity Manager Agent"
        response.status = 200
        return response

    def _hypervisor_list(self):
        """
        List all OpenStack hypervisor
        """
        self.agent = CMAgent()

        hypervisors = self.agent.list_hypervisors()
        print "These are the hypervisors"
        print hypervisors

        response.body = encode_dict_json(hypervisors)
        print "This is the response body:"
        print response.body
        response.status = 200
        response.content_type = 'application/json'
        return response

    def _hypervisor_select(self):
        """
        Select hypervisor to deploy Stack to
        """
        # TODO implement Select hypervisor method
        pass

    def _hypervisor_show(self):
        """
        Show details of a OpenStack hypervisor
        """
        # TODO implement Show hypervisor method
        pass


if __name__ == '__main__':
    server = Application(host='0.0.0.0', port=8091)
    print('Connectivity Manager Agent serving on port 8091...')
    server.start()
