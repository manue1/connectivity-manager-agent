#!/usr/bin/python

import httplib

__author__ = 'beb'


if __name__ == '__main__':

    connection = httplib.HTTPConnection('0.0.0.0:8091')
    headers = {'Content-type': 'application/json'}

    # Retrieve list of hypervisors
    connection.request('GET', '/hosts')
    response = connection.getresponse()
    print response.read()