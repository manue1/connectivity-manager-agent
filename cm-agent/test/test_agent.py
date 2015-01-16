#!/usr/bin/python

import logging
from core.agent import *

__author__ = 'beb'


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s_%(process)d:%(lineno)d [%(levelname)s] %(message)s',level=logging.DEBUG)

    agent = Agent()

    # ------------------
    # Test listing Hypervisors including their VMs & QoS:
    # ------------------
    hypervisors = agent.list_hypervisors()
