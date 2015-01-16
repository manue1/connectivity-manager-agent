#!/usr/bin/python

import logging
import os
import httplib

__author__ = 'beb'

PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
HOST = 'localhost'


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s_%(process)d:%(lineno)d [%(levelname)s] %(message)s',level=logging.INFO)

    # Establish connection to CM Agent
    connection = httplib.HTTPConnection('%s:8091' % HOST)
    headers = {'Content-type': 'application/json'}

    # Get the test config
    f = open(os.path.join('%s/test/' % PATH, 'test_qos_config.json'))
    config_file = f.read()
    logging.debug(config_file)

    connection.request('POST', '/qoses', config_file, headers)
    response = connection.getresponse()
    resp = (response.read())

    logging.debug('response: %s' % resp)