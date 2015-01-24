import json
import os
import logging

PATH = '/etc/nubomedia'
#PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) + "/etc"

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


