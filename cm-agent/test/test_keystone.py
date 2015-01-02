#!/usr/bin/python

from clients.keystone import Client
from core import agent

__author__ = 'beb'

if __name__ == '__main__':

    ksclient = Client()

    print 'token: %s' % ksclient.get_token()
    print 'endpoint: %s' % ksclient.get_endpoint()
    print 'network endpoint: %s' % agent._get_endpoint('network')

