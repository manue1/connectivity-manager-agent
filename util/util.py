# Copyright 2014 Technische Universitaet Berlin
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
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
from model.Entities import Topology
from model.Services import ServiceInstance, State


__author__ = 'giuseppe'

import yaml


def stack_parser(template):
    t =  yaml.load(template)
    services = []
    for key in t:
        #print key, 'corresponds to', doc[key]
        if 'Resources' in key:
            for r in t[key]:
                s = ServiceInstance(r, state = State.Initialised)
                services.append(s)
    return Topology('ims', service_instance_components=services)

