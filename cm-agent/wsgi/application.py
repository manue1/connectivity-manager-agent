#!/usr/bin/python

import logging

from bottle import Bottle, response, request

__author__ = 'beb'

def not_found(message):
    response.body = message
    response.status = 404
    # response.content_type = 'application/json'
    return response


class Application:

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._app = Bottle()
        self._route()
        self._debug = True

    def _route(self):
        ###Welcome Screen
        self._app.route('/', method="GET", callback=self._welcome)

        ###Initialize Agent??
        self._app.route('/init', method="POST", callback=self._init)

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

    def _init(self):
        """
        Initialize the Agent.
        """
        # TODO implement Init method
        pass

    def _hypervisor_list(self):
        """
        List all OpenStack hypervisor
        """
        # TODO implement List hypervisor method

        pass

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
    server.start()
