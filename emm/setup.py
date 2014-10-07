# from distutils.core import setup
from setuptools import setup

setup(
    name='ElasticMediaManager',
    version='0.1',
    packages=['core', 'test', 'util', 'wsgi', 'model'],
    install_requires=[
        'python-heatclient',
        'bottle',
    ],
    url='',
    license='',
    author='mpa',
    author_email='',
    description='Nubomedia',
)
