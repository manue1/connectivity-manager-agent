__author__ = 'beb'

from setuptools import setup

setup(
    name='ConnectivityManagerAgent',
    version='0.1',
    packages=['clients', 'core', 'model', 'wsgi', 'test'],
    install_requires=[
        'bottle',
    ],
    url='',
    license='',
    author='beb',
    author_email='',
    description='Nubomedia CM',
)
