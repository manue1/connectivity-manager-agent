#!/usr/bin/env python

__author__ = 'beb'

from setuptools import setup, find_packages

setup(
    name='ConnectivityManagerAgent',
    version='0.1',
    packages= find_packages(),
    install_requires=[
        'bottle',
        'python-novaclient',
        'python-neutronclient',
        'python-keystoneclient',
    ],
    url='',
    license='',
    author='beb',
    author_email='',
    description='Connectivity Manager Agent',
)
