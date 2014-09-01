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


__author__ = 'giuseppe'


class Topology(object):
    def __init__(self, name, id = None, heat_template = None,  service_instance_components = [] ):
        self.id = id
        self.name = name
        self.heat_template = heat_template
        self.service_instance_components = service_instance_components

    def __str__(self):
        t = ""
        t +='name: %s\n' %(self.name)
        for s in self.service_instance_components:
            t +='%s\n' %(s)
        return t




class Unit(object):

    def __init__(self, id, name, ext_id = None, ips = {}, networks = {}):
        self.id = id
        self.name = name
        self.ext_id = ext_id
        self.ips = ips
        self.networks = networks


class Relation(object):
    pass





