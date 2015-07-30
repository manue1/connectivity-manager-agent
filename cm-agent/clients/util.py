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

import logging

PATH = '/etc/cm-agent'

__author__ = 'beb'


def read_properties():
    props = {}
    with open('%s/cm-agent.properties' % PATH, 'r') as f:
        logging.info('Using %s/cm-agent.properties file', PATH)
        for line in f:
            line = line.rstrip()

            if "=" not in line:
                continue
            if line.startswith("#"):
                continue
            k, v = line.split("=", 1)
            props[k] = v
        return props

def get_credentials():
    # print "Fetch credentials from environment variables"
    creds = {}
    # creds['tenant_name'] = os.environ.get('OS_TENANT_NAME', '')
    # creds['username'] = os.environ.get('OS_USERNAME', '')
    # creds['password'] = os.environ.get('OS_PASSWORD', '')
    # creds['auth_url'] = os.environ.get('OS_AUTH_URL', '')
    # print 'Credentials: %s' % creds
    # ##Fetch Credentials from Configuration
    logging.info('Fetch Credentials from SysUtil')
    conf = read_properties()
    # conf = DatabaseManager().get_by_name(Configuration, "SystemConfiguration")[0]
    #print "props: %s" % conf.props
    creds['tenant_name'] = conf.get('os_tenant', '')
    creds['username'] = conf.get('os_username', '')
    creds['password'] = conf.get('os_password', '')
    creds['auth_url'] = conf.get('os_auth_url', '')
    logging.info('Credentials: %s', creds)
    return creds
