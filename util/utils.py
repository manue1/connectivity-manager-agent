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

__author__ = 'mpa'

import prettytable
import json

def dict_to_table(data_dict, formatters={}):
    pt = prettytable.PrettyTable(['Property', 'Value'],
                                 caching=False, print_empty=False)
    pt.align = 'l'

    for field in data_dict.keys():
        if field in formatters:
            pt.add_row([field, formatters[field](data_dict[field])])
        else:
            pt.add_row([field, data_dict[field]])
    return (pt.get_string(sortby='Property'))

def dict_to_json(data_dict):
    data_json = json.dumps(data_dict)
    return data_json

if __name__ == '__main__':
    stacks_dict = {"stack_id":["1234","5678"], "stack_names":["test1","test2"]}
    print stacks_dict.keys()
    print dict_to_table(stacks_dict)
    stack_json = dict_to_json(stacks_dict)
    print stack_json